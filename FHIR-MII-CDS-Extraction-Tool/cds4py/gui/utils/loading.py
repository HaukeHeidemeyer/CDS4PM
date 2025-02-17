from PyQt6.QtWidgets import QWidget, QVBoxLayout, QProgressBar

class LoadingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_bar)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

