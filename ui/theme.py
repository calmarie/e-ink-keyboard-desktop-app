# Вся палитра лежит в одном словаре, чтобы тему можно было быстро перекрасить.
COLORS = {
    "bg": "#111111",
    "panel": "#383838",
    "panel_alt": "#444444",
    "surface": "#4a4a4a",
    "surface_hover": "#565656",
    "surface_pressed": "#616161",
    "text": "#f5f5f5",
    "muted": "#cfcfcf",
    "accent": "#d996ea",
    "accent_soft": "#c98bdc",
    "border": "#505050",
    "input": "#2f2f2f",
}

FONT_FAMILY = "Segoe UI"


def window_style() -> str:
    # Глобальный стиль окна и стандартных диалогов.
    return f"""
        QMainWindow {{
            background-color: {COLORS["bg"]};
            color: {COLORS["text"]};
            font-family: \"{FONT_FAMILY}\";
        }}
        QMessageBox {{
            background-color: {COLORS["panel"]};
            color: {COLORS["text"]};
        }}
        QMessageBox QPushButton {{
            min-width: 110px;
            min-height: 36px;
            border-radius: 16px;
            padding: 6px 16px;
            background-color: {COLORS["surface"]};
            color: {COLORS["text"]};
            border: 1px solid {COLORS["accent"]};
        }}
    """


def title_style(size: int = 34) -> str:
    # Унифицированный стиль для крупных заголовков страниц.
    return f"""
        font-family: \"{FONT_FAMILY}\";
        font-size: {size}px;
        font-weight: 400;
        color: {COLORS["text"]};
    """


def panel_style() -> str:
    # Большая скругленная карточка-контейнер в центре страницы.
    return f"""
        QFrame {{
            background-color: {COLORS["panel"]};
            border-radius: 36px;
        }}
    """


def side_button_style(active: bool = False) -> str:
    # Левая вертикальная кнопка; `active=True` подсвечивает текущий раздел.
    border_color = COLORS["accent"] if active else COLORS["border"]
    border_width = "2px" if active else "1px"
    return f"""
        QPushButton {{
            background-color: {COLORS["surface"]};
            color: {COLORS["text"]};
            border: {border_width} solid {border_color};
            border-radius: 28px;
            text-align: left;
            padding: 18px 22px;
            font-family: \"{FONT_FAMILY}\";
            font-size: 16px;
            font-weight: 400;
        }}
        QPushButton:hover {{
            background-color: {COLORS["surface_hover"]};
        }}
        QPushButton:pressed {{
            background-color: {COLORS["surface_pressed"]};
        }}
    """


def primary_button_style() -> str:
    # Основная CTA-кнопка вроде "Установить".
    return f"""
        QPushButton {{
            background-color: {COLORS["surface"]};
            color: {COLORS["text"]};
            border: 2px solid {COLORS["accent"]};
            border-radius: 24px;
            font-family: \"{FONT_FAMILY}\";
            font-size: 18px;
            font-weight: 500;
            padding: 14px 28px;
        }}
        QPushButton:hover {{
            background-color: {COLORS["surface_hover"]};
        }}
        QPushButton:pressed {{
            background-color: {COLORS["surface_pressed"]};
        }}
    """


def outline_button_style() -> str:
    # Легкая акцентная кнопка для "Назад" и вторичных действий.
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {COLORS["text"]};
            border: 1px solid {COLORS["accent"]};
            border-radius: 18px;
            font-family: \"{FONT_FAMILY}\";
            font-size: 15px;
            padding: 8px 16px;
        }}
        QPushButton:hover {{
            background-color: rgba(217, 150, 234, 0.12);
        }}
    """


def key_button_style() -> str:
    # Крупные кнопки выбора физической клавиши на стартовом экране.
    return f"""
        QPushButton {{
            background-color: {COLORS["surface"]};
            color: {COLORS["text"]};
            border: 2px solid transparent;
            border-radius: 28px;
            font-family: \"{FONT_FAMILY}\";
            font-size: 24px;
            font-weight: 500;
            padding: 16px;
        }}
        QPushButton:hover {{
            border-color: {COLORS["accent"]};
            background-color: {COLORS["surface_hover"]};
        }}
        QPushButton:pressed {{
            background-color: {COLORS["surface_pressed"]};
        }}
    """


def combo_style() -> str:
    # Оформление выпадающего списка действия.
    return f"""
        QComboBox {{
            background-color: {COLORS["surface"]};
            color: {COLORS["text"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 18px;
            padding: 10px 16px;
            min-height: 24px;
            font-family: \"{FONT_FAMILY}\";
            font-size: 15px;
        }}
        QComboBox::drop-down {{
            border: none;
            width: 28px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {COLORS["surface"]};
            color: {COLORS["text"]};
            selection-background-color: {COLORS["accent"]};
            selection-color: {COLORS["bg"]};
            border: 1px solid {COLORS["border"]};
        }}
    """


def list_style() -> str:
    # Список готовых hotkey-команд в редакторе.
    return f"""
        QListWidget {{
            background-color: transparent;
            border: none;
            color: {COLORS["text"]};
            outline: none;
            font-family: \"{FONT_FAMILY}\";
            font-size: 15px;
        }}
        QListWidget::item {{
            background-color: transparent;
            border: none;
            border-radius: 18px;
            padding: 8px 14px;
            margin: 2px 0;
        }}
        QListWidget::item:selected {{
            background-color: {COLORS["surface"]};
            border: 1px solid {COLORS["accent"]};
        }}
        QListWidget::item:hover {{
            background-color: {COLORS["surface_hover"]};
        }}
    """


def line_edit_style() -> str:
    # Единый вид текстовых полей.
    return f"""
        QLineEdit {{
            background-color: {COLORS["input"]};
            color: {COLORS["text"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 18px;
            padding: 12px 14px;
            font-family: \"{FONT_FAMILY}\";
            font-size: 15px;
        }}
        QLineEdit:focus {{
            border: 1px solid {COLORS["accent"]};
        }}
    """


def label_style(muted: bool = False, size: int = 16) -> str:
    # Вариант для обычных и приглушенных подписей.
    color = COLORS["muted"] if muted else COLORS["text"]
    return f"""
        color: {color};
        font-family: \"{FONT_FAMILY}\";
        font-size: {size}px;
    """


def drop_area_style() -> str:
    # Внутренняя зона drag-and-drop с заметной серой рамкой.
    return f"""
        QFrame {{
            background-color: rgba(255, 255, 255, 0.02);
            border: 1px solid {COLORS["border"]};
            border-radius: 32px;
        }}
    """


def picker_container_style() -> str:
    # Внешний контейнер блока выбора картинки с единственной серой рамкой.
    return f"""
        QFrame {{
            background-color: transparent;
            border: 1px solid {COLORS["border"]};
            border-radius: 28px;
        }}
    """


def preview_card_style() -> str:
    # Мини-карточки недавно выбранных изображений.
    return f"""
        QPushButton {{
            background-color: {COLORS["surface"]};
            color: {COLORS["text"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 22px;
            font-family: \"{FONT_FAMILY}\";
            font-size: 14px;
            padding: 12px;
        }}
        QPushButton:hover {{
            background-color: {COLORS["surface_hover"]};
            border-color: {COLORS["accent"]};
        }}
        QPushButton:disabled {{
            color: {COLORS["muted"]};
            background-color: {COLORS["panel_alt"]};
        }}
    """


def arrow_button_style() -> str:
    # Стрелки листания списка картинок.
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {COLORS["text"]};
            border: none;
            font-family: \"{FONT_FAMILY}\";
            font-size: 42px;
            font-weight: 300;
        }}
        QPushButton:hover {{
            color: {COLORS["accent"]};
        }}
        QPushButton:disabled {{
            color: {COLORS["border"]};
        }}
    """
