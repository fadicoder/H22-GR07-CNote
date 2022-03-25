from PyQt6.QtWidgets import QMainWindow, QWidget


class DrawingWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.setWindowTitle("Hand drawing")
        self.frameGeometry().setWidth()
        self.frameGeometry().setHeight()

    def launch(self):
        self.show()
