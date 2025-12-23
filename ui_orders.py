"""
Экран управления производственными заказами.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from config import COLORS, FONTS, SIZES
from utils import ScrollableFrame
from models_extended import get_all_production_orders, add_production_order, update_production_order_status, delete_production_order


class OrdersScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg_main'])
        self.app = app
        self.selected_id = None
        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        scroll = ScrollableFrame(self)
        scroll.pack(fill=tk.BOTH, expand=True)
        content = scroll.scrollable_frame

        tk.Label(content, text="Производственные заказы", font=FONTS['heading'],
                 bg=COLORS['bg_frame'], fg=COLORS['text_primary'], pady=20).pack()
        tk.Button(content, text="← Назад в меню", font=FONTS['body'],
                  command=lambda: self.app.show_frame('MainMenu'),
                  bg=COLORS['bg_button_secondary'], fg=COLORS['text_primary'],
                  relief=tk.FLAT, padx=15, pady=5).pack(pady=10)

        form = tk.Frame(content, bg=COLORS['bg_frame'], padx=SIZES['padding'], pady=SIZES['padding'])
        form.pack(fill=tk.X, padx=SIZES['padding'], pady=SIZES['padding'])

        tk.Label(form, text="Номер заказа:", font=FONTS['body'], bg=COLORS['bg_frame'],
                 fg=COLORS['text_primary']).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.num_entry = tk.Entry(form, font=FONTS['body'], bg=COLORS['bg_entry'],
                                  fg=COLORS['text_primary'], relief=tk.FLAT)
        self.num_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(form, text="Дата (YYYY-MM-DD):", font=FONTS['body'], bg=COLORS['bg_frame'],
                 fg=COLORS['text_primary']).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = tk.Entry(form, font=FONTS['body'], bg=COLORS['bg_entry'],
                                   fg=COLORS['text_primary'], relief=tk.FLAT)
        self.date_entry.insert(0, datetime.now().date().isoformat())
        self.date_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(form, text="Статус:", font=FONTS['body'], bg=COLORS['bg_frame'],
                 fg=COLORS['text_primary']).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.status_combo = ttk.Combobox(form, state="readonly", font=FONTS['body'],
                                         values=['NEW', 'IN_PROGRESS', 'DONE', 'CANCELLED'])
        self.status_combo.set('NEW')
        self.status_combo.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(form, text="Описание:", font=FONTS['body'], bg=COLORS['bg_frame'],
                 fg=COLORS['text_primary']).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.desc_entry = tk.Entry(form, font=FONTS['body'], bg=COLORS['bg_entry'],
                                   fg=COLORS['text_primary'], relief=tk.FLAT)
        self.desc_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        form.grid_columnconfigure(1, weight=1)

        btns = tk.Frame(form, bg=COLORS['bg_frame'])
        btns.grid(row=4, column=0, columnspan=2, pady=10)
        tk.Button(btns, text="Создать", font=FONTS['button'], bg=COLORS['bg_button_success'],
                  fg=COLORS['text_primary'], relief=tk.FLAT, padx=15, pady=8,
                  command=self.create_order).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Изменить статус", font=FONTS['button'], bg=COLORS['accent_blue'],
                  fg=COLORS['text_primary'], relief=tk.FLAT, padx=15, pady=8,
                  command=self.change_status).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Удалить", font=FONTS['button'], bg=COLORS['bg_button_danger'],
                  fg=COLORS['text_primary'], relief=tk.FLAT, padx=15, pady=8,
                  command=self.remove_order).pack(side=tk.LEFT, padx=5)

        list_frame = tk.Frame(content, bg=COLORS['bg_frame'], padx=SIZES['padding'], pady=SIZES['padding'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding'], pady=SIZES['padding'])
        cols = ("id", "number", "date", "status", "description")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=12)
        for col, text, width in [("id", "ID", 60), ("number", "Номер", 140), ("date", "Дата", 120),
                                 ("status", "Статус", 120), ("description", "Описание", 260)]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=tk.W)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def on_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0])['values']
        self.selected_id = values[0]
        self.num_entry.delete(0, tk.END)
        self.num_entry.insert(0, values[1])
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, values[2])
        self.status_combo.set(values[3])
        self.desc_entry.delete(0, tk.END)
        self.desc_entry.insert(0, values[4] or "")

    def create_order(self):
        number = self.num_entry.get().strip()
        if not number:
            messagebox.showerror("Ошибка", "Введите номер")
            return
        try:
            order_date = datetime.fromisoformat(self.date_entry.get().strip()).date()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректная дата")
            return
        status = self.status_combo.get()
        desc = self.desc_entry.get().strip() or None
        user_id = self.app.current_user['id'] if self.app.current_user else None
        order_id = add_production_order(number, order_date, status, desc, user_id)
        if order_id:
            messagebox.showinfo("Успех", "Заказ создан")
            self.refresh()
        else:
            messagebox.showerror("Ошибка", "Не удалось создать заказ")

    def change_status(self):
        if not self.selected_id:
            messagebox.showerror("Ошибка", "Выберите заказ")
            return
        status = self.status_combo.get()
        user_id = self.app.current_user['id'] if self.app.current_user else None
        if update_production_order_status(self.selected_id, status, user_id):
            messagebox.showinfo("Успех", "Статус обновлен")
            self.refresh()
        else:
            messagebox.showerror("Ошибка", "Не удалось обновить статус")

    def remove_order(self):
        if not self.selected_id:
            messagebox.showerror("Ошибка", "Выберите заказ")
            return
        if not messagebox.askyesno("Подтверждение", "Удалить заказ?"):
            return
        user_id = self.app.current_user['id'] if self.app.current_user else None
        if delete_production_order(self.selected_id, user_id):
            messagebox.showinfo("Успех", "Удалено")
            self.refresh()
        else:
            messagebox.showerror("Ошибка", "Не удалось удалить")

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        orders = get_all_production_orders()
        for o in orders:
            self.tree.insert("", tk.END, values=(o['id'], o.get('number'), o.get('order_date'), o.get('status'), o.get('description')))

