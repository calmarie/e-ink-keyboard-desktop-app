from pathlib import Path  # Работа с путями файлов (удобно проверять расширения и имя файла)

from PySide6.QtCore import QPoint, Qt, Signal, QStandardPaths
from PySide6.QtGui import (
    QColor,
    QDragEnterEvent,
    QDropEvent,
    QImage,
    QMouseEvent,
    QPainter,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QStackedWidget,
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


class DrawingCanvas(QFrame):
    TOOL_BRUSH = "brush"
    TOOL_ERASER = "eraser"
    IMAGE_WIDTH = 184
    IMAGE_HEIGHT = 88
    DISPLAY_SCALE = 2

    def __init__(self):
        super().__init__()
        self.canvas_width = self.IMAGE_WIDTH
        self.canvas_height = self.IMAGE_HEIGHT
        self.display_width = self.canvas_width * self.DISPLAY_SCALE
        self.display_height = self.canvas_height * self.DISPLAY_SCALE
        self.tool = self.TOOL_BRUSH
        self.last_point: QPoint | None = None
        self.is_drawing = False
        self.has_content = False
        self.canvas_image = QImage(
            self.canvas_width, self.canvas_height, QImage.Format_RGB32
        )
        self.canvas_image.fill(Qt.white)

        self.setFixedSize(self.display_width, self.display_height)
        self.setCursor(Qt.CrossCursor)
        self.setStyleSheet(
            """
            QFrame {
                background: white;
                border: 1px solid #505050;
                border-radius: 20px;
            }
            """
        )

    def set_tool(self, tool: str):
        self.tool = tool

    def clear_canvas(self):
        self.canvas_image.fill(Qt.white)
        self.has_content = False
        self.last_point = None
        self.update()

    def load_image(self, image_path: str) -> bool:
        source = QImage(image_path)
        if source.isNull():
            return False

        source = source.convertToFormat(QImage.Format_RGB32)
        prepared = QImage(self.canvas_width, self.canvas_height, QImage.Format_RGB32)
        prepared.fill(Qt.white)

        painter = QPainter(prepared)
        scaled = source.scaled(
            self.canvas_width,
            self.canvas_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        x = (self.canvas_width - scaled.width()) // 2
        y = (self.canvas_height - scaled.height()) // 2
        painter.drawImage(x, y, scaled)
        painter.end()

        self.canvas_image = prepared
        self.has_content = True
        self.last_point = None
        self.update()
        return True

    def export_image(self) -> QImage:
        return self.canvas_image.copy()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() != Qt.LeftButton:
            return

        self.is_drawing = True
        self.last_point = self.map_to_canvas_point(event.position().toPoint())
        self.draw_line_to(self.last_point)

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.is_drawing or not (event.buttons() & Qt.LeftButton):
            return

        current_point = self.map_to_canvas_point(event.position().toPoint())
        self.draw_line_to(current_point)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.is_drawing:
            self.draw_line_to(self.map_to_canvas_point(event.position().toPoint()))
            self.is_drawing = False
            self.last_point = None

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.drawImage(self.rect(), self.canvas_image)

    def draw_line_to(self, end_point: QPoint):
        if self.last_point is None:
            self.last_point = end_point

        painter = QPainter(self.canvas_image)
        painter.setRenderHint(QPainter.Antialiasing, True)

        if self.tool == self.TOOL_ERASER:
            color = QColor(Qt.white)
            width = 9
        else:
            color = QColor(Qt.black)
            width = 4

        pen = QPen(color, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(self.last_point, end_point)
        painter.end()

        self.last_point = end_point
        self.has_content = True
        self.update()

    def map_to_canvas_point(self, point: QPoint) -> QPoint:
        x = int(point.x() * self.canvas_width / self.display_width)
        y = int(point.y() * self.canvas_height / self.display_height)
        x = max(0, min(x, self.canvas_width - 1))
        y = max(0, min(y, self.canvas_height - 1))
        return QPoint(x, y)


class KeyPicPage(QWidget):
    def __init__(self, on_back=None, on_apply=None):
        super().__init__()
        self.on_back = on_back
        self.on_apply = on_apply
        self.selected_image_path = ""
        self.recent_images: list[str] = []
        self.recent_start_index = 0
        self.preview_cards: list[QPushButton] = []
        self.build_ui()

    def build_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(56, 38, 56, 42)
        outer_layout.setSpacing(28)

        top_bar = QHBoxLayout()

        self.back_btn = QPushButton("Назад")
        self.back_btn.setFixedSize(128, 44)
        self.back_btn.setStyleSheet(outline_button_style())
        self.back_btn.clicked.connect(self.go_back)
        top_bar.addWidget(self.back_btn, alignment=Qt.AlignLeft)

        self.title = QLabel("Выберите или нарисуйте картинку")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet(title_style())
        top_bar.addWidget(self.title, stretch=1)
        top_bar.addSpacing(128)

        outer_layout.addLayout(top_bar)

        content_frame = QFrame()
        content_frame.setStyleSheet(panel_style())

        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(32)

        left_panel = QVBoxLayout()
        left_panel.setSpacing(14)

        self.image_btn = self.build_side_button("поменять\nкартинку", True)
        self.image_btn.clicked.connect(self.choose_image)
        left_panel.addWidget(self.image_btn)

        self.assign_btn = self.build_side_button("поменять\nназначение", False)
        self.assign_btn.clicked.connect(self.go_back)
        left_panel.addWidget(self.assign_btn)
        left_panel.addStretch()

        right_panel = QVBoxLayout()
        right_panel.setSpacing(18)

        mode_row = QHBoxLayout()
        mode_row.setSpacing(10)

        self.file_mode_btn = QPushButton("Файл")
        self.file_mode_btn.setCheckable(True)
        self.file_mode_btn.setFixedSize(140, 48)
        self.file_mode_btn.clicked.connect(lambda: self.set_editor_mode("file"))
        mode_row.addWidget(self.file_mode_btn)

        self.draw_mode_btn = QPushButton("Рисовать")
        self.draw_mode_btn.setCheckable(True)
        self.draw_mode_btn.setFixedSize(140, 48)
        self.draw_mode_btn.clicked.connect(lambda: self.set_editor_mode("draw"))
        mode_row.addWidget(self.draw_mode_btn)

        mode_row.addStretch()
        right_panel.addLayout(mode_row)

        self.editor_stack = QStackedWidget()
        self.editor_stack.addWidget(self.build_file_page())
        self.editor_stack.addWidget(self.build_draw_page())
        right_panel.addWidget(self.editor_stack, 1)

        chooser_row = QHBoxLayout()
        chooser_row.setSpacing(10)

        list_hint = QLabel("или выберите\nиз списка")
        list_hint.setStyleSheet(label_style(muted=True, size=14))
        chooser_row.addWidget(list_hint, alignment=Qt.AlignBottom)

        self.prev_btn = QPushButton("‹")
        self.prev_btn.setFixedSize(54, 54)
        self.prev_btn.setStyleSheet(arrow_button_style())
        self.prev_btn.clicked.connect(lambda: self.shift_recent(-1))
        chooser_row.addWidget(self.prev_btn, alignment=Qt.AlignBottom)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        for _ in range(3):
            card = QPushButton("пусто")
            card.setFixedSize(170, 110)
            card.setStyleSheet(preview_card_style())
            card.clicked.connect(self.select_from_recent)
            self.preview_cards.append(card)
            cards_layout.addWidget(card)

        chooser_row.addLayout(cards_layout)

        self.next_btn = QPushButton("›")
        self.next_btn.setFixedSize(54, 54)
        self.next_btn.setStyleSheet(arrow_button_style())
        self.next_btn.clicked.connect(lambda: self.shift_recent(1))
        chooser_row.addWidget(self.next_btn, alignment=Qt.AlignBottom)

        chooser_row.addStretch()
        right_panel.addLayout(chooser_row)

        bottom_row = QHBoxLayout()
        bottom_row.addStretch()

        self.apply_btn = QPushButton("Установить")
        self.apply_btn.setFixedSize(320, 78)
        self.apply_btn.setStyleSheet(primary_button_style())
        self.apply_btn.clicked.connect(self.apply_image)
        bottom_row.addWidget(self.apply_btn)

        right_panel.addStretch(1)
        right_panel.addLayout(bottom_row)

        content_layout.addLayout(left_panel, 1)
        content_layout.addLayout(right_panel, 3)
        outer_layout.addWidget(content_frame)

        self.set_editor_mode("file")
        self.refresh_recent_cards()

    def build_file_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)

        self.drop_area = ImageDropArea()
        self.drop_area.setMaximumHeight(310)
        self.drop_area.image_selected.connect(self.set_image_path)
        layout.addWidget(self.drop_area)
        return page

    def build_draw_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        hint = QLabel("Рисуйте черным цветом или стирайте ластиком")
        hint.setStyleSheet(label_style(muted=True, size=15))
        layout.addWidget(hint)

        canvas_row = QHBoxLayout()
        canvas_row.setSpacing(18)

        self.draw_canvas = DrawingCanvas()
        canvas_row.addWidget(self.draw_canvas, alignment=Qt.AlignTop)

        tools_layout = QVBoxLayout()
        tools_layout.setSpacing(10)

        self.brush_btn = QPushButton("Черный")
        self.brush_btn.setFixedSize(130, 48)
        self.brush_btn.clicked.connect(lambda: self.set_draw_tool(DrawingCanvas.TOOL_BRUSH))
        tools_layout.addWidget(self.brush_btn)

        self.eraser_btn = QPushButton("Ластик")
        self.eraser_btn.setFixedSize(130, 48)
        self.eraser_btn.clicked.connect(lambda: self.set_draw_tool(DrawingCanvas.TOOL_ERASER))
        tools_layout.addWidget(self.eraser_btn)

        self.clear_canvas_btn = QPushButton("Очистить")
        self.clear_canvas_btn.setFixedSize(130, 48)
        self.clear_canvas_btn.clicked.connect(self.clear_canvas)
        tools_layout.addWidget(self.clear_canvas_btn)

        tools_layout.addStretch()
        canvas_row.addLayout(tools_layout)
        canvas_row.addStretch()

        layout.addLayout(canvas_row)
        self.set_draw_tool(DrawingCanvas.TOOL_BRUSH)
        return page

    def choose_image(self):
        self.set_editor_mode("file")
        self.drop_area.open_file_dialog()

    def set_image_path(self, image_path: str):
        self.set_editor_mode("file")
        self.selected_image_path = image_path
        self.drop_area.show_image(image_path)
        self.draw_canvas.load_image(image_path)
        self.remember_image(image_path)

    def get_image_path(self) -> str:
        return self.selected_image_path

    def apply_image(self):
        if self.editor_stack.currentIndex() == 1:
            if not self.draw_canvas.has_content:
                QMessageBox.warning(self, "Ошибка", "Сначала нарисуйте картинку.")
                return

            saved_path = self.save_drawing_to_file()
            if not saved_path:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить рисунок.")
                return

            self.selected_image_path = saved_path
            self.drop_area.show_image(saved_path)
            self.remember_image(saved_path)
        elif not self.selected_image_path:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите картинку.")
            return

        if self.on_apply:
            self.on_apply(self.selected_image_path)

    def go_back(self):
        if self.on_back:
            self.on_back()

    def shift_recent(self, delta: int):
        if len(self.recent_images) <= len(self.preview_cards):
            return

        max_start = max(0, len(self.recent_images) - len(self.preview_cards))
        self.recent_start_index = max(0, min(self.recent_start_index + delta, max_start))
        self.refresh_recent_cards()

    def select_from_recent(self):
        button = self.sender()
        if not isinstance(button, QPushButton):
            return

        image_path = button.property("image_path")
        if image_path:
            self.set_editor_mode("file")
            self.set_image_path(image_path)

    def refresh_recent_cards(self):
        visible_items = self.recent_images[
            self.recent_start_index : self.recent_start_index + len(self.preview_cards)
        ]

        for index, card in enumerate(self.preview_cards):
            if index < len(visible_items):
                image_path = visible_items[index]
                card.setProperty("image_path", image_path)
                card.setText(Path(image_path).name)
                card.setEnabled(True)
            else:
                card.setProperty("image_path", "")
                card.setText("пусто")
                card.setEnabled(False)

        has_multiple_pages = len(self.recent_images) > len(self.preview_cards)
        self.prev_btn.setEnabled(has_multiple_pages and self.recent_start_index > 0)
        self.next_btn.setEnabled(
            has_multiple_pages
            and self.recent_start_index + len(self.preview_cards) < len(self.recent_images)
        )

    def remember_image(self, image_path: str):
        if image_path in self.recent_images:
            self.recent_images.remove(image_path)

        self.recent_images.insert(0, image_path)
        self.recent_start_index = 0
        self.refresh_recent_cards()

    def set_editor_mode(self, mode: str):
        is_draw_mode = mode == "draw"
        self.editor_stack.setCurrentIndex(1 if is_draw_mode else 0)
        self.file_mode_btn.setChecked(not is_draw_mode)
        self.draw_mode_btn.setChecked(is_draw_mode)
        self.file_mode_btn.setStyleSheet(self.mode_button_style(active=not is_draw_mode))
        self.draw_mode_btn.setStyleSheet(self.mode_button_style(active=is_draw_mode))

    def set_draw_tool(self, tool: str):
        self.draw_canvas.set_tool(tool)
        is_brush = tool == DrawingCanvas.TOOL_BRUSH
        self.brush_btn.setStyleSheet(self.mode_button_style(active=is_brush))
        self.eraser_btn.setStyleSheet(self.mode_button_style(active=not is_brush))
        self.clear_canvas_btn.setStyleSheet(outline_button_style())

    def clear_canvas(self):
        self.draw_canvas.clear_canvas()

    def save_drawing_to_file(self) -> str:
        base_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        if not base_dir:
            base_dir = str(Path.home() / "AppData" / "Local" / "EInkKeyboard")

        drawings_dir = Path(base_dir) / "drawings"
        drawings_dir.mkdir(parents=True, exist_ok=True)

        existing_indices = []
        for item in drawings_dir.glob("drawing_*.png"):
            suffix = item.stem.replace("drawing_", "")
            if suffix.isdigit():
                existing_indices.append(int(suffix))

        next_index = max(existing_indices, default=0) + 1
        image_path = drawings_dir / f"drawing_{next_index:03}.png"
        saved = self.draw_canvas.export_image().save(str(image_path), "PNG")
        return str(image_path) if saved else ""

    @staticmethod
    def build_side_button(text: str, active: bool) -> QPushButton:
        button = QPushButton(text)
        button.setFixedSize(250, 96)
        button.setStyleSheet(side_button_style(active=active))
        return button

    @staticmethod
    def mode_button_style(active: bool) -> str:
        return primary_button_style() if active else outline_button_style()
