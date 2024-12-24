from PyQt5.QtWidgets import QLabel, QVBoxLayout, QDialog
from PyQt5.QtGui import QPixmap


class TestDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Icon")
        layout = QVBoxLayout(self)
        icon_label = QLabel(self)
        pixmap = QPixmap("calendar.png")
        if pixmap.isNull():
            print("Failed to load image")
        icon_label.setPixmap(pixmap)
        layout.addWidget(icon_label)


app = QApplication([])
dialog = TestDialog()
dialog.show()
app.exec_()
