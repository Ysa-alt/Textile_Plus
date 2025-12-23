"""
Экран регистрации прихода материалов.
Позволяет зарегистрировать поступление новой партии материала на склад.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from config import COLORS, FONTS, SIZES
from utils import ScrollableFrame
from models import get_all_materials, register_receipt, get_material_balance
from models_extended import get_all_locations, get_all_suppliers, get_contracts_by_supplier


class ReceiptScreen(tk.Frame):
    """
    Экран для регистрации прихода материалов.
    """
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg_main'])
        self.app = app
        self.materials = []
        self.locations = []
        self.suppliers = []
        self.contracts = []
        
        self.create_widgets()
        self.load_materials()
        self.load_locations()
        self.load_suppliers()
    
    def create_widgets(self):
        """Создает виджеты экрана."""
        # Прокручиваемый контейнер
        scroll_frame = ScrollableFrame(self)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        content = scroll_frame.scrollable_frame
        
        # Заголовок
        title_label = tk.Label(
            content,
            text="Регистрация прихода материалов",
            font=FONTS['heading'],
            bg=COLORS['bg_frame'],
            fg=COLORS['text_primary'],
            pady=20
        )
        title_label.pack()
        
        # Кнопка "Назад"
        btn_back = tk.Button(
            content,
            text="← Назад в меню",
            font=FONTS['body'],
            command=lambda: self.app.show_frame('MainMenu'),
            bg=COLORS['bg_button_secondary'],
            fg=COLORS['text_primary'],
            activebackground=COLORS['bg_button_hover'],
            activeforeground=COLORS['text_primary'],
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        btn_back.pack(pady=10)
        
        # Фрейм для формы
        form_frame = tk.Frame(
            content,
            bg=COLORS['bg_frame'],
            padx=SIZES['padding'] * 2,
            pady=SIZES['padding'] * 2
        )
        form_frame.pack(fill=tk.X, padx=SIZES['padding'], pady=SIZES['padding'])
        
        # Поле "Материал"
        material_frame = tk.Frame(form_frame, bg=COLORS['bg_frame'])
        material_frame.pack(fill=tk.X, pady=15)
        
        tk.Label(
            material_frame,
            text="Материал:",
            font=FONTS['body'],
            bg=COLORS['bg_frame'],
            fg=COLORS['text_primary'],
            width=20,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=10)
        
        self.material_combo = ttk.Combobox(
            material_frame,
            font=FONTS['body'],
            width=SIZES['entry_width'],
            state="readonly"
        )
        self.material_combo.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.material_combo.bind("<<ComboboxSelected>>", self.on_material_selected)
        
        # Поле "Локация"
        location_frame = tk.Frame(form_frame, bg=COLORS['bg_frame'])
        location_frame.pack(fill=tk.X, pady=15)

        tk.Label(
            location_frame,
            text="Адрес хранения:",
            font=FONTS['body'],
            bg=COLORS['bg_frame'],
            fg=COLORS['text_primary'],
            width=20,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=10)

        self.location_combo = ttk.Combobox(
            location_frame,
            font=FONTS['body'],
            width=SIZES['entry_width'],
            state="readonly"
        )
        self.location_combo.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Поле "Поставщик"
        supplier_frame = tk.Frame(form_frame, bg=COLORS['bg_frame'])
        supplier_frame.pack(fill=tk.X, pady=15)

        tk.Label(
            supplier_frame,
            text="Поставщик:",
            font=FONTS['body'],
            bg=COLORS['bg_frame'],
            fg=COLORS['text_primary'],
            width=20,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=10)

        self.supplier_combo = ttk.Combobox(
            supplier_frame,
            font=FONTS['body'],
            width=SIZES['entry_width'],
            state="readonly"
        )
        self.supplier_combo.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.supplier_combo.bind("<<ComboboxSelected>>", self.on_supplier_selected)

        # Поле "Договор"
        contract_frame = tk.Frame(form_frame, bg=COLORS['bg_frame'])
        contract_frame.pack(fill=tk.X, pady=15)

        tk.Label(
            contract_frame,
            text="Договор:",
            font=FONTS['body'],
            bg=COLORS['bg_frame'],
            fg=COLORS['text_primary'],
            width=20,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=10)

        self.contract_combo = ttk.Combobox(
            contract_frame,
            font=FONTS['body'],
            width=SIZES['entry_width'],
            state="readonly"
        )
        self.contract_combo.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Метка с текущим остатком
        self.balance_label = tk.Label(
            form_frame,
            text="Текущий остаток: -",
            font=FONTS['body'],
            bg=COLORS['bg_frame'],
            fg=COLORS['accent_blue'],
            pady=10
        )
        self.balance_label.pack()
        
        # Поле "Количество"
        quantity_frame = tk.Frame(form_frame, bg=COLORS['bg_frame'])
        quantity_frame.pack(fill=tk.X, pady=15)
        
        tk.Label(
            quantity_frame,
            text="Количество:",
            font=FONTS['body'],
            bg=COLORS['bg_frame'],
            fg=COLORS['text_primary'],
            width=20,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=10)
        
        self.quantity_entry = tk.Entry(
            quantity_frame,
            font=FONTS['body'],
            width=SIZES['entry_width'],
            bg=COLORS['bg_entry'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            relief=tk.FLAT
        )
        self.quantity_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Поле "Цена за единицу"
        price_frame = tk.Frame(form_frame, bg=COLORS['bg_frame'])
        price_frame.pack(fill=tk.X, pady=15)
        
        tk.Label(
            price_frame,
            text="Цена за единицу:",
            font=FONTS['body'],
            bg=COLORS['bg_frame'],
            fg=COLORS['text_primary'],
            width=20,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=10)
        
        self.price_entry = tk.Entry(
            price_frame,
            font=FONTS['body'],
            width=SIZES['entry_width'],
            bg=COLORS['bg_entry'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            relief=tk.FLAT
        )
        self.price_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Поле "Серийный номер"
        serial_frame = tk.Frame(form_frame, bg=COLORS['bg_frame'])
        serial_frame.pack(fill=tk.X, pady=15)

        tk.Label(
            serial_frame,
            text="Серийный номер:",
            font=FONTS['body'],
            bg=COLORS['bg_frame'],
            fg=COLORS['text_primary'],
            width=20,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=10)

        self.serial_entry = tk.Entry(
            serial_frame,
            font=FONTS['body'],
            width=SIZES['entry_width'],
            bg=COLORS['bg_entry'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            relief=tk.FLAT
        )
        self.serial_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Кнопки
        button_frame = tk.Frame(form_frame, bg=COLORS['bg_frame'])
        button_frame.pack(pady=30)
        
        btn_save = tk.Button(
            button_frame,
            text="Сохранить",
            font=FONTS['button'],
            command=self.save_receipt,
            bg=COLORS['bg_button_success'],
            fg=COLORS['text_primary'],
            activebackground='#229954',
            activeforeground=COLORS['text_primary'],
            cursor="hand2",
            relief=tk.FLAT,
            width=20,
            padx=20,
            pady=10
        )
        btn_save.pack(side=tk.LEFT, padx=10)
        
        btn_clear = tk.Button(
            button_frame,
            text="Очистить",
            font=FONTS['button'],
            command=self.clear_form,
            bg=COLORS['bg_button_secondary'],
            fg=COLORS['text_primary'],
            activebackground=COLORS['bg_button_hover'],
            activeforeground=COLORS['text_primary'],
            cursor="hand2",
            relief=tk.FLAT,
            width=20,
            padx=20,
            pady=10
        )
        btn_clear.pack(side=tk.LEFT, padx=10)
    
    def load_materials(self):
        """Загружает список материалов в Combobox."""
        self.materials = get_all_materials()
        if not self.materials:
            messagebox.showwarning(
                "Предупреждение",
                "Нет материалов в базе данных. Сначала добавьте материалы!"
            )
            return
        
        material_list = [
            f"{m['id']} - {m['name']} ({m['unit']})"
            for m in self.materials
        ]
        self.material_combo['values'] = material_list

    def load_locations(self):
        """Загружает адреса хранения."""
        self.locations = get_all_locations()
        location_list = [f"{l['id']} - {l['code']}" for l in self.locations]
        self.location_combo['values'] = location_list

    def load_suppliers(self):
        """Загружает поставщиков."""
        self.suppliers = get_all_suppliers()
        supplier_list = [f"{s['id']} - {s['name']}" for s in self.suppliers]
        self.supplier_combo['values'] = supplier_list

    def on_supplier_selected(self, event=None):
        """Подгружает договоры выбранного поставщика."""
        selection = self.supplier_combo.get()
        if not selection:
            return
        try:
            supplier_id = int(selection.split(" - ")[0])
        except (ValueError, IndexError):
            return
        self.contracts = get_contracts_by_supplier(supplier_id)
        contract_list = [f"{c['id']} - {c['number']}" for c in self.contracts]
        self.contract_combo['values'] = contract_list
    
    def on_material_selected(self, event=None):
        """Обновляет информацию об остатке при выборе материала."""
        selection = self.material_combo.get()
        if not selection:
            return
        
        try:
            material_id = int(selection.split(" - ")[0])
            balance = get_material_balance(material_id)
            self.balance_label.config(text=f"Текущий остаток: {balance}")
        except (ValueError, IndexError):
            self.balance_label.config(text="Текущий остаток: -")
    
    def clear_form(self):
        """Очищает форму."""
        self.quantity_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.material_combo.set("")
        self.location_combo.set("")
        self.supplier_combo.set("")
        self.contract_combo.set("")
        self.serial_entry.delete(0, tk.END)
        self.balance_label.config(text="Текущий остаток: -")
    
    def save_receipt(self):
        """Сохраняет приход материала."""
        selection = self.material_combo.get()
        if not selection:
            messagebox.showerror("Ошибка", "Выберите материал!")
            return
        
        try:
            material_id = int(selection.split(" - ")[0])
        except (ValueError, IndexError):
            messagebox.showerror("Ошибка", "Ошибка при выборе материала!")
            return
        
        try:
            quantity = float(self.quantity_entry.get().strip())
            if quantity <= 0:
                raise ValueError("Количество должно быть больше нуля")
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректное количество: {e}")
            return
        
        try:
            price = float(self.price_entry.get().strip())
            if price < 0:
                raise ValueError("Цена не может быть отрицательной")
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректная цена: {e}")
            return

        location_id = None
        if self.location_combo.get():
            try:
                location_id = int(self.location_combo.get().split(" - ")[0])
            except (ValueError, IndexError):
                messagebox.showerror("Ошибка", "Некорректно выбран адрес хранения")
                return

        supplier_id = None
        if self.supplier_combo.get():
            try:
                supplier_id = int(self.supplier_combo.get().split(" - ")[0])
            except (ValueError, IndexError):
                messagebox.showerror("Ошибка", "Некорректно выбран поставщик")
                return

        contract_id = None
        if self.contract_combo.get():
            try:
                contract_id = int(self.contract_combo.get().split(" - ")[0])
            except (ValueError, IndexError):
                messagebox.showerror("Ошибка", "Некорректно выбран договор")
                return

        serial_number = self.serial_entry.get().strip() or None

        user_id = self.app.current_user['id'] if self.app.current_user else None
        batch_id = register_receipt(material_id, quantity, price, location_id, supplier_id, contract_id, serial_number, user_id)
        
        if batch_id:
            messagebox.showinfo(
                "Успех",
                f"Приход успешно зарегистрирован!\nПартия ID: {batch_id}\nКоличество: {quantity}"
            )
            self.clear_form()
            self.on_material_selected()  # Обновляем остаток
        else:
            messagebox.showerror("Ошибка", "Не удалось зарегистрировать приход!")
    
    def refresh(self):
        """Обновляет данные экрана при показе."""
        self.load_materials()
        self.load_locations()
        self.load_suppliers()
