from PyQt5.QtWidgets import QLabel, QApplication
from PyQt5.QtGui import QPixmap

import sys

app = QApplication(sys.argv)
label = QLabel()
pixmap = QPixmap("./pages/profile.png")
if pixmap.isNull():
    print("Failed to load icon!")
else:
    label.setPixmap(pixmap)
label.show()
sys.exit(app.exec_())
