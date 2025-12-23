"""
Экран управления адресами хранения.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from config import COLORS, FONTS, SIZES
from utils import ScrollableFrame
from models_extended import get_all_locations, add_location, update_location, delete_location


class LocationsScreen(tk.Frame):
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

        title = tk.Label(content, text="Адреса хранения", font=FONTS['heading'], bg=COLORS['bg_frame'],
                         fg=COLORS['text_primary'], pady=20)
        title.pack()

        btn_back = tk.Button(content, text="← Назад в меню", font=FONTS['body'],
                             command=lambda: self.app.show_frame('MainMenu'),
                             bg=COLORS['bg_button_secondary'], fg=COLORS['text_primary'],
                             activebackground=COLORS['bg_button_hover'], relief=tk.FLAT, padx=15, pady=5)
        btn_back.pack(pady=10)

        form = tk.Frame(content, bg=COLORS['bg_frame'], padx=SIZES['padding'], pady=SIZES['padding'])
        form.pack(fill=tk.X, padx=SIZES['padding'], pady=SIZES['padding'])

        tk.Label(form, text="Код:", font=FONTS['body'], bg=COLORS['bg_frame'], fg=COLORS['text_primary'],
                 width=15, anchor=tk.W).grid(row=0, column=0, padx=5, pady=5)
        self.code_entry = tk.Entry(form, font=FONTS['body'], bg=COLORS['bg_entry'], fg=COLORS['text_primary'],
                                   relief=tk.FLAT)
        self.code_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(form, text="Название:", font=FONTS['body'], bg=COLORS['bg_frame'], fg=COLORS['text_primary'],
                 width=15, anchor=tk.W).grid(row=1, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(form, font=FONTS['body'], bg=COLORS['bg_entry'], fg=COLORS['text_primary'],
                                   relief=tk.FLAT)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(form, text="Описание:", font=FONTS['body'], bg=COLORS['bg_frame'], fg=COLORS['text_primary'],
                 width=15, anchor=tk.W).grid(row=2, column=0, padx=5, pady=5)
        self.desc_entry = tk.Entry(form, font=FONTS['body'], bg=COLORS['bg_entry'], fg=COLORS['text_primary'],
                                   relief=tk.FLAT)
        self.desc_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        form.grid_columnconfigure(1, weight=1)

        btns = tk.Frame(form, bg=COLORS['bg_frame'])
        btns.grid(row=3, column=0, columnspan=2, pady=10)

        tk.Button(btns, text="Добавить", font=FONTS['button'], bg=COLORS['bg_button_success'],
                  fg=COLORS['text_primary'], relief=tk.FLAT, padx=15, pady=8,
                  command=self.create_location).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Изменить", font=FONTS['button'], bg=COLORS['accent_blue'],
                  fg=COLORS['text_primary'], relief=tk.FLAT, padx=15, pady=8,
                  command=self.edit_location).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Удалить", font=FONTS['button'], bg=COLORS['bg_button_danger'],
                  fg=COLORS['text_primary'], relief=tk.FLAT, padx=15, pady=8,
                  command=self.remove_location).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Очистить", font=FONTS['button'], bg=COLORS['bg_button_secondary'],
                  fg=COLORS['text_primary'], relief=tk.FLAT, padx=15, pady=8,
                  command=self.clear_form).pack(side=tk.LEFT, padx=5)

        list_frame = tk.Frame(content, bg=COLORS['bg_frame'], padx=SIZES['padding'], pady=SIZES['padding'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding'], pady=SIZES['padding'])

        columns = ("id", "code", "name", "description")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        for col, text, width, anchor in [
            ("id", "ID", 60, tk.CENTER),
            ("code", "Код", 120, tk.CENTER),
            ("name", "Название", 200, tk.W),
            ("description", "Описание", 300, tk.W),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=anchor)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def on_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0])['values']
        self.selected_id = values[0]
        self.code_entry.delete(0, tk.END)
        self.code_entry.insert(0, values[1])
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, values[2])
        self.desc_entry.delete(0, tk.END)
        self.desc_entry.insert(0, values[3] or "")

    def clear_form(self):
        self.selected_id = None
        self.code_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.tree.selection_remove(self.tree.selection())

    def create_location(self):
        code = self.code_entry.get().strip()
        name = self.name_entry.get().strip()
        desc = self.desc_entry.get().strip() or None
        if not code or not name:
            messagebox.showerror("Ошибка", "Заполните код и название")
            return
        user_id = self.app.current_user['id'] if self.app.current_user else None
        loc_id = add_location(code, name, desc, user_id)
        if loc_id:
            messagebox.showinfo("Успех", "Адрес добавлен")
            self.refresh()
            self.clear_form()
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить адрес")

    def edit_location(self):
        if not self.selected_id:
            messagebox.showerror("Ошибка", "Выберите адрес")
            return
        code = self.code_entry.get().strip()
        name = self.name_entry.get().strip()
        desc = self.desc_entry.get().strip() or None
        user_id = self.app.current_user['id'] if self.app.current_user else None
        if update_location(self.selected_id, code, name, desc, user_id):
            messagebox.showinfo("Успех", "Адрес обновлен")
            self.refresh()
        else:
            messagebox.showerror("Ошибка", "Не удалось обновить адрес")

    def remove_location(self):
        if not self.selected_id:
            messagebox.showerror("Ошибка", "Выберите адрес")
            return
        if not messagebox.askyesno("Подтверждение", "Удалить выбранный адрес?"):
            return
        user_id = self.app.current_user['id'] if self.app.current_user else None
        if delete_location(self.selected_id, user_id):
            messagebox.showinfo("Успех", "Удалено")
            self.refresh()
            self.clear_form()
        else:
            messagebox.showerror("Ошибка", "Не удалось удалить")

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        locations = get_all_locations()
        for loc in locations:
            self.tree.insert("", tk.END, values=(loc['id'], loc['code'], loc.get('name'), loc.get('description')))

