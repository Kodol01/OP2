from PyQt5 import QtWidgets, QtGui, QtCore
import sys

class DraggableButton(QtWidgets.QPushButton):
    def __init__(self, parent=None, description="This is a description of the node."):
        super().__init__(parent)
        self.setAcceptDrops(False)
        self.description = description

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            drag = QtGui.QDrag(self)
            mime_data = QtCore.QMimeData()
            mime_data.setText(self.text())
            drag.setMimeData(mime_data)
            drag.setPixmap(self.grab())
            drag.setHotSpot(event.pos())
            transparent_pixmap = self.grab()
            transparent_pixmap.fill(QtGui.QColor(255, 255, 255, 128))
            drag.setPixmap(transparent_pixmap)
            drag.exec_(QtCore.Qt.CopyAction)

    def enterEvent(self, event):
        main_window = self.window()
        if isinstance(main_window, EasyMLApp):
            main_window.node_description.setText(f"{self.text()} - {self.description}")

    def leaveEvent(self, event):
        main_window = self.window()
        if isinstance(main_window, EasyMLApp):
            main_window.node_description.setText("Node Description")


class DropWorkspace(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: white; border: 1px solid black;")

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
        painter.setFont(QtGui.QFont("Arial", 12))
        painter.drawText(self.rect(), QtCore.Qt.AlignCenter, "Workspace")

    def dragEnterEvent(self, event):
        if event.mimeData():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData():
            source = event.source()
            if isinstance(source, DraggableButton):
                new_node = QtWidgets.QPushButton(source.text(), self)
                new_node.setIcon(source.icon())
                new_node.setIconSize(source.iconSize())
                new_node.move(event.pos())
                new_node.show()
                event.acceptProposedAction()


class EasyMLApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EASY ML")
        self.setGeometry(100, 100, 1200, 800)

        self.main_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.main_widget)

        main_layout = QtWidgets.QHBoxLayout(self.main_widget)
        left_panel_layout = QtWidgets.QVBoxLayout()
        right_workspace_layout = QtWidgets.QVBoxLayout()

        # Menu bar
        menu_bar = self.menuBar()
        menu_bar.addMenu("File")
        menu_bar.addMenu("Edit")
        menu_bar.addMenu("Node")
        menu_bar.addMenu("Help")

        # Tabs for node categories
        tabs = QtWidgets.QTabWidget()
        tab1 = self.create_tab("Tab 1")
        tab2 = self.create_tab("Tab 2")
        tab3 = self.create_tab("Tab 3")
        tab4 = self.create_tab("Tab 4")

        tabs.addTab(tab1, "Tab 1")
        tabs.addTab(tab2, "Tab 2")
        tabs.addTab(tab3, "Tab 3")
        tabs.addTab(tab4, "Tab 4")

        # Left panel (node icons and descriptions)
        left_panel_widget = QtWidgets.QWidget()
        left_panel_widget.setMaximumWidth(300)

        self.node_description = QtWidgets.QLabel("Node Description")
        self.node_description.setAlignment(QtCore.Qt.AlignCenter)
        self.node_description.setMinimumHeight(100)

        left_panel_layout.addWidget(tabs)
        left_panel_layout.addWidget(self.node_description)
        left_panel_widget.setLayout(left_panel_layout)

        # Right panel (workspace)
        self.workspace = DropWorkspace()
        right_workspace_layout.addWidget(self.workspace)

        # Add left and right panels to main layout
        main_layout.addWidget(left_panel_widget)
        main_layout.addLayout(right_workspace_layout)

    def create_tab(self, tab_name):
        tab = QtWidgets.QWidget()
        tab_layout = QtWidgets.QGridLayout()
        for i in range(5):
            for j in range(4):
                icon_button = DraggableButton(description=f"Description for {tab_name} Node {i}-{j}")
                icon_button.setText(f"Node {i}-{j}")
                icon_button.setIcon(QtGui.QIcon("resource/transform_node_tap_icon.png"))
                icon_button.setIconSize(QtCore.QSize(50, 50))
                icon_button.setMinimumHeight(80)
                tab_layout.addWidget(icon_button, i * 2, j)
                node_name_label = QtWidgets.QLabel("Node Name")
                node_name_label.setAlignment(QtCore.Qt.AlignCenter)
                tab_layout.addWidget(node_name_label, i * 2 + 1, j)
        tab.setLayout(tab_layout)
        return tab


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = EasyMLApp()
    window.show()
    sys.exit(app.exec_())
