"""
Экран регистрации списания материалов.
Позволяет списать материал со склада по методу FIFO или LIFO.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from config import COLORS, FONTS, SIZES
from utils import ScrollableFrame
from models import get_all_materials, register_issue, get_material_balance
from models_extended import get_available_balance
from fifo_lifo import can_issue


class IssueScreen(tk.Frame):
    """
    Экран для регистрации списания материалов.
    """
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg_main'])
        self.app = app
        self.materials = []
        self.selected_method = tk.StringVar(value="FIFO")
        
        self.create_widgets()
        self.load_materials()
    
    def create_widgets(self):
        """Создает виджеты экрана."""
        # Прокручиваемый контейнер
        scroll_frame = ScrollableFrame(self)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        content = scroll_frame.scrollable_frame
        
        # Заголовок
        title_label = tk.Label(
            content,
            text="Регистрация списания материалов",
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
        
        # Метка с остатком
        self.balance_label = tk.Label(
            form_frame,
            text="Текущий остаток: -",
            font=FONTS['body'],
            bg=COLORS['bg_frame'],
            fg=COLORS['accent_blue'],
            pady=10
        )
        self.balance_label.pack()
        self.available_label = tk.Label(
            form_frame,
            text="Доступно (с учетом резервов): -",
            font=FONTS['body'],
            bg=COLORS['bg_frame'],
            fg=COLORS['accent_blue'],
            pady=5
        )
        self.available_label.pack()
        
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
        
        # Метод списания в рамке
        method_frame = tk.LabelFrame(
            form_frame,
            text="Метод списания",
            font=FONTS['body'],
            bg=COLORS['bg_frame'],
            fg=COLORS['text_primary'],
            padx=20,
            pady=15,
            relief=tk.FLAT,
            borderwidth=1
        )
        method_frame.pack(fill=tk.X, pady=20)
        
        # Радиокнопки для выбора метода
        rb_fifo = tk.Radiobutton(
            method_frame,
            text="FIFO (First In, First Out) - старые партии списываются первыми",
            variable=self.selected_method,
            value="FIFO",
            font=FONTS['body'],
            bg=COLORS['bg_frame'],
            fg=COLORS['text_primary'],
            activebackground=COLORS['bg_frame'],
            activeforeground=COLORS['text_primary'],
            selectcolor=COLORS['bg_entry']
        )
        rb_fifo.pack(anchor=tk.W, pady=8)
        
        rb_lifo = tk.Radiobutton(
            method_frame,
            text="LIFO (Last In, First Out) - новые партии списываются первыми",
            variable=self.selected_method,
            value="LIFO",
            font=FONTS['body'],
            bg=COLORS['bg_frame'],
            fg=COLORS['text_primary'],
            activebackground=COLORS['bg_frame'],
            activeforeground=COLORS['text_primary'],
            selectcolor=COLORS['bg_entry']
        )
        rb_lifo.pack(anchor=tk.W, pady=8)
        
        # Кнопки
        button_frame = tk.Frame(form_frame, bg=COLORS['bg_frame'])
        button_frame.pack(pady=30)
        
        btn_issue = tk.Button(
            button_frame,
            text="Списать",
            font=FONTS['button'],
            command=self.issue_material,
            bg=COLORS['accent_orange'],
            fg=COLORS['text_primary'],
            activebackground='#e67e22',
            activeforeground=COLORS['text_primary'],
            cursor="hand2",
            relief=tk.FLAT,
            width=20,
            padx=20,
            pady=10
        )
        btn_issue.pack(side=tk.LEFT, padx=10)
        
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
    
    def on_material_selected(self, event=None):
        """Обновляет информацию об остатке при выборе материала."""
        selection = self.material_combo.get()
        if not selection:
            return
        
        try:
            material_id = int(selection.split(" - ")[0])
            balance = get_material_balance(material_id)
            self.balance_label.config(text=f"Текущий остаток: {balance}")
            available = get_available_balance(material_id)
            self.available_label.config(text=f"Доступно (резервы учтены): {available}")
        except (ValueError, IndexError):
            self.balance_label.config(text="Текущий остаток: -")
            self.available_label.config(text="Доступно (резервы учтены): -")
    
    def clear_form(self):
        """Очищает форму."""
        self.quantity_entry.delete(0, tk.END)
        self.material_combo.set("")
        self.balance_label.config(text="Текущий остаток: -")
        self.available_label.config(text="Доступно (резервы учтены): -")
    
    def issue_material(self):
        """Выполняет списание материала."""
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
        
        method = self.selected_method.get()
        available = get_available_balance(material_id)
        if quantity > available:
            messagebox.showerror(
                "Ошибка",
                f"Недостаточно материала на складе!\n"
                f"Доступно (учтены резервы): {available}\n"
                f"Требуется: {quantity}"
            )
            return
        
        # Подтверждение
        if not messagebox.askyesno(
            "Подтверждение",
            f"Списать {quantity} по методу {method}?\n"
            f"Доступно: {available}"
        ):
            return
        
        # Регистрируем списание
        user_id = self.app.current_user['id'] if self.app.current_user else None
        success = register_issue(material_id, quantity, method, None, user_id)
        
        if success:
            messagebox.showinfo(
                "Успех",
                f"Списание успешно зарегистрировано!\n"
                f"Количество: {quantity}\n"
                f"Метод: {method}"
            )
            self.clear_form()
            self.on_material_selected()  # Обновляем остаток
        else:
            messagebox.showerror("Ошибка", "Не удалось зарегистрировать списание!")
    
    def refresh(self):
        """Обновляет данные экрана при показе."""
        self.load_materials()
