from pathlib import Path  # Работа с путями файлов (удобно проверять расширения и имя файла)

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Импорт стилей (CSS для виджетов)
from ui.theme import (
    arrow_button_style,
    drop_area_style,
    label_style,
    outline_button_style,
    panel_style,
    preview_card_style,
    primary_button_style,
    side_button_style,
    title_style,
)


class ImageDropArea(QFrame):
    # Сигнал: отдаём наружу путь к выбранному изображению
    image_selected = Signal(str)

    def __init__(self):
        super().__init__()
        self.placeholder_icon_path = (
            Path(__file__).resolve().parent.parent / "assets" / "image_add_icon.png"
        )

        # Разрешаем drag & drop
        self.setAcceptDrops(True)

        # Курсор "указатель"
        self.setCursor(Qt.PointingHandCursor)

        # Минимальная высота зоны
        self.setMinimumHeight(240)

        # Стилизация
        self.setStyleSheet(drop_area_style())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(16)

        # Подсказка пользователю
        self.hint_label = QLabel("выберите изображение или перетащите")
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setStyleSheet(f"{label_style(size=18)} border: none; background: transparent;")
        layout.addWidget(self.hint_label)

        # Превью изображения (или placeholder)
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(150)
        self.preview_label.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.preview_label, stretch=1)

        # Текст с путём к файлу
        self.path_label = QLabel("Файл пока не выбран")
        self.path_label.setAlignment(Qt.AlignCenter)
        self.path_label.setWordWrap(True)
        self.path_label.setStyleSheet(
            f"{label_style(muted=True, size=14)} border: none; background: transparent;"
        )
        layout.addWidget(self.path_label)

        self.show_placeholder()

    def mousePressEvent(self, event):
        # Клик по области открывает диалог выбора файла
        if event.button() == Qt.LeftButton:
            self.open_file_dialog()
        super().mousePressEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent):
        # Проверяем, можно ли принять файл
        if self.extract_local_image(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        # Обработка "броска" файла
        image_path = self.extract_local_image(event)
        if image_path:
            # Отправляем сигнал наружу
            self.image_selected.emit(image_path)
            event.acceptProposedAction()
        else:
            event.ignore()

    def show_image(self, image_path: str):
        # Загружаем изображение
        pixmap = QPixmap(image_path)

        # Показываем путь
        self.path_label.setText(image_path)

        # Если не удалось загрузить картинку
        if pixmap.isNull():
            self.preview_label.setText("Файл выбран,\nно превью недоступно")
            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setStyleSheet(
                f"{title_style(28)} border: none; background: transparent;"
            )
            return

        # Масштабируем под нужный размер
        scaled = pixmap.scaled(320, 170, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Показываем превью
        self.preview_label.setText("")
        self.preview_label.setStyleSheet("background: transparent; border: none;")
        self.preview_label.setPixmap(scaled)

    def show_placeholder(self):
        placeholder = QPixmap(str(self.placeholder_icon_path))
        self.preview_label.setText("")
        self.preview_label.setStyleSheet("background: transparent; border: none;")
        self.preview_label.setPixmap(QPixmap())

        if placeholder.isNull():
            self.preview_label.setText("[]")
            self.preview_label.setStyleSheet(
                f"{title_style(62)} border: none; background: transparent;"
            )
            return

        scaled = placeholder.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_label.setPixmap(scaled)

    def open_file_dialog(self):
        # Открываем диалог выбора файла
        image_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp *.gif)",
        )

        # Если файл выбран — отправляем сигнал
        if image_path:
            self.image_selected.emit(image_path)

    @staticmethod
    def extract_local_image(event) -> str | None:
        # Достаём данные из drag/drop события
        mime_data = event.mimeData()

        # Если нет URL — это не файл
        if not mime_data.hasUrls():
            return None

        for url in mime_data.urls():
            # Нас интересуют только локальные файлы
            if not url.isLocalFile():
                continue

            local_path = url.toLocalFile()

            # Проверяем расширение файла
            if Path(local_path).suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".webp"}:
                return local_path

        return None


class KeyPicPage(QWidget):
    def __init__(self, on_back=None, on_apply=None):
        super().__init__()

        # Callback-и
        self.on_back = on_back
        self.on_apply = on_apply

        # Текущий выбранный файл
        self.selected_image_path = ""

        # Список недавно использованных изображений
        self.recent_images: list[str] = []

        # Индекс начала "страницы" в списке recent
        self.recent_start_index = 0

        # Кнопки-превью
        self.preview_cards: list[QPushButton] = []

        # Сборка UI
        self.build_ui()

    def build_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(56, 38, 56, 42)
        outer_layout.setSpacing(28)

        # -------- ВЕРХНЯЯ ПАНЕЛЬ --------
        top_bar = QHBoxLayout()

        self.back_btn = QPushButton("Назад")
        self.back_btn.setFixedSize(128, 44)
        self.back_btn.setStyleSheet(outline_button_style())
        self.back_btn.clicked.connect(self.go_back)
        top_bar.addWidget(self.back_btn, alignment=Qt.AlignLeft)

        self.title = QLabel("Выберите картинку")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet(title_style())
        top_bar.addWidget(self.title, stretch=1)
        top_bar.addSpacing(128)

        outer_layout.addLayout(top_bar)

        # -------- ОСНОВНОЙ КОНТЕНТ --------
        content_frame = QFrame()
        content_frame.setStyleSheet(panel_style())

        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(32)

        # -------- ЛЕВАЯ ПАНЕЛЬ --------
        left_panel = QVBoxLayout()
        left_panel.setSpacing(14)

        # Активная кнопка "картинка"
        self.image_btn = self.build_side_button("поменять\nкартинку", True)
        self.image_btn.clicked.connect(self.choose_image)
        left_panel.addWidget(self.image_btn)

        # Неактивная кнопка "назначение"
        self.assign_btn = self.build_side_button("поменять\nназначение", False)
        self.assign_btn.clicked.connect(self.go_back)
        left_panel.addWidget(self.assign_btn)

        left_panel.addStretch()

        # -------- ПРАВАЯ ПАНЕЛЬ --------
        right_panel = QVBoxLayout()
        right_panel.setSpacing(18)

        # Область drag & drop
        self.drop_area = ImageDropArea()
        self.drop_area.setMaximumHeight(310)

        # Подписываемся на сигнал выбора картинки
        self.drop_area.image_selected.connect(self.set_image_path)

        right_panel.addWidget(self.drop_area, 1)

        # -------- ВЫБОР ИЗ СПИСКА --------
        chooser_row = QHBoxLayout()
        chooser_row.setSpacing(10)

        list_hint = QLabel("или выберите\nиз списка")
        list_hint.setStyleSheet(label_style(muted=True, size=14))
        chooser_row.addWidget(list_hint, alignment=Qt.AlignBottom)

        # Кнопка "назад"
        self.prev_btn = QPushButton("‹")
        self.prev_btn.setFixedSize(54, 54)
        self.prev_btn.setStyleSheet(arrow_button_style())
        self.prev_btn.clicked.connect(lambda: self.shift_recent(-1))
        chooser_row.addWidget(self.prev_btn, alignment=Qt.AlignBottom)

        # Карточки превью
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        for _ in range(3):
            card = QPushButton("пусто")
            card.setFixedSize(170, 110)
            card.setStyleSheet(preview_card_style())

            # При клике выбираем изображение
            card.clicked.connect(self.select_from_recent)

            self.preview_cards.append(card)
            cards_layout.addWidget(card)

        chooser_row.addLayout(cards_layout)

        # Кнопка "вперёд"
        self.next_btn = QPushButton("›")
        self.next_btn.setFixedSize(54, 54)
        self.next_btn.setStyleSheet(arrow_button_style())
        self.next_btn.clicked.connect(lambda: self.shift_recent(1))
        chooser_row.addWidget(self.next_btn, alignment=Qt.AlignBottom)

        chooser_row.addStretch()
        right_panel.addLayout(chooser_row)

        # -------- КНОПКА ПРИМЕНИТЬ --------
        bottom_row = QHBoxLayout()
        bottom_row.addStretch()

        self.apply_btn = QPushButton("Установить")
        self.apply_btn.setFixedSize(320, 78)
        self.apply_btn.setStyleSheet(primary_button_style())
        self.apply_btn.clicked.connect(self.apply_image)

        bottom_row.addWidget(self.apply_btn)

        right_panel.addStretch(1)
        right_panel.addLayout(bottom_row)

        # Сборка layout-ов
        content_layout.addLayout(left_panel, 1)
        content_layout.addLayout(right_panel, 3)
        outer_layout.addWidget(content_frame)

        # Обновляем карточки recent
        self.refresh_recent_cards()

    def choose_image(self):
        # Открываем диалог выбора через drop_area
        self.drop_area.open_file_dialog()

    def set_image_path(self, image_path: str):
        # Сохраняем выбранный путь
        self.selected_image_path = image_path

        # Показываем превью
        self.drop_area.show_image(image_path)

        # Добавляем в recent
        self.remember_image(image_path)

    def get_image_path(self) -> str:
        return self.selected_image_path

    def apply_image(self):
        # Проверка: выбрана ли картинка
        if not self.selected_image_path:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите картинку.")
            return

        # Отправляем наружу
        if self.on_apply:
            self.on_apply(self.selected_image_path)

    def go_back(self):
        # Возврат назад
        if self.on_back:
            self.on_back()

    def shift_recent(self, delta: int):
        # Пролистывание списка recent
        if len(self.recent_images) <= len(self.preview_cards):
            return

        max_start = max(0, len(self.recent_images) - len(self.preview_cards))

        # Ограничиваем индекс
        self.recent_start_index = max(0, min(self.recent_start_index + delta, max_start))

        self.refresh_recent_cards()

    def select_from_recent(self):
        # Выбор картинки из карточки
        button = self.sender()
        if not isinstance(button, QPushButton):
            return

        image_path = button.property("image_path")

        if image_path:
            self.set_image_path(image_path)

    def refresh_recent_cards(self):
        # Обновление отображаемых карточек
        visible_items = self.recent_images[
            self.recent_start_index:self.recent_start_index + len(self.preview_cards)
        ]

        for index, card in enumerate(self.preview_cards):
            if index < len(visible_items):
                image_path = visible_items[index]

                # Сохраняем путь внутрь кнопки
                card.setProperty("image_path", image_path)

                # Показываем имя файла
                card.setText(Path(image_path).name)

                card.setEnabled(True)
            else:
                card.setProperty("image_path", "")
                card.setText("пусто")
                card.setEnabled(False)

        # Управление кнопками навигации
        has_multiple_pages = len(self.recent_images) > len(self.preview_cards)

        self.prev_btn.setEnabled(has_multiple_pages and self.recent_start_index > 0)
        self.next_btn.setEnabled(
            has_multiple_pages
            and self.recent_start_index + len(self.preview_cards) < len(self.recent_images)
        )

    def remember_image(self, image_path: str):
        # Добавляем изображение в начало списка recent
        if image_path in self.recent_images:
            self.recent_images.remove(image_path)

        self.recent_images.insert(0, image_path)

        # Сбрасываем прокрутку
        self.recent_start_index = 0

        self.refresh_recent_cards()

    @staticmethod
    def build_side_button(text: str, active: bool) -> QPushButton:
        # Универсальный метод создания кнопок слева
        button = QPushButton(text)
        button.setFixedSize(250, 96)
        button.setStyleSheet(side_button_style(active=active))
        return button
