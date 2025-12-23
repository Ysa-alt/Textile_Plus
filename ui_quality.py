"""
Экран управления качеством партий.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from config import COLORS, FONTS, SIZES
from utils import ScrollableFrame
from models_extended import get_all_batches_with_material, update_batch_quality


class QualityScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg_main'])
        self.app = app
        self.selected_batch = None
        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        scroll = ScrollableFrame(self)
        scroll.pack(fill=tk.BOTH, expand=True)
        content = scroll.scrollable_frame

        tk.Label(content, text="Качество партий", font=FONTS['heading'], bg=COLORS['bg_frame'],
                 fg=COLORS['text_primary'], pady=20).pack()
        tk.Button(content, text="← Назад в меню", font=FONTS['body'],
                  command=lambda: self.app.show_frame('MainMenu'),
                  bg=COLORS['bg_button_secondary'], fg=COLORS['text_primary'],
                  relief=tk.FLAT, padx=15, pady=5).pack(pady=10)

        btn_frame = tk.Frame(content, bg=COLORS['bg_frame'])
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Установить OK", font=FONTS['button'], bg=COLORS['bg_button_success'],
                  fg=COLORS['text_primary'], relief=tk.FLAT, padx=15, pady=8,
                  command=lambda: self.change_quality('OK')).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Блокировать", font=FONTS['button'], bg=COLORS['bg_button_danger'],
                  fg=COLORS['text_primary'], relief=tk.FLAT, padx=15, pady=8,
                  command=lambda: self.change_quality('BLOCKED')).pack(side=tk.LEFT, padx=5)

        table_frame = tk.Frame(content, bg=COLORS['bg_frame'], padx=SIZES['padding'], pady=SIZES['padding'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding'], pady=SIZES['padding'])

        cols = ("id", "material", "qty", "received", "location", "quality", "serial")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)
        headings = [
            ("id", "ID", 50),
            ("material", "Материал", 200),
            ("qty", "Кол-во", 100),
            ("received", "Дата", 150),
            ("location", "Адрес", 120),
            ("quality", "Статус", 100),
            ("serial", "Серийный", 140)
        ]
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

    def change_quality(self, status: str):
        if not self.selected_batch:
            messagebox.showerror("Ошибка", "Выберите партию")
            return
        user_id = self.app.current_user['id'] if self.app.current_user else None
        if update_batch_quality(self.selected_batch, status, user_id):
            messagebox.showinfo("Успех", "Статус обновлен")
            self.refresh()
        else:
            messagebox.showerror("Ошибка", "Не удалось обновить статус")

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        batches = get_all_batches_with_material()
        for b in batches:
            self.tree.insert("", tk.END, values=(
                b['id'],
                b.get('material_name'),
                b.get('quantity'),
                b.get('received_at'),
                b.get('location_code'),
                b.get('quality_status'),
                b.get('serial_number')
            ))

