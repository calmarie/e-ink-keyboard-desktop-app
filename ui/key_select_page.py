from PySide6.QtCore import Qt
from PySide6.QtWidgets import *

# =========================
# ЭКРАН 1 — ВЫБОР КЛАВИШИ
# =========================
class KeySelectionPage(QWidget):
    def __init__(self, on_key_selected):
        super().__init__()

        # функция, которая вызовется при клике на кнопку
        self.on_key_selected = on_key_selected

        self.build_ui()

    def build_ui(self):
        # главный вертикальный layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)

        # заголовок
        title = QLabel("Выберите клавишу")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)
        main_layout.addWidget(title)

        # сетка 2x2 для кнопок
        grid = QGridLayout()
        grid.setSpacing(20)

        # создаем 4 кнопки
        for i in range(4):
            btn = QPushButton(f"Key {i + 1}")

            # размер кнопки
            btn.setMinimumSize(180, 140)


            # при клике вызываем функцию и передаем индекс кнопки
            btn.clicked.connect(lambda _, x=i: self.on_key_selected(x))

            # добавляем кнопку в сетку
            grid.addWidget(btn, i // 2, i % 2)

        # оборачиваем сетку
        grid_wrapper = QWidget()
        grid_wrapper.setLayout(grid)

        main_layout.addWidget(grid_wrapper, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)