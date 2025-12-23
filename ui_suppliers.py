"""
Экран управления поставщиками и договорами.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from config import COLORS, FONTS, SIZES
from utils import ScrollableFrame
from models_extended import (
    get_all_suppliers, add_supplier, update_supplier, delete_supplier,
    get_contracts_by_supplier, add_contract, update_contract, delete_contract
)


class SuppliersScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg_main'])
        self.app = app
        self.selected_supplier = None
        self.selected_contract = None
        self.create_widgets()
        self.refresh_suppliers()

    def create_widgets(self):
        scroll = ScrollableFrame(self)
        scroll.pack(fill=tk.BOTH, expand=True)
        content = scroll.scrollable_frame

        title = tk.Label(content, text="Поставщики и договоры", font=FONTS['heading'], bg=COLORS['bg_frame'],
                         fg=COLORS['text_primary'], pady=20)
        title.pack()
        tk.Button(content, text="← Назад в меню", font=FONTS['body'],
                  command=lambda: self.app.show_frame('MainMenu'),
                  bg=COLORS['bg_button_secondary'], fg=COLORS['text_primary'],
                  activebackground=COLORS['bg_button_hover'], relief=tk.FLAT,
                  padx=15, pady=5).pack(pady=10)

        form = tk.Frame(content, bg=COLORS['bg_frame'], padx=SIZES['padding'], pady=SIZES['padding'])
        form.pack(fill=tk.X, padx=SIZES['padding'], pady=SIZES['padding'])
        labels = [("Название", "name_entry"), ("ИНН", "inn_entry"), ("Контакты", "contact_entry")]
        for idx, (text, attr) in enumerate(labels):
            tk.Label(form, text=f"{text}:", font=FONTS['body'], bg=COLORS['bg_frame'],
                     fg=COLORS['text_primary'], width=15, anchor=tk.W).grid(row=idx, column=0, padx=5, pady=5)
            entry = tk.Entry(form, font=FONTS['body'], bg=COLORS['bg_entry'], fg=COLORS['text_primary'],
                             relief=tk.FLAT)
            entry.grid(row=idx, column=1, padx=5, pady=5, sticky="ew")
            setattr(self, attr, entry)
        form.grid_columnconfigure(1, weight=1)

        btns = tk.Frame(form, bg=COLORS['bg_frame'])
        btns.grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(btns, text="Добавить", font=FONTS['button'], bg=COLORS['bg_button_success'],
                  fg=COLORS['text_primary'], relief=tk.FLAT, padx=15, pady=8,
                  command=self.create_supplier).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Изменить", font=FONTS['button'], bg=COLORS['accent_blue'],
                  fg=COLORS['text_primary'], relief=tk.FLAT, padx=15, pady=8,
                  command=self.edit_supplier).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Удалить", font=FONTS['button'], bg=COLORS['bg_button_danger'],
                  fg=COLORS['text_primary'], relief=tk.FLAT, padx=15, pady=8,
                  command=self.remove_supplier).pack(side=tk.LEFT, padx=5)

        # Таблица поставщиков
        sup_frame = tk.Frame(content, bg=COLORS['bg_frame'], padx=SIZES['padding'], pady=SIZES['padding'])
        sup_frame.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding'], pady=SIZES['padding'])
        sup_cols = ("id", "name", "inn", "contact")
        self.sup_tree = ttk.Treeview(sup_frame, columns=sup_cols, show="headings", height=10)
        for col, text, width in [("id", "ID", 50), ("name", "Название", 220), ("inn", "ИНН", 120), ("contact", "Контакты", 200)]:
            self.sup_tree.heading(col, text=text)
            self.sup_tree.column(col, width=width, anchor=tk.W)
        self.sup_tree.bind('<<TreeviewSelect>>', self.on_supplier_select)
        sup_scroll = ttk.Scrollbar(sup_frame, orient=tk.VERTICAL, command=self.sup_tree.yview)
        self.sup_tree.configure(yscrollcommand=sup_scroll.set)
        self.sup_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sup_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Блок договоров
        contract_frame = tk.LabelFrame(content, text="Договоры выбранного поставщика", font=FONTS['body'],
                                       bg=COLORS['bg_frame'], fg=COLORS['text_primary'],
                                       padx=SIZES['padding'], pady=SIZES['padding'])
        contract_frame.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding'], pady=SIZES['padding'])

        contract_form = tk.Frame(contract_frame, bg=COLORS['bg_frame'])
        contract_form.pack(fill=tk.X, pady=5)
        tk.Label(contract_form, text="Номер:", font=FONTS['body'], bg=COLORS['bg_frame'],
                 fg=COLORS['text_primary'], width=15, anchor=tk.W).grid(row=0, column=0, padx=5, pady=5)
        self.contract_number = tk.Entry(contract_form, font=FONTS['body'], bg=COLORS['bg_entry'],
                                        fg=COLORS['text_primary'], relief=tk.FLAT)
        self.contract_number.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(contract_form, text="Дата (YYYY-MM-DD):", font=FONTS['body'], bg=COLORS['bg_frame'],
                 fg=COLORS['text_primary'], width=20, anchor=tk.W).grid(row=1, column=0, padx=5, pady=5)
        self.contract_date = tk.Entry(contract_form, font=FONTS['body'], bg=COLORS['bg_entry'],
                                      fg=COLORS['text_primary'], relief=tk.FLAT)
        self.contract_date.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(contract_form, text="Описание:", font=FONTS['body'], bg=COLORS['bg_frame'],
                 fg=COLORS['text_primary'], width=15, anchor=tk.W).grid(row=2, column=0, padx=5, pady=5)
        self.contract_desc = tk.Entry(contract_form, font=FONTS['body'], bg=COLORS['bg_entry'],
                                      fg=COLORS['text_primary'], relief=tk.FLAT)
        self.contract_desc.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        contract_form.grid_columnconfigure(1, weight=1)

        cbtns = tk.Frame(contract_frame, bg=COLORS['bg_frame'])
        cbtns.pack(pady=5)
        tk.Button(cbtns, text="Добавить договор", font=FONTS['button'], bg=COLORS['bg_button_success'],
                  fg=COLORS['text_primary'], relief=tk.FLAT, padx=10, pady=6,
                  command=self.create_contract).pack(side=tk.LEFT, padx=5)
        tk.Button(cbtns, text="Изменить договор", font=FONTS['button'], bg=COLORS['accent_blue'],
                  fg=COLORS['text_primary'], relief=tk.FLAT, padx=10, pady=6,
                  command=self.edit_contract).pack(side=tk.LEFT, padx=5)
        tk.Button(cbtns, text="Удалить договор", font=FONTS['button'], bg=COLORS['bg_button_danger'],
                  fg=COLORS['text_primary'], relief=tk.FLAT, padx=10, pady=6,
                  command=self.remove_contract).pack(side=tk.LEFT, padx=5)

        self.contract_tree = ttk.Treeview(contract_frame, columns=("id", "number", "date", "description"),
                                          show="headings", height=8)
        for col, text, width in [("id", "ID", 50), ("number", "Номер", 150), ("date", "Дата", 120), ("description", "Описание", 250)]:
            self.contract_tree.heading(col, text=text)
            self.contract_tree.column(col, width=width, anchor=tk.W)
        self.contract_tree.bind('<<TreeviewSelect>>', self.on_contract_select)
        cscroll = ttk.Scrollbar(contract_frame, orient=tk.VERTICAL, command=self.contract_tree.yview)
        self.contract_tree.configure(yscrollcommand=cscroll.set)
        self.contract_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cscroll.pack(side=tk.RIGHT, fill=tk.Y)

    # Supplier handlers
    def on_supplier_select(self, event=None):
        sel = self.sup_tree.selection()
        if not sel:
            return
        values = self.sup_tree.item(sel[0])['values']
        self.selected_supplier = values[0]
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, values[1])
        self.inn_entry.delete(0, tk.END)
        self.inn_entry.insert(0, values[2] or "")
        self.contact_entry.delete(0, tk.END)
        self.contact_entry.insert(0, values[3] or "")
        self.refresh_contracts()

    def create_supplier(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Ошибка", "Название обязательно")
            return
        inn = self.inn_entry.get().strip() or None
        contact = self.contact_entry.get().strip() or None
        user_id = self.app.current_user['id'] if self.app.current_user else None
        sup_id = add_supplier(name, inn, contact, user_id)
        if sup_id:
            messagebox.showinfo("Успех", "Поставщик добавлен")
            self.refresh_suppliers()
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить")

    def edit_supplier(self):
        if not self.selected_supplier:
            messagebox.showerror("Ошибка", "Выберите поставщика")
            return
        name = self.name_entry.get().strip()
        inn = self.inn_entry.get().strip() or None
        contact = self.contact_entry.get().strip() or None
        user_id = self.app.current_user['id'] if self.app.current_user else None
        if update_supplier(self.selected_supplier, name, inn, contact, user_id):
            messagebox.showinfo("Успех", "Поставщик обновлен")
            self.refresh_suppliers()
        else:
            messagebox.showerror("Ошибка", "Не удалось обновить")

    def remove_supplier(self):
        if not self.selected_supplier:
            messagebox.showerror("Ошибка", "Выберите поставщика")
            return
        if not messagebox.askyesno("Подтверждение", "Удалить поставщика?"):
            return
        user_id = self.app.current_user['id'] if self.app.current_user else None
        if delete_supplier(self.selected_supplier, user_id):
            messagebox.showinfo("Успех", "Удалено")
            self.refresh_suppliers()
            self.contract_tree.delete(*self.contract_tree.get_children())
        else:
            messagebox.showerror("Ошибка", "Не удалось удалить")

    # Contract handlers
    def on_contract_select(self, event=None):
        sel = self.contract_tree.selection()
        if not sel:
            return
        values = self.contract_tree.item(sel[0])['values']
        self.selected_contract = values[0]
        self.contract_number.delete(0, tk.END)
        self.contract_number.insert(0, values[1])
        self.contract_date.delete(0, tk.END)
        self.contract_date.insert(0, values[2])
        self.contract_desc.delete(0, tk.END)
        self.contract_desc.insert(0, values[3] or "")

    def create_contract(self):
        if not self.selected_supplier:
            messagebox.showerror("Ошибка", "Выберите поставщика")
            return
        number = self.contract_number.get().strip()
        date_str = self.contract_date.get().strip() or datetime.now().date().isoformat()
        desc = self.contract_desc.get().strip() or None
        try:
            date_value = datetime.fromisoformat(date_str).date()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректная дата")
            return
        user_id = self.app.current_user['id'] if self.app.current_user else None
        cid = add_contract(self.selected_supplier, number, date_value, desc, user_id)
        if cid:
            messagebox.showinfo("Успех", "Договор добавлен")
            self.refresh_contracts()
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить договор")

    def edit_contract(self):
        if not self.selected_contract or not self.selected_supplier:
            messagebox.showerror("Ошибка", "Выберите договор")
            return
        number = self.contract_number.get().strip()
        date_str = self.contract_date.get().strip()
        desc = self.contract_desc.get().strip() or None
        try:
            date_value = datetime.fromisoformat(date_str).date()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректная дата")
            return
        user_id = self.app.current_user['id'] if self.app.current_user else None
        if update_contract(self.selected_contract, self.selected_supplier, number, date_value, desc, user_id):
            messagebox.showinfo("Успех", "Договор обновлен")
            self.refresh_contracts()
        else:
            messagebox.showerror("Ошибка", "Не удалось обновить договор")

    def remove_contract(self):
        if not self.selected_contract:
            messagebox.showerror("Ошибка", "Выберите договор")
            return
        if not messagebox.askyesno("Подтверждение", "Удалить договор?"):
            return
        user_id = self.app.current_user['id'] if self.app.current_user else None
        if delete_contract(self.selected_contract, user_id):
            messagebox.showinfo("Успех", "Удалено")
            self.refresh_contracts()
        else:
            messagebox.showerror("Ошибка", "Не удалось удалить договор")

    # Refresh helpers
    def refresh_suppliers(self):
        for item in self.sup_tree.get_children():
            self.sup_tree.delete(item)
        suppliers = get_all_suppliers()
        for sup in suppliers:
            self.sup_tree.insert("", tk.END, values=(sup['id'], sup['name'], sup.get('inn'), sup.get('contact')))

    def refresh_contracts(self):
        for item in self.contract_tree.get_children():
            self.contract_tree.delete(item)
        if not self.selected_supplier:
            return
        contracts = get_contracts_by_supplier(self.selected_supplier)
        for c in contracts:
            self.contract_tree.insert("", tk.END, values=(
                c['id'],
                c['number'],
                c.get('contract_date'),
                c.get('description')
            ))

    def refresh(self):
        self.refresh_suppliers()
        self.refresh_contracts()

