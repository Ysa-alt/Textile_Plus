"""
Экран журнала аудита.
Для ИТ отдела и руководства: просмотр всех операций в системе.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORS, FONTS, SIZES
from utils import ScrollableFrame
from db import get_connection


class AuditScreen(ScrollableFrame):
    """
    Экран для просмотра журнала аудита.
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
            text="Журнал аудита",
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
        
        # Таблица аудита
        table_frame = tk.Frame(self.content, bg=COLORS['bg_frame'], padx=SIZES['padding'], pady=SIZES['padding'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding'], pady=SIZES['padding'])
        
        columns = ("id", "user", "action", "details", "created")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("user", text="Пользователь")
        self.tree.heading("action", text="Действие")
        self.tree.heading("details", text="Детали")
        self.tree.heading("created", text="Дата/Время")
        
        self.tree.column("id", width=60, anchor=tk.CENTER)
        self.tree.column("user", width=150, anchor=tk.W)
        self.tree.column("action", width=300, anchor=tk.W)
        self.tree.column("details", width=300, anchor=tk.W)
        self.tree.column("created", width=180, anchor=tk.CENTER)
        
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
        """Обновляет список записей аудита."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        connection = get_connection()
        if not connection:
            return
        
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT a.*, u.username 
                FROM audit_log a
                LEFT JOIN users u ON u.id = a.user_id
                ORDER BY a.created_at DESC
                LIMIT 1000
            """)
            logs = cursor.fetchall()
            
            for log in logs:
                username = log.get('username', 'Система')
                created_at = log.get('created_at', '')
                if created_at:
                    created_at = created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(created_at, 'strftime') else str(created_at)
                
                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        log.get('id', ''),
                        username,
                        log.get('action', ''),
                        log.get('details', '') or '',
                        created_at
                    )
                )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить журнал аудита: {e}")
        finally:
            cursor.close()
            connection.close()


