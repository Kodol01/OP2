from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class NodeInformation(QWidget):
    def __init__(self):
        super().__init__()
        # self.setFixedSize(480, 270)

        self.setStyleSheet("""
            QWidget {
                border: 2px solid black;  /* 테두리 두께 및 색상 */
                border-radius: 10px;     /* 둥근 테두리 반지름 */
            }
        """)

        label = QLabel("Node Information")
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)