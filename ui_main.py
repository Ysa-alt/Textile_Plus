"""
Главное окно приложения для управления складом.
Содержит менеджер экранов и управление полноэкранным режимом.
"""

import tkinter as tk
from tkinter import messagebox
from config import COLORS, FONTS, SIZES
from db import create_tables, migrate_tables
from ui_login import LoginScreen
from ui_materials import MaterialsScreen
from ui_receipt import ReceiptScreen
from ui_issue import IssueScreen
from ui_reports import ReportsScreen
from ui_replenishment import ReplenishmentScreen
from ui_locations import LocationsScreen
from ui_suppliers import SuppliersScreen
from ui_orders import OrdersScreen
from ui_reservations import ReservationsScreen
from ui_quality import QualityScreen
from ui_transfer import TransferScreen


class App:
    """
    Главный класс приложения с менеджером экранов.
    Управляет переключением между экранами и полноэкранным режимом.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Управление складом - Текстиль Плюс")
        self.root.geometry(f"{SIZES['window_default_width']}x{SIZES['window_default_height']}")
        self.root.minsize(SIZES['window_min_width'], SIZES['window_min_height'])
        self.root.resizable(True, True)
        self.root.configure(bg=COLORS['bg_main'])
        
        # Выполняем инициализацию базы данных при запуске приложения
        # Создает все таблицы и добавляет новые поля к существующим
        print("=" * 60)
        print("Проверка и обновление структуры базы данных...")
        print("=" * 60)
        try:
            if create_tables():  # Создает все таблицы, если их нет
                print("✓ Таблицы проверены/созданы")
            migrate_tables()  # Добавляет новые поля к существующим таблицам
            print("=" * 60)
            print("✓ Структура базы данных готова к работе")
            print("=" * 60)
        except Exception as e:
            print(f"⚠ Ошибка при обновлении БД: {e}")
            print("Попробуйте запустить: python db.py")
            import traceback
            traceback.print_exc()
        
        # Текущий пользователь и роль
        self.current_user = None
        self.user_role = None
        
        # Состояние полноэкранного режима
        self.fullscreen = False
        
        # Привязываем горячие клавиши
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.exit_fullscreen)
        
        # Контейнер для экранов
        self.container = tk.Frame(self.root, bg=COLORS['bg_main'])
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Словарь для хранения экранов
        self.frames = {}
        
        # Создаем все экраны
        self._create_screens()
        
        # Показываем экран авторизации
        self.show_frame('Login')
        
        # Центрируем окно
        self.center_window()
    
    def has_permission(self, required_roles: list) -> bool:
        """
        Проверяет, есть ли у текущего пользователя права доступа.
        
        Args:
            required_roles: Список ролей, которым разрешен доступ
        
        Returns:
            True если доступ разрешен, False иначе
        """
        if not self.user_role:
            return False
        return self.user_role in required_roles or 'admin' in required_roles or self.user_role == 'admin'
    
    def _create_screens(self):
        """Создает все экраны приложения."""
        # Экран авторизации
        self.frames['Login'] = LoginScreen(self.container, self)
        
        # Главное меню
        main_menu = MainMenu(self.container, self)
        self.frames['MainMenu'] = main_menu
        
        # Экраны функционала
        self.frames['Materials'] = MaterialsScreen(self.container, self)
        self.frames['Receipt'] = ReceiptScreen(self.container, self)
        self.frames['Issue'] = IssueScreen(self.container, self)
        self.frames['Reports'] = ReportsScreen(self.container, self)
        self.frames['Replenishment'] = ReplenishmentScreen(self.container, self)
        self.frames['Locations'] = LocationsScreen(self.container, self)
        self.frames['Suppliers'] = SuppliersScreen(self.container, self)
        self.frames['Orders'] = OrdersScreen(self.container, self)
        self.frames['Reservations'] = ReservationsScreen(self.container, self)
        self.frames['Quality'] = QualityScreen(self.container, self)
        self.frames['Transfer'] = TransferScreen(self.container, self)
        
        # Размещаем все экраны в одном месте (они будут показываться по очереди)
        for frame in self.frames.values():
            frame.place(x=0, y=0, relwidth=1, relheight=1)
    
    def show_frame(self, frame_name: str):
        """
        Показывает указанный экран и скрывает остальные.
        
        Args:
            frame_name: Имя экрана для отображения ('MainMenu', 'Materials', и т.д.)
        """
        # Скрываем все экраны
        for frame in self.frames.values():
            frame.lower()
        
        # Показываем выбранный экран
        if frame_name in self.frames:
            self.frames[frame_name].lift()
            # Обновляем данные экрана, если нужно
            if hasattr(self.frames[frame_name], 'refresh'):
                self.frames[frame_name].refresh()
    
    def toggle_fullscreen(self, event=None):
        """
        Переключает полноэкранный режим.
        Горячая клавиша: F11
        """
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)
    
    def exit_fullscreen(self, event=None):
        """
        Выходит из полноэкранного режима.
        Горячая клавиша: Esc
        """
        if self.fullscreen:
            self.fullscreen = False
            self.root.attributes('-fullscreen', False)
    
    def center_window(self):
        """Центрирует окно на экране."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def quit_app(self):
        """Закрывает приложение."""
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.root.quit()


class MainMenu(tk.Frame):
    """
    Главное меню приложения с кнопками навигации.
    """
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg_main'])
        self.app = app
        
        self.create_widgets()
    
    def create_widgets(self):
        """Создает виджеты главного меню."""
        def allowed(required):
            return self.app.has_permission(required)

        # Заголовок
        title_label = tk.Label(
            self,
            text="Управление складом",
            font=FONTS['title'],
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary'],
            pady=30
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            self,
            text="Текстиль Плюс",
            font=FONTS['subheading'],
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary'],
            pady=10
        )
        subtitle_label.pack()
        
        # Фрейм для кнопок
        button_frame = tk.Frame(self, bg=COLORS['bg_main'], pady=40)
        button_frame.pack(expand=True)
        
        # Кнопка "Материалы"
        if allowed(['storekeeper', 'admin', 'supply']):
            btn_materials = tk.Button(
                button_frame,
                text="Материалы",
                font=FONTS['button'],
                width=SIZES['button_width'],
                height=SIZES['button_height'],
                command=lambda: self.app.show_frame('Materials'),
                bg=COLORS['bg_button'],
                fg=COLORS['text_primary'],
                activebackground=COLORS['bg_button_hover'],
                activeforeground=COLORS['text_primary'],
                cursor="hand2",
                relief=tk.FLAT,
                padx=20,
                pady=15
            )
            btn_materials.pack(pady=10)
        
        # Кнопка "Приход"
        if allowed(['storekeeper', 'admin']):
            btn_receipt = tk.Button(
                button_frame,
                text="Приход материалов",
                font=FONTS['button'],
                width=SIZES['button_width'],
                height=SIZES['button_height'],
                command=lambda: self.app.show_frame('Receipt'),
                bg=COLORS['bg_button'],
                fg=COLORS['text_primary'],
                activebackground=COLORS['bg_button_hover'],
                activeforeground=COLORS['text_primary'],
                cursor="hand2",
                relief=tk.FLAT,
                padx=20,
                pady=15
            )
            btn_receipt.pack(pady=10)
        
        # Кнопка "Списание"
        if allowed(['storekeeper', 'admin']):
            btn_issue = tk.Button(
                button_frame,
                text="Списание материалов",
                font=FONTS['button'],
                width=SIZES['button_width'],
                height=SIZES['button_height'],
                command=lambda: self.app.show_frame('Issue'),
                bg=COLORS['bg_button'],
                fg=COLORS['text_primary'],
                activebackground=COLORS['bg_button_hover'],
                activeforeground=COLORS['text_primary'],
                cursor="hand2",
                relief=tk.FLAT,
                padx=20,
                pady=15
            )
            btn_issue.pack(pady=10)

        # Перемещение
        if allowed(['storekeeper', 'admin']):
            tk.Button(
                button_frame,
                text="Перемещения",
                font=FONTS['button'],
                width=SIZES['button_width'],
                height=SIZES['button_height'],
                command=lambda: self.app.show_frame('Transfer'),
                bg=COLORS['bg_button'],
                fg=COLORS['text_primary'],
                activebackground=COLORS['bg_button_hover'],
                activeforeground=COLORS['text_primary'],
                cursor="hand2",
                relief=tk.FLAT,
                padx=20,
                pady=15
            ).pack(pady=10)
            tk.Button(
                button_frame,
                text="Адреса хранения",
                font=FONTS['button'],
                width=SIZES['button_width'],
                height=SIZES['button_height'],
                command=lambda: self.app.show_frame('Locations'),
                bg=COLORS['bg_button'],
                fg=COLORS['text_primary'],
                activebackground=COLORS['bg_button_hover'],
                activeforeground=COLORS['text_primary'],
                cursor="hand2",
                relief=tk.FLAT,
                padx=20,
                pady=15
            ).pack(pady=10)
        
        # Кнопка "Отчеты"
        if allowed(['accountant', 'admin', 'storekeeper', 'supply']):
            btn_reports = tk.Button(
                button_frame,
                text="Отчет по остаткам",
                font=FONTS['button'],
                width=SIZES['button_width'],
                height=SIZES['button_height'],
                command=lambda: self.app.show_frame('Reports'),
                bg=COLORS['bg_button'],
                fg=COLORS['text_primary'],
                activebackground=COLORS['bg_button_hover'],
                activeforeground=COLORS['text_primary'],
                cursor="hand2",
                relief=tk.FLAT,
                padx=20,
                pady=15
            )
            btn_reports.pack(pady=10)
        
        # Кнопка "Заявки на пополнение" (для снабженцев)
        if allowed(['supply', 'admin']):
            btn_replenishment = tk.Button(
                button_frame,
                text="Заявки на пополнение",
                font=FONTS['button'],
                width=SIZES['button_width'],
                height=SIZES['button_height'],
                command=lambda: self.app.show_frame('Replenishment'),
                bg=COLORS['accent_orange'],
                fg=COLORS['text_primary'],
                activebackground='#e67e22',
                activeforeground=COLORS['text_primary'],
                cursor="hand2",
                relief=tk.FLAT,
                padx=20,
                pady=15
            )
            btn_replenishment.pack(pady=10)

        # Поставщики и договоры
        if allowed(['supply', 'admin']):
            tk.Button(
                button_frame,
                text="Поставщики / Договоры",
                font=FONTS['button'],
                width=SIZES['button_width'],
                height=SIZES['button_height'],
                command=lambda: self.app.show_frame('Suppliers'),
                bg=COLORS['bg_button'],
                fg=COLORS['text_primary'],
                activebackground=COLORS['bg_button_hover'],
                activeforeground=COLORS['text_primary'],
                cursor="hand2",
                relief=tk.FLAT,
                padx=20,
                pady=15
            ).pack(pady=10)

        # Заказы и резервы
        if allowed(['storekeeper', 'admin', 'supply']):
            tk.Button(
                button_frame,
                text="Заказы производства",
                font=FONTS['button'],
                width=SIZES['button_width'],
                height=SIZES['button_height'],
                command=lambda: self.app.show_frame('Orders'),
                bg=COLORS['bg_button'],
                fg=COLORS['text_primary'],
                activebackground=COLORS['bg_button_hover'],
                activeforeground=COLORS['text_primary'],
                cursor="hand2",
                relief=tk.FLAT,
                padx=20,
                pady=15
            ).pack(pady=10)
            tk.Button(
                button_frame,
                text="Резервы материалов",
                font=FONTS['button'],
                width=SIZES['button_width'],
                height=SIZES['button_height'],
                command=lambda: self.app.show_frame('Reservations'),
                bg=COLORS['bg_button'],
                fg=COLORS['text_primary'],
                activebackground=COLORS['bg_button_hover'],
                activeforeground=COLORS['text_primary'],
                cursor="hand2",
                relief=tk.FLAT,
                padx=20,
                pady=15
            ).pack(pady=10)

        # Качество партий
        if allowed(['storekeeper', 'admin']):
            tk.Button(
                button_frame,
                text="Качество партий",
                font=FONTS['button'],
                width=SIZES['button_width'],
                height=SIZES['button_height'],
                command=lambda: self.app.show_frame('Quality'),
                bg=COLORS['bg_button'],
                fg=COLORS['text_primary'],
                activebackground=COLORS['bg_button_hover'],
                activeforeground=COLORS['text_primary'],
                cursor="hand2",
                relief=tk.FLAT,
                padx=20,
                pady=15
            ).pack(pady=10)
        
        # Информация о пользователе
        if self.app.current_user:
            user_info = tk.Label(
                self,
                text=f"Пользователь: {self.app.current_user['username']} | Роль: {self.app.user_role}",
                font=FONTS['small'],
                bg=COLORS['bg_main'],
                fg=COLORS['text_secondary'],
                pady=10
            )
            user_info.pack()
        
        # Кнопка "Выход"
        btn_exit = tk.Button(
            button_frame,
            text="Выход",
            font=FONTS['button'],
            width=SIZES['button_width'],
            height=SIZES['button_height'],
            command=self.app.quit_app,
            bg=COLORS['bg_button_danger'],
            fg=COLORS['text_primary'],
            activebackground='#c0392b',
            activeforeground=COLORS['text_primary'],
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=15
        )
        btn_exit.pack(pady=20)
        
        # Информационная метка
        info_label = tk.Label(
            self,
            text="F11 - полноэкранный режим | Esc - выход из полноэкранного режима",
            font=FONTS['small'],
            bg=COLORS['bg_main'],
            fg=COLORS['text_muted'],
            pady=20
        )
        info_label.pack(side=tk.BOTTOM)


def main():
    """Точка входа в приложение."""
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
