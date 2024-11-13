import os
from PySide6 import QtWidgets, QtGui, QtCore
from backend import WatermarkAdder, fileops
from PIL import ImageQt, ImageFile
from enum import Enum


class ImageNavigator(Enum):
    PREVIOUS = 1
    NEXT = 2


class WatermarkManager:
    def __init__(self, watermark_adder: WatermarkAdder) -> None:
        self.watermark_adder = watermark_adder
        self.text = ""
        self.font_size = 20
        self.font_color = "#ffffff"

    def set_text(self, text: str) -> None:
        self.text = text

    def set_font_size(self, size: float) -> None:
        self.font_size = size
        self.watermark_adder.set_font_size(size)

    def set_font_color(self, color: str) -> None:
        self.font_color = color
        self.watermark_adder.set_font_color(color)

    def is_enabled(self) -> bool:
        return bool(self.text) and bool(self.font_size) and bool(self.font_color)

    def apply_to_image(self, image_path: str) -> ImageFile.ImageFile:
        return self.watermark_adder.apply(image_path, self.text)


class ImageRenamer:
    def __init__(self, template="{num}{ext}") -> None:
        self.template = template

    def set_template(self, template: str) -> None:
        if not template.endswith("{ext}"):
            template += "{ext}"
        self.template = template

    def rename(self, file_paths: list[str]) -> list[str]:
        new_file_paths: list[str] = []
        for i, file_path in enumerate(file_paths):
            _, ext = fileops.extract_file_name_and_ext(file_path)
            new_file_name = self.template.format(num=i, ext=ext)
            new_file_path = fileops.create_new_file_path(file_path, new_file_name)
            new_file_paths.append(new_file_path)
            os.rename(file_path, new_file_path)
        return new_file_paths


class MainWindow(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.init_ui()
        self.image_navigator = ImageNavigator
        self.watermark_manager = WatermarkManager(WatermarkAdder())
        self.image_renamer = ImageRenamer()
        self.current_image_index = -1
        self.file_paths = []
        self.images_opened = False

    def init_ui(self) -> None:
        self.setWindowTitle("Watermark Master")
        self.resize(800, 600)
        self.setup_layout()

    def setup_layout(self):
        layout = QtWidgets.QVBoxLayout()
        self.setup_preview_label()
        layout.addWidget(self.preview_label)
        self.setup_images_info()
        layout.addLayout(self.images_info_layout)
        self.setup_navigation_bar()
        layout.addLayout(self.navigation_bar_layout)
        self.setup_watermark()
        layout.addLayout(self.watermark_layout)
        self.setup_rename()
        layout.addLayout(self.rename_layout)
        self.setLayout(layout)

    def setup_preview_label(self):
        self.preview_label = QtWidgets.QLabel("NONE", self)
        self.preview_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(64)
        font.setBold(True)
        font.setItalic(True)
        self.preview_label.setFont(font)
        self.preview_label.setStyleSheet("color: #A9A9A9")

    def preview_image(self) -> None:
        pixmap = QtGui.QPixmap(self.file_paths[self.current_image_index])
        self.preview_label.setPixmap(
            pixmap.scaled(
                self.preview_label.size(),
                aspectMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            )
        )

    def update_image_preview(self):
        if self.images_opened and self.watermark_manager.is_enabled():
            self.preview_watermark()
        elif self.images_opened:
            self.preview_image()

    def preview_watermark(self):
        image = self.watermark_manager.apply_to_image(
            self.file_paths[self.current_image_index]
        )
        pixmap = ImageQt.toqpixmap(image)
        self.preview_label.setPixmap(
            pixmap.scaled(
                self.preview_label.size(),
                aspectMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            )
        )

    def navigate_images(self, direction: ImageNavigator):
        max_index = len(self.file_paths) - 1
        if direction == self.image_navigator.PREVIOUS:
            self.current_image_index = (self.current_image_index - 1) % (max_index + 1)
        elif direction == self.image_navigator.NEXT:
            self.current_image_index = (self.current_image_index + 1) % (max_index + 1)
        self.update_image_preview()
        self.update_images_current_inedx()

    def setup_images_info(self):
        self.images_info_layout = QtWidgets.QHBoxLayout()

        self.images_total_label = QtWidgets.QLabel("total: 0", self)
        self.images_total_label.setFixedHeight(30)
        self.images_info_layout.addWidget(self.images_total_label)

        self.images_current_index_label = QtWidgets.QLabel("current: 0", self)
        self.images_current_index_label.setFixedHeight(30)
        self.images_info_layout.addWidget(self.images_current_index_label)

        for i in range(self.images_info_layout.count()):
            self.images_info_layout.itemAt(i).widget().setVisible(False)

    def update_images_total(self, count: int) -> None:
        self.images_total_label.setText(f"total: {count}")
        self.images_total_label.adjustSize()

    def update_images_current_inedx(self) -> None:
        self.images_current_index_label.setText(f"current: {self.current_image_index}")

    def setup_navigation_bar(self) -> None:
        self.navigation_bar_layout = QtWidgets.QHBoxLayout()

        self.open_btn = QtWidgets.QPushButton("open", self)
        self.open_btn.clicked.connect(self.open_images)
        self.navigation_bar_layout.addWidget(self.open_btn)

        self.add_btn = QtWidgets.QPushButton("add", self)
        self.add_btn.clicked.connect(self.add_images)
        self.add_btn.setDisabled(True)
        self.navigation_bar_layout.addWidget(self.add_btn)

        self.prev_image_btn = QtWidgets.QPushButton("prev", self)
        self.prev_image_btn.setDisabled(True)
        self.prev_image_btn.clicked.connect(
            lambda: self.navigate_images(self.image_navigator.PREVIOUS)
        )
        self.navigation_bar_layout.addWidget(self.prev_image_btn)

        self.next_image_btn = QtWidgets.QPushButton("next", self)
        self.next_image_btn.setDisabled(True)
        self.next_image_btn.clicked.connect(
            lambda: self.navigate_images(self.image_navigator.NEXT)
        )
        self.navigation_bar_layout.addWidget(self.next_image_btn)

    def setup_watermark(self):
        self.watermark_layout = QtWidgets.QGridLayout()

        self.watermark_label = QtWidgets.QLabel("watermark")
        self.watermark_layout.addWidget(self.watermark_label, 0, 0, 1, 1)

        self.watermark_text_input = QtWidgets.QLineEdit(self)
        self.watermark_text_input.setPlaceholderText("watermark")

        def handle_watermark_text_input():
            self.watermark_manager.set_text(self.watermark_text_input.text())
            if self.images_opened and self.watermark_manager.is_enabled():
                self.add_watermark_btn.setDisabled(False)
                self.preview_watermark()
            elif self.images_opened:
                self.preview_image()
                self.add_watermark_btn.setDisabled(True)

        self.watermark_text_input.textChanged.connect(handle_watermark_text_input)
        self.watermark_layout.addWidget(self.watermark_text_input, 0, 1, 1, 2)

        self.watermark_size_label = QtWidgets.QLabel("size", self)
        self.watermark_layout.addWidget(self.watermark_size_label, 0, 3, 1, 1)

        self.watermark_size_input = QtWidgets.QLineEdit(self)
        self.watermark_size_input.setText("20")

        def handle_watermark_size_input():
            size_str = self.watermark_size_input.text()
            if not size_str:
                self.watermark_manager.set_font_size(0)
                self.add_watermark_btn.setDisabled(True)
                self.preview_image()
                return
            font_size = float(size_str)
            self.watermark_manager.set_font_size(font_size)
            if self.images_opened and self.watermark_manager.is_enabled():
                self.add_watermark_btn.setDisabled(False)
                self.preview_watermark()

        self.watermark_size_input.textEdited.connect(handle_watermark_size_input)
        self.watermark_layout.addWidget(self.watermark_size_input, 0, 4, 1, 2)

        self.watermark_color_label = QtWidgets.QLabel("color", self)
        self.watermark_layout.addWidget(self.watermark_color_label, 1, 0, 1, 1)

        self.watermark_color_input = QtWidgets.QLineEdit(self)
        self.watermark_color_input.setText("#ffffff")

        def handle_watermark_color_input():
            color = self.watermark_color_input.text()
            self.watermark_manager.set_font_color(color)
            if self.images_opened and self.watermark_manager.is_enabled():
                self.add_watermark_btn.setDisabled(False)
                self.preview_watermark()
            elif self.images_opened:
                self.preview_image()
                self.add_watermark_btn.setDisabled(True)

        self.watermark_color_input.textChanged.connect(handle_watermark_color_input)
        self.watermark_layout.addWidget(self.watermark_color_input, 1, 1, 1, 2)

        self.add_watermark_btn = QtWidgets.QPushButton("Add", self)
        self.add_watermark_btn.setDisabled(True)
        self.add_watermark_btn.clicked.connect(self.add_watermarks)
        self.watermark_layout.addWidget(self.add_watermark_btn, 2, 0, 1, 6)

    def setup_rename(self):
        self.rename_layout = QtWidgets.QHBoxLayout()

        self.rename_template_label = QtWidgets.QLabel("template", self)
        self.rename_layout.addWidget(self.rename_template_label)

        self.rename_template_input = QtWidgets.QLineEdit(self)
        self.rename_template_input.setText("{num}")

        def handle_rename_input():
            template = self.rename_template_input.text()
            self.image_renamer.set_template(template)
            if self.images_opened and template:
                self.rename_btn.setDisabled(False)
            else:
                self.rename_btn.setDisabled(True)

        self.rename_template_input.textChanged.connect(handle_rename_input)
        self.rename_layout.addWidget(self.rename_template_input)

        self.rename_btn = QtWidgets.QPushButton("Rename", self)
        self.rename_btn.setDisabled(True)
        self.rename_btn.clicked.connect(self.rename_images)
        self.rename_layout.addWidget(self.rename_btn)

    def open_images(self) -> None:
        self.file_paths, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, "Select Images", "", "Image Files (*.png *.jpg *.bmp)"
        )
        if self.file_paths:
            self.current_image_index = 0
            self.preview_image()
            self.update_images_total(len(self.file_paths))
            self.add_btn.setDisabled(False)
            self.prev_image_btn.setDisabled(False)
            self.next_image_btn.setDisabled(False)

        self.images_opened = True
        if self.watermark_manager.is_enabled():
            self.add_watermark_btn.setDisabled(False)
            self.preview_watermark()
        self.rename_btn.setDisabled(False)
        for i in range(self.images_info_layout.count()):
            self.images_info_layout.itemAt(i).widget().setVisible(True)

    def add_images(self) -> None:
        file_paths, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, "Select Images", "", "Image Files (*.png *.jpg *.bmp)"
        )
        if file_paths:
            self.file_paths = self.file_paths + [
                item for item in file_paths if item not in set(self.file_paths)
            ]
            self.update_images_total(len(self.file_paths))

    def add_watermarks(self):
        for img_path in self.file_paths:
            image = self.watermark_manager.apply_to_image(img_path)
            file_name, file_extension = fileops.extract_file_name_and_ext(img_path)
            new_file_name = f"{file_name}_Watermark{file_extension}"
            new_file_path = fileops.create_new_file_path(img_path, new_file_name)
            image.save(new_file_path)
        QtWidgets.QMessageBox.information(self, "Add Watermark", "Successful")

    def rename_images(self) -> None:
        self.file_paths = self.image_renamer.rename(self.file_paths)
        QtWidgets.QMessageBox.information(self, "Rename", "Successful")
