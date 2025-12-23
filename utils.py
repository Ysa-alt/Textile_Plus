"""
Вспомогательные модули для интерфейса.
Содержит класс ScrollableFrame для создания прокручиваемых контейнеров.
"""

import tkinter as tk
from tkinter import ttk
from config import COLORS, SCROLLBAR_WIDTH


class ScrollableFrame(tk.Frame):
    """
    Прокручиваемый фрейм на основе Canvas и Scrollbar.
    Позволяет создавать контейнеры с вертикальной прокруткой.
    
    Использование:
        scroll_frame = ScrollableFrame(parent)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        # Добавляем виджеты в scroll_frame.scrollable_frame
        label = tk.Label(scroll_frame.scrollable_frame, text="Текст")
        label.pack()
    """
    
    def __init__(self, parent, *args, **kwargs):
        """
        Инициализация прокручиваемого фрейма.
        
        Args:
            parent: Родительский виджет
            *args, **kwargs: Дополнительные параметры для Frame
        """
        super().__init__(parent, *args, **kwargs)
        
        # Создаем Canvas для прокрутки
        self.canvas = tk.Canvas(
            self,
            bg=COLORS['bg_frame'],
            highlightthickness=0,
            borderwidth=0
        )
        
        # Создаем вертикальный скроллбар
        self.scrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.canvas.yview
        )
        
        # Создаем внутренний фрейм для содержимого
        self.scrollable_frame = tk.Frame(
            self.canvas,
            bg=COLORS['bg_frame']
        )
        
        # Привязываем прокрутку колесиком мыши
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Создаем окно в Canvas для scrollable_frame
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )
        
        # Настраиваем Canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Привязываем события прокрутки
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        
        # Привязываем прокрутку колесиком мыши
        # Для Windows используется <MouseWheel>, для Linux - <Button-4> и <Button-5>
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel_linux)
        self.canvas.bind("<Button-5>", self._on_mousewheel_linux)
        self.scrollable_frame.bind("<Button-4>", self._on_mousewheel_linux)
        self.scrollable_frame.bind("<Button-5>", self._on_mousewheel_linux)
        
        # Размещаем виджеты
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _on_canvas_configure(self, event):
        """
        Обработчик изменения размера Canvas.
        Обновляет ширину внутреннего фрейма.
        """
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def _on_frame_configure(self, event):
        """
        Обработчик изменения размера внутреннего фрейма.
        Обновляет область прокрутки Canvas.
        """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_mousewheel(self, event):
        """
        Обработчик прокрутки колесиком мыши (Windows).
        Прокручивает Canvas при движении колесика.
        """
        # Прокручиваем Canvas
        try:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except:
            pass
    
    def _on_mousewheel_linux(self, event):
        """
        Обработчик прокрутки колесиком мыши (Linux).
        Прокручивает Canvas при движении колесика.
        """
        try:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
        except:
            pass

