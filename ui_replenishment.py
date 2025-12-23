"""
Экран управления заявками на пополнение.
Для отдела снабжения: просмотр и изменение статуса заявок.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from config import COLORS, FONTS, SIZES
from utils import ScrollableFrame
from models_extended import get_all_replenishment_requests, update_replenishment_request_status


class ReplenishmentScreen(tk.Frame):
    """
    Экран для управления заявками на пополнение.
    Автоматические заявки при минимальном уровне запаса.
    """
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg_main'])
        self.app = app
        
        self.create_widgets()
        self.refresh_requests()
    
    def create_widgets(self):
        """Создает виджеты экрана."""
        # Прокручиваемый контейнер
        scroll_frame = ScrollableFrame(self)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        content = scroll_frame.scrollable_frame
        
        # Заголовок
        title_label = tk.Label(
            content,
            text="Заявки на пополнение",
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
        
        # Таблица заявок
        table_frame = tk.Frame(content, bg=COLORS['bg_frame'], padx=SIZES['padding'], pady=SIZES['padding'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=SIZES['padding'], pady=SIZES['padding'])
        
        columns = ("id", "material", "qty", "status", "created")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("material", text="Материал")
        self.tree.heading("qty", text="Количество")
        self.tree.heading("status", text="Статус")
        self.tree.heading("created", text="Дата создания")
        
        self.tree.column("id", width=60, anchor=tk.CENTER)
        self.tree.column("material", width=250, anchor=tk.W)
        self.tree.column("qty", width=150, anchor=tk.E)
        self.tree.column("status", width=120, anchor=tk.CENTER)
        self.tree.column("created", width=180, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления статусом
        status_frame = tk.Frame(content, bg=COLORS['bg_frame'], pady=20)
        status_frame.pack()
        
        status_label = tk.Label(
            status_frame,
            text="Изменить статус выбранной заявки:",
            font=FONTS['body'],
            bg=COLORS['bg_frame'],
            fg=COLORS['text_primary']
        )
        status_label.pack(side=tk.LEFT, padx=10)
        
        btn_sent = tk.Button(
            status_frame,
            text="Отправлено (SENT)",
            font=FONTS['body'],
            command=lambda: self.update_status('SENT'),
            bg=COLORS['accent_blue'],
            fg=COLORS['text_primary'],
            cursor="hand2",
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        btn_sent.pack(side=tk.LEFT, padx=5)
        
        btn_approved = tk.Button(
            status_frame,
            text="Одобрено (APPROVED)",
            font=FONTS['body'],
            command=lambda: self.update_status('APPROVED'),
            bg=COLORS['bg_button_success'],
            fg=COLORS['text_primary'],
            cursor="hand2",
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        btn_approved.pack(side=tk.LEFT, padx=5)
        
        btn_rejected = tk.Button(
            status_frame,
            text="Отклонено (REJECTED)",
            font=FONTS['body'],
            command=lambda: self.update_status('REJECTED'),
            bg=COLORS['bg_button_danger'],
            fg=COLORS['text_primary'],
            cursor="hand2",
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        btn_rejected.pack(side=tk.LEFT, padx=5)
        
        btn_refresh = tk.Button(
            status_frame,
            text="Обновить",
            font=FONTS['body'],
            command=self.refresh_requests,
            bg=COLORS['bg_button_secondary'],
            fg=COLORS['text_primary'],
            cursor="hand2",
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        btn_refresh.pack(side=tk.LEFT, padx=5)
    
    def update_status(self, new_status: str):
        """Обновляет статус выбранной заявки."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showerror("Ошибка", "Выберите заявку!")
            return
        
        item = self.tree.item(selection[0])
        request_id = item['values'][0]
        
        user_id = self.app.current_user['id'] if self.app.current_user else None
        
        if update_replenishment_request_status(request_id, new_status, user_id):
            messagebox.showinfo("Успех", f"Статус заявки обновлен на {new_status}")
            self.refresh_requests()
        else:
            messagebox.showerror("Ошибка", "Не удалось обновить статус!")
    
    def refresh_requests(self):
        """Обновляет список заявок."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        requests = get_all_replenishment_requests()
        
        status_names = {
            'NEW': 'Новая',
            'SENT': 'Отправлено',
            'APPROVED': 'Одобрено',
            'REJECTED': 'Отклонено'
        }
        
        for req in requests:
            status_display = status_names.get(req['status'], req['status'])
            created_at = req['created_at'].strftime('%Y-%m-%d %H:%M') if req['created_at'] else ''
            
            self.tree.insert(
                "",
                tk.END,
                values=(
                    req['id'],
                    f"{req['material_name']} ({req['unit']})",
                    f"{req['requested_qty']:.3f}",
                    status_display,
                    created_at
                )
            )
    
    def refresh(self):
        """Обновляет данные экрана при показе."""
        self.refresh_requests()


