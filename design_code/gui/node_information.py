from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class NodeInformation(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(480, 270)

        label = QLabel("Node Information")
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)