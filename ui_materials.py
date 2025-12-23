"""
Экран управления материалами.
Позволяет добавлять, изменять и удалять материалы.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from config import COLORS, FONTS, SIZES
from utils import ScrollableFrame
from models import add_material, get_all_materials, update_material, delete_material

# Категории материалов
MATERIAL_CATEGORIES = {
    'fabric': 'Ткань',
    'accessory': 'Фурнитура',
    'thread': 'Нитки',
    'other': 'Прочее'
}


class MaterialsScreen(tk.Frame):
    """
    Экран для управления материалами.
    """
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg_main'])
        self.app = app
        self.selected_material_id = None
        
        self.create_widgets()
        self.refresh_materials_list()
    
    def create_widgets(self):
        """Создает виджеты экрана."""
        # Прокручиваемый контейнер
        scroll_frame = ScrollableFrame(self)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        content = scroll_frame.scrollable_frame
        
        # Заголовок
        title_label = tk.Label(
            content,
            text="Управление материалами",
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
        
        # Фрейм для формы добавления/редактирования
        form_frame = tk.Frame(
            content,
            bg=COLORS['bg_frame'],
            padx=SIZES['padding'],
            pady=SIZES['padding']
        )
        form_frame.pack(fill=tk.X, padx=SIZES['padding'], pady=SIZES['padding'])
        
        # Заголовок формы
        form_title = tk.Label(
            form_frame,
            text="Добавление / Редактирование материала",
            font=FONTS['subheading'],
            bg=COLORS['bg_frame'],
            fg=COLORS['text_primary']
        )
        form_title.pack(pady=10)
        
        # Поле "Название"
        name_frame = tk.Frame(form_frame, bg=COLORS['bg_frame'])
        name_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            name_frame,
            text="Название материала:",
            font=FONTS['body'],
            bg=COLORS['bg_frame'],
            fg=COLORS['text_primary'],
            width=20,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=10)
        
        self.name_entry = tk.Entry(
            name_frame,
            font=FONTS['body'],
            width=SIZES['entry_width'],
            bg=COLORS['bg_entry'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            relief=tk.FLAT
        )
        self.name_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Поле "Единица измерения"
        unit_frame = tk.Frame(form_frame, bg=COLORS['bg_frame'])
        unit_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            unit_frame,
            text="Единица измерения:",
            font=FONTS['body'],
            bg=COLORS['bg_frame'],
            fg=COLORS['text_primary'],
            width=20,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=10)
        
        self.unit_entry = tk.Entry(
            unit_frame,
            font=FONTS['body'],
            width=SIZES['entry_width'],
            bg=COLORS['bg_entry'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            relief=tk.FLAT
        )
        self.unit_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.unit_entry.insert(0, "м")
        
        # Поле "Тип материала" (категория)
        category_frame = tk.Frame(form_frame, bg=COLORS['bg_frame'])
        category_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            category_frame,
            text="Тип материала:",
            font=FONTS['body'],
            bg=COLORS['bg_frame'],
            fg=COLORS['text_primary'],
            width=20,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=10)
        
        self.category_combo = ttk.Combobox(
            category_frame,
            font=FONTS['body'],
            width=SIZES['entry_width'],
            state="readonly",
            values=list(MATERIAL_CATEGORIES.values())
        )
        self.category_combo.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.category_combo.set(MATERIAL_CATEGORIES['other'])  # Значение по умолчанию

        # Поля минимального/максимального запаса
        stock_frame = tk.Frame(form_frame, bg=COLORS['bg_frame'])
        stock_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            stock_frame,
            text="Мин. запас:",
            font=FONTS['body'],
            bg=COLORS['bg_frame'],
            fg=COLORS['text_primary'],
            width=20,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=10)

        self.min_entry = tk.Entry(
            stock_frame,
            font=FONTS['body'],
            width=10,
            bg=COLORS['bg_entry'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            relief=tk.FLAT
        )
        self.min_entry.pack(side=tk.LEFT, padx=5)
        self.min_entry.insert(0, "0")

        tk.Label(
            stock_frame,
            text="Макс. запас:",
            font=FONTS['body'],
            bg=COLORS['bg_frame'],
            fg=COLORS['text_primary'],
            width=15,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=10)

        self.max_entry = tk.Entry(
            stock_frame,
            font=FONTS['body'],
            width=10,
            bg=COLORS['bg_entry'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            relief=tk.FLAT
        )
        self.max_entry.pack(side=tk.LEFT, padx=5)
        
        # Кнопки формы
        button_frame = tk.Frame(form_frame, bg=COLORS['bg_frame'])
        button_frame.pack(pady=20)
        
        btn_add = tk.Button(
            button_frame,
            text="Добавить",
            font=FONTS['button'],
            command=self.add_material,
            bg=COLORS['bg_button_success'],
            fg=COLORS['text_primary'],
            activebackground='#229954',
            activeforeground=COLORS['text_primary'],
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        btn_add.pack(side=tk.LEFT, padx=5)
        
        btn_update = tk.Button(
            button_frame,
            text="Изменить",
            font=FONTS['button'],
            command=self.update_material,
            bg=COLORS['accent_blue'],
            fg=COLORS['text_primary'],
            activebackground='#2980b9',
            activeforeground=COLORS['text_primary'],
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        btn_update.pack(side=tk.LEFT, padx=5)
        
        btn_delete = tk.Button(
            button_frame,
            text="Удалить",
            font=FONTS['button'],
            command=self.delete_material,
            bg=COLORS['bg_button_danger'],
            fg=COLORS['text_primary'],
            activebackground='#c0392b',
            activeforeground=COLORS['text_primary'],
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        btn_delete.pack(side=tk.LEFT, padx=5)
        
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
            padx=20,
            pady=10
        )
        btn_clear.pack(side=tk.LEFT, padx=5)
        
        # Разделитель
        separator = tk.Frame(content, height=2, bg=COLORS['separator'])
        separator.pack(fill=tk.X, padx=SIZES['padding'], pady=SIZES['padding'])
        
        # Список материалов
        list_frame = tk.Frame(content, bg=COLORS['bg_frame'], padx=SIZES['padding'], pady=SIZES['padding'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding'], pady=SIZES['padding'])
        
        list_title = tk.Label(
            list_frame,
            text="Список материалов",
            font=FONTS['subheading'],
            bg=COLORS['bg_frame'],
            fg=COLORS['text_primary'],
            pady=10
        )
        list_title.pack()
        
        # Treeview для отображения материалов
        tree_frame = tk.Frame(list_frame, bg=COLORS['bg_frame'])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("id", "name", "unit", "category", "min_stock", "max_stock")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Настраиваем колонки
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Название")
        self.tree.heading("unit", text="Единица измерения")
        self.tree.heading("category", text="Тип")
        self.tree.heading("min_stock", text="Мин. запас")
        self.tree.heading("max_stock", text="Макс. запас")
        
        self.tree.column("id", width=60, anchor=tk.CENTER)
        self.tree.column("name", width=250, anchor=tk.W)
        self.tree.column("unit", width=150, anchor=tk.CENTER)
        self.tree.column("category", width=150, anchor=tk.CENTER)
        self.tree.column("min_stock", width=120, anchor=tk.E)
        self.tree.column("max_stock", width=120, anchor=tk.E)
        
        # Привязываем выбор строки
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопка обновления
        btn_refresh = tk.Button(
            list_frame,
            text="Обновить список",
            font=FONTS['body'],
            command=self.refresh_materials_list,
            bg=COLORS['accent_blue'],
            fg=COLORS['text_primary'],
            activebackground='#2980b9',
            activeforeground=COLORS['text_primary'],
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        btn_refresh.pack(pady=10)
    
    def on_select(self, event):
        """Обработчик выбора материала в таблице."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            if values:
                self.selected_material_id = values[0]
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, values[1])
                self.unit_entry.delete(0, tk.END)
                self.unit_entry.insert(0, values[2])
                # Устанавливаем категорию
                if len(values) > 3 and values[3]:
                    self.category_combo.set(values[3])
                else:
                    self.category_combo.set(MATERIAL_CATEGORIES['other'])
                # Мин/макс запас
                if len(values) > 5:
                    self.min_entry.delete(0, tk.END)
                    self.min_entry.insert(0, values[4])
                    self.max_entry.delete(0, tk.END)
                    self.max_entry.insert(0, values[5] if values[5] is not None else "")
    
    def clear_form(self):
        """Очищает форму и снимает выделение."""
        self.name_entry.delete(0, tk.END)
        self.unit_entry.delete(0, tk.END)
        self.unit_entry.insert(0, "м")
        self.category_combo.set(MATERIAL_CATEGORIES['other'])
        self.min_entry.delete(0, tk.END)
        self.min_entry.insert(0, "0")
        self.max_entry.delete(0, tk.END)
        self.selected_material_id = None
        self.tree.selection_remove(self.tree.selection())
    
    def add_material(self):
        """Добавляет новый материал."""
        name = self.name_entry.get().strip()
        unit = self.unit_entry.get().strip()
        category_display = self.category_combo.get()
        min_stock = self.min_entry.get().strip() or "0"
        max_stock = self.max_entry.get().strip()
        
        if not name:
            messagebox.showerror("Ошибка", "Введите название материала!")
            return
        
        if not unit:
            messagebox.showerror("Ошибка", "Введите единицу измерения!")
            return
        
        # Преобразуем отображаемое значение в код категории
        category = 'other'  # По умолчанию
        for key, value in MATERIAL_CATEGORIES.items():
            if value == category_display:
                category = key
                break
        
        try:
            min_value = float(min_stock)
            max_value = float(max_stock) if max_stock else None
        except ValueError:
            messagebox.showerror("Ошибка", "Мин/Макс запас должны быть числом")
            return

        material_id = add_material(name, unit, category, min_value, max_value)
        
        if material_id:
            messagebox.showinfo("Успех", f"Материал '{name}' успешно добавлен!")
            self.clear_form()
            self.refresh_materials_list()
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить материал. Возможно, он уже существует.")
    
    def update_material(self):
        """Обновляет выбранный материал."""
        if not self.selected_material_id:
            messagebox.showerror("Ошибка", "Выберите материал для изменения!")
            return
        
        name = self.name_entry.get().strip()
        unit = self.unit_entry.get().strip()
        category_display = self.category_combo.get()
        min_stock = self.min_entry.get().strip() or "0"
        max_stock = self.max_entry.get().strip()
        
        if not name:
            messagebox.showerror("Ошибка", "Введите название материала!")
            return
        
        if not unit:
            messagebox.showerror("Ошибка", "Введите единицу измерения!")
            return
        
        # Преобразуем отображаемое значение в код категории
        category = 'other'  # По умолчанию
        for key, value in MATERIAL_CATEGORIES.items():
            if value == category_display:
                category = key
                break
        
        try:
            min_value = float(min_stock)
            max_value = float(max_stock) if max_stock else None
        except ValueError:
            messagebox.showerror("Ошибка", "Мин/Макс запас должны быть числом")
            return

        if update_material(self.selected_material_id, name, unit, category, min_value, max_value):
            messagebox.showinfo("Успех", f"Материал успешно обновлен!")
            self.clear_form()
            self.refresh_materials_list()
        else:
            messagebox.showerror("Ошибка", "Не удалось обновить материал!")
    
    def delete_material(self):
        """Удаляет выбранный материал."""
        if not self.selected_material_id:
            messagebox.showerror("Ошибка", "Выберите материал для удаления!")
            return
        
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот материал?\nЭто также удалит все связанные партии и операции!"):
            return
        
        if delete_material(self.selected_material_id):
            messagebox.showinfo("Успех", "Материал успешно удален!")
            self.clear_form()
            self.refresh_materials_list()
        else:
            messagebox.showerror("Ошибка", "Не удалось удалить материал!")
    
    def refresh_materials_list(self):
        """Обновляет список материалов."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        materials = get_all_materials()
        
        for material in materials:
            # Преобразуем код категории в отображаемое значение
            category_display = MATERIAL_CATEGORIES.get(material.get('category', 'other'), 'Прочее')
            min_stock = material.get('min_stock') if material.get('min_stock') is not None else material.get('minstock', 0)
            max_stock = material.get('max_stock') if material.get('max_stock') is not None else material.get('maxstock')
            
            self.tree.insert(
                "",
                tk.END,
                values=(
                    material['id'],
                    material['name'],
                    material['unit'],
                    category_display,
                    min_stock,
                    max_stock
                )
            )
    
    def refresh(self):
        """Обновляет данные экрана при показе."""
        self.refresh_materials_list()
