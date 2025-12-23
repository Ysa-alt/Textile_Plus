"""
Экран перемещения между адресами хранения.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from config import COLORS, FONTS, SIZES
from utils import ScrollableFrame
from models_extended import get_all_batches_with_material, get_all_locations, transfer_batch


class TransferScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg_main'])
        self.app = app
        self.batches = []
        self.locations = []
        self.selected_batch = None
        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        scroll = ScrollableFrame(self)
        scroll.pack(fill=tk.BOTH, expand=True)
        content = scroll.scrollable_frame

        tk.Label(content, text="Перемещение между локациями", font=FONTS['heading'],
                 bg=COLORS['bg_frame'], fg=COLORS['text_primary'], pady=20).pack()
        tk.Button(content, text="← Назад в меню", font=FONTS['body'],
                  command=lambda: self.app.show_frame('MainMenu'),
                  bg=COLORS['bg_button_secondary'], fg=COLORS['text_primary'],
                  relief=tk.FLAT, padx=15, pady=5).pack(pady=10)

        form = tk.Frame(content, bg=COLORS['bg_frame'], padx=SIZES['padding'], pady=SIZES['padding'])
        form.pack(fill=tk.X, padx=SIZES['padding'], pady=SIZES['padding'])

        tk.Label(form, text="Целевая локация:", font=FONTS['body'], bg=COLORS['bg_frame'],
                 fg=COLORS['text_primary'], width=18, anchor=tk.W).grid(row=0, column=0, padx=5, pady=5)
        self.location_combo = ttk.Combobox(form, state="readonly", font=FONTS['body'])
        self.location_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(form, text="Количество:", font=FONTS['body'], bg=COLORS['bg_frame'],
                 fg=COLORS['text_primary'], width=18, anchor=tk.W).grid(row=1, column=0, padx=5, pady=5)
        self.qty_entry = tk.Entry(form, font=FONTS['body'], bg=COLORS['bg_entry'],
                                  fg=COLORS['text_primary'], relief=tk.FLAT)
        self.qty_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        form.grid_columnconfigure(1, weight=1)

        tk.Button(form, text="Переместить", font=FONTS['button'], bg=COLORS['accent_blue'],
                  fg=COLORS['text_primary'], relief=tk.FLAT, padx=15, pady=8,
                  command=self.do_transfer).grid(row=2, column=0, columnspan=2, pady=10)

        table_frame = tk.Frame(content, bg=COLORS['bg_frame'], padx=SIZES['padding'], pady=SIZES['padding'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding'], pady=SIZES['padding'])
        cols = ("id", "material", "qty", "location", "quality")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=14)
        headings = [("id", "ID", 50), ("material", "Материал", 220), ("qty", "Кол-во", 100),
                    ("location", "Адрес", 140), ("quality", "Качество", 100)]
        for col, text, width in headings:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=tk.W)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        scrollb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollb.pack(side=tk.RIGHT, fill=tk.Y)

    def on_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            self.selected_batch = None
            return
        self.selected_batch = self.tree.item(sel[0])['values'][0]

    def do_transfer(self):
        if not self.selected_batch:
            messagebox.showerror("Ошибка", "Выберите партию")
            return
        if not self.location_combo.get():
            messagebox.showerror("Ошибка", "Выберите целевую локацию")
            return
        try:
            target_location = int(self.location_combo.get().split(" - ")[0])
            qty = float(self.qty_entry.get().strip() or 0)
        except Exception:
            messagebox.showerror("Ошибка", "Проверьте количество/локацию")
            return
        user_id = self.app.current_user['id'] if self.app.current_user else None
        if transfer_batch(self.selected_batch, target_location, qty, user_id):
            messagebox.showinfo("Успех", "Перемещение выполнено")
            self.refresh()
        else:
            messagebox.showerror("Ошибка", "Не удалось переместить")

    def refresh(self):
        self.locations = get_all_locations()
        self.location_combo['values'] = [f"{l['id']} - {l['code']}" for l in self.locations]
        self.batches = get_all_batches_with_material()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for b in self.batches:
            self.tree.insert("", tk.END, values=(
                b['id'],
                b.get('material_name'),
                b.get('quantity'),
                b.get('location_code'),
                b.get('quality_status')
            ))

