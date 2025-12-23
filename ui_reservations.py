"""
Экран управления резервами материалов.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from config import COLORS, FONTS, SIZES
from utils import ScrollableFrame
from models import get_all_materials
from models_extended import (
    get_all_production_orders,
    add_reservation,
    get_all_reservations,
    release_reservation,
    get_available_balance
)


class ReservationsScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg_main'])
        self.app = app
        self.materials = []
        self.orders = []
        self.selected_reservation = None
        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        scroll = ScrollableFrame(self)
        scroll.pack(fill=tk.BOTH, expand=True)
        content = scroll.scrollable_frame

        tk.Label(content, text="Резервирование материалов", font=FONTS['heading'],
                 bg=COLORS['bg_frame'], fg=COLORS['text_primary'], pady=20).pack()
        tk.Button(content, text="← Назад в меню", font=FONTS['body'],
                  command=lambda: self.app.show_frame('MainMenu'),
                  bg=COLORS['bg_button_secondary'], fg=COLORS['text_primary'],
                  relief=tk.FLAT, padx=15, pady=5).pack(pady=10)

        form = tk.Frame(content, bg=COLORS['bg_frame'], padx=SIZES['padding'], pady=SIZES['padding'])
        form.pack(fill=tk.X, padx=SIZES['padding'], pady=SIZES['padding'])

        tk.Label(form, text="Заказ:", font=FONTS['body'], bg=COLORS['bg_frame'],
                 fg=COLORS['text_primary'], width=15, anchor=tk.W).grid(row=0, column=0, padx=5, pady=5)
        self.order_combo = ttk.Combobox(form, state="readonly", font=FONTS['body'])
        self.order_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(form, text="Материал:", font=FONTS['body'], bg=COLORS['bg_frame'],
                 fg=COLORS['text_primary'], width=15, anchor=tk.W).grid(row=1, column=0, padx=5, pady=5)
        self.material_combo = ttk.Combobox(form, state="readonly", font=FONTS['body'])
        self.material_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.material_combo.bind("<<ComboboxSelected>>", self.update_available)

        tk.Label(form, text="Количество:", font=FONTS['body'], bg=COLORS['bg_frame'],
                 fg=COLORS['text_primary'], width=15, anchor=tk.W).grid(row=2, column=0, padx=5, pady=5)
        self.qty_entry = tk.Entry(form, font=FONTS['body'], bg=COLORS['bg_entry'],
                                  fg=COLORS['text_primary'], relief=tk.FLAT)
        self.qty_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.available_label = tk.Label(form, text="Доступно: -", font=FONTS['body'],
                                        bg=COLORS['bg_frame'], fg=COLORS['accent_blue'])
        self.available_label.grid(row=3, column=0, columnspan=2, pady=5)

        form.grid_columnconfigure(1, weight=1)

        btns = tk.Frame(form, bg=COLORS['bg_frame'])
        btns.grid(row=4, column=0, columnspan=2, pady=10)
        tk.Button(btns, text="Создать резерв", font=FONTS['button'], bg=COLORS['bg_button_success'],
                  fg=COLORS['text_primary'], relief=tk.FLAT, padx=15, pady=8,
                  command=self.create_reservation).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Снять резерв", font=FONTS['button'], bg=COLORS['bg_button_danger'],
                  fg=COLORS['text_primary'], relief=tk.FLAT, padx=15, pady=8,
                  command=self.release_reservation).pack(side=tk.LEFT, padx=5)

        list_frame = tk.Frame(content, bg=COLORS['bg_frame'], padx=SIZES['padding'], pady=SIZES['padding'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding'], pady=SIZES['padding'])
        cols = ("id", "order", "material", "qty", "status", "created")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=12)
        headings = [("id", "ID", 50), ("order", "Заказ", 140), ("material", "Материал", 200),
                    ("qty", "Кол-во", 100), ("status", "Статус", 120), ("created", "Создано", 150)]
        for col, text, width in headings:
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
            self.selected_reservation = None
            return
        values = self.tree.item(sel[0])['values']
        self.selected_reservation = values[0]

    def update_available(self, event=None):
        selection = self.material_combo.get()
        if not selection:
            self.available_label.config(text="Доступно: -")
            return
        try:
            material_id = int(selection.split(" - ")[0])
            available = get_available_balance(material_id)
            self.available_label.config(text=f"Доступно: {available}")
        except Exception:
            self.available_label.config(text="Доступно: -")

    def create_reservation(self):
        order_sel = self.order_combo.get()
        mat_sel = self.material_combo.get()
        if not order_sel or not mat_sel:
            messagebox.showerror("Ошибка", "Выберите заказ и материал")
            return
        try:
            order_id = int(order_sel.split(" - ")[0])
            material_id = int(mat_sel.split(" - ")[0])
            qty = float(self.qty_entry.get().strip())
        except Exception:
            messagebox.showerror("Ошибка", "Проверьте введенные данные")
            return
        available = get_available_balance(material_id)
        if qty > available:
            messagebox.showerror("Ошибка", f"Недостаточно. Доступно {available}")
            return
        user_id = self.app.current_user['id'] if self.app.current_user else None
        res_id = add_reservation(order_id, material_id, qty, user_id)
        if res_id:
            messagebox.showinfo("Успех", "Резерв создан")
            self.refresh()
        else:
            messagebox.showerror("Ошибка", "Не удалось создать резерв")

    def release_reservation(self):
        if not self.selected_reservation:
            messagebox.showerror("Ошибка", "Выберите резерв")
            return
        user_id = self.app.current_user['id'] if self.app.current_user else None
        if release_reservation(self.selected_reservation, 'RELEASED', user_id):
            messagebox.showinfo("Успех", "Резерв обновлен")
            self.refresh()
        else:
            messagebox.showerror("Ошибка", "Не удалось обновить резерв")

    def refresh(self):
        # load combos
        self.orders = get_all_production_orders()
        self.order_combo['values'] = [f"{o['id']} - {o.get('number')}" for o in self.orders]
        self.materials = get_all_materials()
        self.material_combo['values'] = [f"{m['id']} - {m['name']}" for m in self.materials]

        for item in self.tree.get_children():
            self.tree.delete(item)
        reservations = get_all_reservations()
        for r in reservations:
            self.tree.insert("", tk.END, values=(
                r['id'],
                r.get('order_number'),
                r.get('material_name'),
                r.get('reserved_qty'),
                r.get('status'),
                r.get('created_at')
            ))

