"""
Экран управления пользователями.
Для ИТ отдела и руководства: просмотр и управление пользователями системы.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORS, FONTS, SIZES
from utils import ScrollableFrame
from db import get_connection


class UsersScreen(ScrollableFrame):
    """
    Экран для управления пользователями.
    """
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg_main'])
        self.app = app
        self.content = self.scrollable_frame
        self.create_widgets()
        self.refresh()
    
    def create_widgets(self):
        """Создает виджеты экрана."""
        # Заголовок
        title_label = tk.Label(
            self.content,
            text="Управление пользователями",
            font=FONTS['heading'],
            bg=COLORS['bg_frame'],
            fg=COLORS['text_primary'],
            pady=20
        )
        title_label.pack()
        
        # Кнопка "Назад"
        btn_back = tk.Button(
            self.content,
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
        
        # Таблица пользователей
        table_frame = tk.Frame(self.content, bg=COLORS['bg_frame'], padx=SIZES['padding'], pady=SIZES['padding'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding'], pady=SIZES['padding'])
        
        columns = ("id", "username", "role")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("username", text="Имя пользователя")
        self.tree.heading("role", text="Роль")
        
        self.tree.column("id", width=60, anchor=tk.CENTER)
        self.tree.column("username", width=200, anchor=tk.W)
        self.tree.column("role", width=200, anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопка обновления
        btn_refresh = tk.Button(
            self.content,
            text="Обновить",
            font=FONTS['body'],
            command=self.refresh,
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
    
    def refresh(self):
        """Обновляет список пользователей."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        connection = get_connection()
        if not connection:
            return
        
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users ORDER BY username")
            users = cursor.fetchall()
            
            role_names = {
                'director': 'Руководство',
                'supply': 'Отдел снабжения',
                'storekeeper': 'Складской персонал',
                'production': 'Производственный отдел',
                'it': 'ИТ отдел',
                'accountant': 'Бухгалтерия',
                'quality': 'Отдел контроля качества',
                'admin': 'Администратор'
            }
            
            for user in users:
                role_display = role_names.get(user.get('role', ''), user.get('role', ''))
                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        user.get('id', ''),
                        user.get('username', ''),
                        role_display
                    )
                )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить пользователей: {e}")
        finally:
            cursor.close()
            connection.close()

