import os
from PySide6 import QtWidgets, QtGui, QtCore
from backend import WatermarkAdder, fileops
from PIL import ImageQt

class MainWindow(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.watermark_adder = WatermarkAdder()

        self.setWindowTitle("Watermark Master")
        self.resize(800, 600)

        self.setup_ui()

    def setup_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout()

        self.images_opened = False

        self.preview_label = QtWidgets.QLabel(self)
        layout.addWidget(self.preview_label)

        self.setup_images_info()
        layout.addWidget(self.images_info_label)

        self.setup_open_btn()
        layout.addWidget(self.open_btn)

        self.setup_watermark()
        layout.addLayout(self.watermark_layout)

        self.setup_rename_btn()
        layout.addWidget(self.rename_btn)

        self.setLayout(layout)

        print(self.watermark_input.size())

    def setup_images_info(self):
        self.images_info_label = QtWidgets.QLabel("total: 0", self)
        self.images_info_label.setFixedHeight(30)

    def update_images_info(self, count: int) -> None:
        self.images_info_label.setText(f"total: {count}")
        self.images_info_label.adjustSize()

    def setup_open_btn(self):
        self.open_btn = QtWidgets.QPushButton("Open Images", self)
        self.open_btn.clicked.connect(self.open_images)

    def setup_watermark(self):
        self.watermark_layout = QtWidgets.QHBoxLayout()

        self.watermark_label = QtWidgets.QLabel("watermark")
        self.watermark_layout.addWidget(self.watermark_label)

        self.watermark_input = QtWidgets.QLineEdit(self)
        self.watermark_input.setPlaceholderText("watermark")
        self.watermark_input.textChanged.connect(
            lambda: self.disabled_watermark_btns(
                not self.images_opened and self.watermark_input.text() == ""
            )
        )
        self.watermark_layout.addWidget(self.watermark_input)

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
        self.watermark_size_input.textEdited.connect(handle_watermark_size_input)
        self.watermark_layout.addWidget(self.watermark_size_input)

        self.preview_watermark_btn = QtWidgets.QPushButton("Preview", self)
        self.preview_watermark_btn.setDisabled(True)
        self.preview_watermark_btn.clicked.connect(self.preview_watermark)
        self.watermark_layout.addWidget(self.preview_watermark_btn)

        self.add_watermark_btn = QtWidgets.QPushButton("Add", self)
        self.add_watermark_btn.setDisabled(True)
        self.add_watermark_btn.clicked.connect(self.add_watermarks)
        self.watermark_layout.addWidget(self.add_watermark_btn)

    def setup_rename_btn(self):
        self.rename_btn = QtWidgets.QPushButton("Rename Images", self)
        self.rename_btn.setDisabled(True)
        self.rename_btn.clicked.connect(self.renameImages)

    def open_images(self) -> None:
        self.file_paths, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, "Select Images", "", "Image Files (*.png *.jpg *.bmp)"
        )
        if self.file_paths:
            self.preview_image(self.file_paths[0])
            self.update_images_info(len(self.file_paths))

        self.images_opened = True
        if self.watermark_input.text():
            self.disabled_watermark_btns(False)
        self.rename_btn.setDisabled(False)

    def disabled_watermark_btns(self, enabled: bool) -> None:
        self.preview_watermark_btn.setDisabled(enabled)
        self.add_watermark_btn.setDisabled(enabled)

    def preview_image(self, filePath: str) -> None:
        pixmap = QtGui.QPixmap(filePath)
        self.preview_label.setPixmap(
            pixmap.scaled(
                self.preview_label.size(),
                aspectMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            )
        )

    def preview_watermark(self):
        text = self.watermark_input.text()
        image = self.watermark_adder.apply(self.file_paths[0], text)
        pixmap = ImageQt.toqpixmap(image)
        self.preview_label.setPixmap(
            pixmap.scaled(
                self.preview_label.size(),
                aspectMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            )
        )

    def add_watermarks(self):
        text = self.watermark_input.text()
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