from PyQt5.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout, QLabel, QProxyStyle, QStyleFactory, QTabBar, QStylePainter, QStyleOptionTab, QStyle
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

class NodeTap(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setTabBarAutoHide(False)
        self.setMovable(False)

        # 아이콘 크기 설정
        self.setIconSize(QSize(32, 32))

        # 커스텀 스타일 적용
        self.setStyleSheet("""
            QTabWidget {
                border: 2px solid black;  /* 테두리 두께 및 색상 */
                border-radius: 10px;     /* 둥근 테두리 반지름 */
            }
        """)


        # 탭 추가
        self.addTab(FileNodeTap(), QIcon("resource/file_node_tap_icon.png"), "File")
        self.addTab(VisualizationNodeTap(), QIcon("resource/visualization_node_tap_icon.png"), "Visualization")
        self.addTab(TransfromNodeTap(), QIcon("resource/transform_node_tap_icon.png"), "Transform")
        self.addTab(LearningNodeTap(), QIcon("resource/machine_learning_icon.png"), "Learning")


# 개별 탭 클래스 정의
class FileNodeTap(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("File Node Tap")
        layout.addWidget(label)
        self.setLayout(layout)

class VisualizationNodeTap(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Visualization Node Tap")
        layout.addWidget(label)
        self.setLayout(layout)

class TransfromNodeTap(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Transform Node Tap")
        layout.addWidget(label)
        self.setLayout(layout)

class LearningNodeTap(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Learning Node Tap")
        layout.addWidget(label)
        self.setLayout(layout)