import os
from PySide6 import QtWidgets, QtGui, QtCore
from backend import WatermarkAdder, fileops
from PIL import ImageQt
from enum import Enum


class MainWindow(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.watermark_adder = WatermarkAdder()
        self.cur_image_index = -1
        self.file_paths = []
        self.images_opened = False

        self.setWindowTitle("Watermark Master")
        self.resize(800, 600)

        self.setup_ui()

    def setup_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout()

        self.setup_preview_label()
        layout.addWidget(self.preview_label)

        self.setup_images_info()
        layout.addLayout(self.images_info_layout)

        self.setup_open_btn()
        layout.addWidget(self.open_btn)

        self.setup_watermark()
        layout.addLayout(self.watermark_layout)

        self.setup_rename_btn()
        layout.addWidget(self.rename_btn)

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
        
    def setup_images_info(self):
        class ChangeImageAction(Enum):
            prev = 1
            next = 2

        def handle_change_image(action: ChangeImageAction):
            max_index = len(self.file_paths) - 1
            if action == ChangeImageAction.prev:
                self.cur_image_index -= 1
                if self.cur_image_index < 0:
                    self.cur_image_index = max_index
            elif action == ChangeImageAction.next:
                self.cur_image_index += 1
                if self.cur_image_index > max_index:
                    self.cur_image_index = 0

            if self.check_watermark_enabled():
                self.preview_watermark()
            elif self.images_opened:
                self.preview_image()

            self.update_images_current_inedx()

        self.images_info_layout = QtWidgets.QHBoxLayout()

        self.images_total_label = QtWidgets.QLabel("total: 0", self)
        self.images_total_label.setFixedHeight(30)
        self.images_info_layout.addWidget(self.images_total_label)

        self.images_current_index_label = QtWidgets.QLabel("current: 0", self)
        self.images_info_layout.addWidget(self.images_current_index_label)

        self.prev_image_btn = QtWidgets.QPushButton("prev", self)
        self.prev_image_btn.setDisabled(True)
        self.prev_image_btn.clicked.connect(
            lambda: handle_change_image(ChangeImageAction.prev)
        )
        self.images_info_layout.addWidget(self.prev_image_btn)

        self.next_image_btn = QtWidgets.QPushButton("next", self)
        self.next_image_btn.setDisabled(True)
        self.next_image_btn.clicked.connect(
            lambda: handle_change_image(ChangeImageAction.next)
        )
        self.images_info_layout.addWidget(self.next_image_btn)
        for i in range(self.images_info_layout.count()):
            self.images_info_layout.itemAt(i).widget().setVisible(False)

    def update_images_total(self, count: int) -> None:
        self.images_total_label.setText(f"total: {count}")
        self.images_total_label.adjustSize()

    def update_images_current_inedx(self) -> None:
        self.images_current_index_label.setText(f"current: {self.cur_image_index}")

    def setup_open_btn(self):
        self.open_btn = QtWidgets.QPushButton("Open Images", self)
        self.open_btn.clicked.connect(self.open_images)

    def setup_watermark(self):
        self.watermark_layout = QtWidgets.QHBoxLayout()

        self.watermark_label = QtWidgets.QLabel("watermark")
        self.watermark_layout.addWidget(self.watermark_label)

        self.watermark_text_input = QtWidgets.QLineEdit(self)
        self.watermark_text_input.setPlaceholderText("watermark")

        def handle_watermark_text_input():
            if self.check_watermark_enabled():
                self.add_watermark_btn.setDisabled(False)
                self.preview_watermark()
            elif self.images_opened:
                self.preview_image()
                self.add_watermark_btn.setDisabled(True)

        self.watermark_text_input.textChanged.connect(handle_watermark_text_input)
        self.watermark_layout.addWidget(self.watermark_text_input)

        self.watermark_size_label = QtWidgets.QLabel("size", self)
        self.watermark_layout.addWidget(self.watermark_size_label)

        self.watermark_size_input = QtWidgets.QLineEdit(self)
        watermark_size_validator = QtGui.QDoubleValidator(
            0, 1000, 2, self.watermark_size_input
        )
        self.watermark_size_input.setValidator(watermark_size_validator)
        self.watermark_size_input.setText("20")

        def handle_watermark_size_input():
            font_size = float(self.watermark_size_input.text())
            self.watermark_adder.set_font_size(font_size)
            if self.check_watermark_enabled():
                self.preview_watermark()

        self.watermark_size_input.textEdited.connect(handle_watermark_size_input)
        self.watermark_layout.addWidget(self.watermark_size_input)

        self.add_watermark_btn = QtWidgets.QPushButton("Add", self)
        self.add_watermark_btn.setDisabled(True)
        self.add_watermark_btn.clicked.connect(self.add_watermarks)
        self.watermark_layout.addWidget(self.add_watermark_btn)

    def check_watermark_enabled(self) -> bool:
        if not self.images_opened:
            return False
        if self.watermark_text_input.text() == "":
            return False
        if self.watermark_size_input.text() == "":
            return False
        return True

    def setup_rename_btn(self):
        self.rename_btn = QtWidgets.QPushButton("Rename Images", self)
        self.rename_btn.setDisabled(True)
        self.rename_btn.clicked.connect(self.renameImages)

    def open_images(self) -> None:
        self.file_paths, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, "Select Images", "", "Image Files (*.png *.jpg *.bmp)"
        )
        if self.file_paths:
            self.cur_image_index = 0
            self.preview_image()
            self.update_images_total(len(self.file_paths))
            self.prev_image_btn.setDisabled(False)
            self.next_image_btn.setDisabled(False)

        self.images_opened = True
        if self.check_watermark_enabled():
            self.add_watermark_btn.setDisabled(False)
            self.preview_watermark()
        self.rename_btn.setDisabled(False)
        for i in range(self.images_info_layout.count()):
            self.images_info_layout.itemAt(i).widget().setVisible(True)

    def preview_image(self) -> None:
        pixmap = QtGui.QPixmap(self.file_paths[self.cur_image_index])
        self.preview_label.setPixmap(
            pixmap.scaled(
                self.preview_label.size(),
                aspectMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            )
        )

    def preview_watermark(self):
        text = self.watermark_text_input.text()
        image = self.watermark_adder.apply(self.file_paths[self.cur_image_index], text)
        pixmap = ImageQt.toqpixmap(image)
        self.preview_label.setPixmap(
            pixmap.scaled(
                self.preview_label.size(),
                aspectMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            )
        )

    def add_watermarks(self):
        text = self.watermark_text_input.text()
        for img_path in self.file_paths:
            image = self.watermark_adder.apply(img_path, text)
            file_name, file_extension = fileops.extract_file_name_and_ext(img_path)
            new_file_name = f"{file_name}_Watermark{file_extension}"
            new_file_path = fileops.create_new_file_path(img_path, new_file_name)
            image.save(new_file_path)
        QtWidgets.QMessageBox.information(self, "Add Watermark", "Successful")

    def renameImages(self) -> None:
        for i, file_path in enumerate(self.file_paths):
            _, ext = fileops.extract_file_name_and_ext(file_path)
            newFileName = f"new_name_{i}{ext}"
            newFilePath = fileops.create_new_file_path(file_path, newFileName)
            os.rename(file_path, newFilePath)
            self.file_paths[i] = newFilePath
        QtWidgets.QMessageBox.information(self, "Rename", "Successful")
