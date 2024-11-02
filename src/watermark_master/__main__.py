import os
import sys
from PySide6 import QtWidgets, QtGui, QtCore
from PIL import Image, ImageDraw, ImageFont, ImageQt, ImageFile


class MainWindow(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Watermark Master")
        self.resize(800, 600)

        self.setup_ui()

    def setup_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout()

        self.preview_label = QtWidgets.QLabel(self)
        layout.addWidget(self.preview_label)

        self.btn_open = QtWidgets.QPushButton("Open Images", self)
        self.btn_open.clicked.connect(self.open_images)
        layout.addWidget(self.btn_open)

        watermark_layout = QtWidgets.QHBoxLayout()
        self.watermark_input = QtWidgets.QLineEdit(self)
        self.watermark_input.setPlaceholderText("watermark")
        watermark_layout.addWidget(self.watermark_input)

        self.btn_preview_watermark = QtWidgets.QPushButton("Preview", self)
        self.btn_preview_watermark.clicked.connect(self.preview_watermark)
        watermark_layout.addWidget(self.btn_preview_watermark)

        self.btn_add_watermark = QtWidgets.QPushButton("Add", self)
        self.btn_add_watermark.clicked.connect(self.add_watermarks)
        watermark_layout.addWidget(self.btn_add_watermark)
        layout.addLayout(watermark_layout)

        self.btn_rename = QtWidgets.QPushButton("Rename Images", self)
        self.btn_rename.clicked.connect(self.renameImages)
        layout.addWidget(self.btn_rename)

        self.setLayout(layout)


    def open_images(self) -> None:
        self.file_paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Images", "", "Image Files (*.png *.jpg *.bmp)")
        if self.file_paths:
            self.preview_image(self.file_paths[0])

    def preview_image(self, filePath: str) -> None:
        pixmap = QtGui.QPixmap(filePath)
        self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), aspectMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio))

    def preview_watermark(self):
        image = self.add_watermark(self.file_paths[0])
        pixmap  = ImageQt.toqpixmap(image)
        self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), aspectMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio))


    def add_watermark(self, img_path: str) -> ImageFile.ImageFile:
        image = Image.open(img_path)
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default(20)
        text = self.watermark_input.text()
        draw.text((10, 10), text, font=font, fill=(255, 255, 255))
        return image

    def add_watermarks(self):
        for img_path in self.file_paths:
            image = self.add_watermark(img_path)
            file_name, file_extension = self.extract_file_name_and_ext(img_path)
            new_file_name = f"{file_name}_Watermark{file_extension}"
            new_file_path = self.create_new_file_path(img_path, new_file_name)
            image.save(new_file_path)

    def extract_file_name_and_ext(self, filePath: str) -> tuple[str, str]:
        _, file_name = os.path.split(filePath)
        name, ext = os.path.splitext(file_name)
        return name, ext
    
    def create_new_file_path(self, filePath: str, newFileName: str) -> str:
        dirName, _ = os.path.split(filePath)
        newFilePath = os.path.join(dirName, newFileName)
        return newFilePath

    def renameImages(self) -> None:
        for i, file_path in enumerate(self.file_paths):
            _, ext = self.extract_file_name_and_ext(file_path)
            newFileName = f"new_name_{i}{ext}"
            newFilePath = self.create_new_file_path(file_path, newFileName)
            os.rename(file_path, newFilePath)
            self.file_paths[i] = newFilePath

def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()