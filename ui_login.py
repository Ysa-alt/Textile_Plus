"""
Экран авторизации пользователя.
Простая форма входа без шифрования для учебного проекта.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from config import COLORS, FONTS, SIZES
from models_extended import get_user_by_username


class LoginScreen(tk.Frame):
    """
    Экран авторизации пользователя.
    """
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg_main'])
        self.app = app
        self.current_user = None
        
        self.create_widgets()
    
    def create_widgets(self):
        """Создает виджеты экрана авторизации."""
        # Центральный фрейм
        center_frame = tk.Frame(self, bg=COLORS['bg_main'])
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Заголовок
        title_label = tk.Label(
            center_frame,
            text="Вход в систему",
            font=FONTS['title'],
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary'],
            pady=20
        )
        title_label.pack()
        
        # Форма входа
        form_frame = tk.Frame(center_frame, bg=COLORS['bg_frame'], padx=40, pady=30)
        form_frame.pack()
        
        tk.Label(
            form_frame,
            text="Имя пользователя:",
            font=FONTS['body'],
            bg=COLORS['bg_frame'],
            fg=COLORS['text_primary']
        ).pack(anchor=tk.W, pady=10)
        
        self.username_entry = tk.Entry(
            form_frame,
            font=FONTS['body'],
            width=30,
            bg=COLORS['bg_entry'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            relief=tk.FLAT
        )
        self.username_entry.pack(pady=5)
        self.username_entry.focus()
        self.username_entry.bind('<Return>', lambda e: self.login())
        
        # Кнопка входа
        btn_login = tk.Button(
            form_frame,
            text="Войти",
            font=FONTS['button'],
            command=self.login,
            bg=COLORS['bg_button'],
            fg=COLORS['text_primary'],
            activebackground=COLORS['bg_button_hover'],
            activeforeground=COLORS['text_primary'],
            cursor="hand2",
            relief=tk.FLAT,
            width=20,
            padx=20,
            pady=10
        )
        btn_login.pack(pady=20)
        
        # Информация
        info_label = tk.Label(
            center_frame,
            text="Логины: director, supply, storekeeper, production, it, accountant, quality",
            font=FONTS['small'],
            bg=COLORS['bg_main'],
            fg=COLORS['text_muted'],
            pady=10
        )
        info_label.pack()
    
    def login(self):
        """Выполняет авторизацию пользователя (без пароля)."""
        username = self.username_entry.get().strip()
        
        if not username:
            messagebox.showerror("Ошибка", "Введите имя пользователя!")
            return
        
        # Список разрешенных ролей по ТЗ
        allowed_roles = ['director', 'supply', 'storekeeper', 'production', 'it', 'accountant', 'quality']
        
        if username not in allowed_roles:
            messagebox.showerror("Ошибка", f"Неверный логин. Используйте: {', '.join(allowed_roles)}")
            return
        
        # Ищем или создаем пользователя
        user = get_user_by_username(username)
        
        if not user:
            # Создаем пользователя с ролью = логину
            from db import get_connection
            connection = get_connection()
            if connection:
                cursor = connection.cursor()
                try:
                    cursor.execute(
                        "INSERT INTO users (username, role) VALUES (%s, %s)",
                        (username, username)  # роль = логин
                    )
                    connection.commit()
                    user = {'id': cursor.lastrowid, 'username': username, 'role': username}
                    print(f"Создан новый пользователь: {username} с ролью {username}")
                except Exception as e:
                    print(f"Ошибка при создании пользователя: {e}")
                    connection.rollback()
                    # Пробуем найти пользователя с другой ролью
                    user = get_user_by_username(username)
                finally:
                    cursor.close()
                    connection.close()
        
        if user:
            self.current_user = user
            self.app.current_user = user
            self.app.user_role = user.get('role', username)  # Используем роль из БД или логин
            self.app.show_frame('MainMenu')
        else:
            messagebox.showerror("Ошибка", "Не удалось войти в систему!")


