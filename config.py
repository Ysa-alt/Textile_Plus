"""
Модуль с настройками стилей приложения.
Содержит цвета, шрифты, размеры для единообразного оформления.
"""

# Цветовая схема (темная тема)
COLORS = {
    # Основные цвета
    'bg_main': '#2b2b2b',           # Темный фон главного окна
    'bg_frame': '#3c3c3c',          # Фон карточек/фреймов
    'bg_entry': '#4a4a4a',          # Фон полей ввода
    'bg_button': '#6c5ce7',         # Основной цвет кнопок (фиолетовый)
    'bg_button_hover': '#5f4fd6',    # Цвет кнопок при наведении
    'bg_button_danger': '#e74c3c',   # Цвет кнопок удаления/отмены
    'bg_button_success': '#27ae60',  # Цвет кнопок сохранения
    'bg_button_secondary': '#7f8c8d', # Вторичный цвет кнопок
    
    # Текст
    'text_primary': '#ffffff',       # Основной текст
    'text_secondary': '#b0b0b0',     # Вторичный текст
    'text_muted': '#888888',         # Приглушенный текст
    
    # Границы и разделители
    'border': '#555555',             # Цвет границ
    'separator': '#555555',          # Цвет разделителей
    
    # Акцентные цвета
    'accent_blue': '#3498db',        # Синий акцент
    'accent_green': '#2ecc71',       # Зеленый акцент
    'accent_orange': '#f39c12',      # Оранжевый акцент
    'accent_red': '#e74c3c',         # Красный акцент
}

# Шрифты
FONTS = {
    'title': ('Segoe UI', 20, 'bold'),      # Заголовок окна
    'heading': ('Segoe UI', 16, 'bold'),     # Заголовок раздела
    'subheading': ('Segoe UI', 14, 'bold'),  # Подзаголовок
    'body': ('Segoe UI', 11),                # Обычный текст
    'small': ('Segoe UI', 9),                # Мелкий текст
    'button': ('Segoe UI', 11, 'bold'),      # Текст кнопок
}

# Размеры
SIZES = {
    'window_min_width': 800,
    'window_min_height': 600,
    'window_default_width': 1000,
    'window_default_height': 700,
    'padding': 20,                  # Стандартный отступ
    'padding_small': 10,            # Малый отступ
    'button_width': 20,             # Ширина кнопок (в символах)
    'button_height': 1,              # Высота кнопок (в строках)
    'entry_width': 30,              # Ширина полей ввода
}

# Настройки прокрутки
SCROLLBAR_WIDTH = 15


