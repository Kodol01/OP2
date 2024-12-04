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
            drop_action = drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction)
            
            if drop_action == QtCore.Qt.MoveAction:
                self.close()
            # Call reset_tab_nodes after dragging a node
            main_window = self.window()
            if isinstance(main_window, EasyMLApp):
                main_window.reset_tab_nodes()

    def enterEvent(self, event):
        main_window = self.window()
        if isinstance(main_window, EasyMLApp):
            main_window.node_description.setText(f"{self.text()} - {self.description}")

    def leaveEvent(self, event):
        main_window = self.window()
        if isinstance(main_window, EasyMLApp):
            main_window.node_description.setText("Node Description")


class NodeWithDots(DraggableButton):
    def __init__(self, description="This is a description of the node.", parent=None):
        super().__init__(parent=parent, description=description)
        self.left_dot = None
        self.right_dot = None
        self.connections = []
        self.add_dots()  # Add dots during initialization

    def add_dots(self):
        # Left red dot
        self.left_dot = Dot(self, "red")
        self.left_dot.move(-15, self.height() // 2 - 5)
        self.left_dot.show()

        # Right blue dot
        self.right_dot = Dot(self, "blue")
        self.right_dot.move(self.width() + 5, self.height() // 2 - 5)
        self.right_dot.show()

    def moveEvent(self, event):
        # Move dots when the node moves
        if self.left_dot and self.right_dot:
            self.left_dot.move(-15, self.height() // 2 - 5)
            self.right_dot.move(self.width() + 5, self.height() // 2 - 5)
        for connection in self.connections:
            connection.update_position()
        super().moveEvent(event)

    def delete_dots(self):
        if self.left_dot:
            self.left_dot.deleteLater()
            self.left_dot = None
        if self.right_dot:
            self.right_dot.deleteLater()
            self.right_dot = None

    def closeEvent(self, event):
        # Ensure dots are deleted when the node is closed
        self.delete_dots()
        super().closeEvent(event)


class Dot(QtWidgets.QWidget):
    def __init__(self, parent, color):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {color}; border-radius: 5px;")
        self.resize(10, 10)
        self.color = color
        self.parent_node = parent

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            drag = QtGui.QDrag(self)
            mime_data = QtCore.QMimeData()
            mime_data.setText(self.color)
            drag.setMimeData(mime_data)

            # Create a transparent pixmap for dragging
            pixmap = QtGui.QPixmap(self.size())
            pixmap.fill(QtCore.Qt.transparent)
            painter = QtGui.QPainter(pixmap)
            painter.setBrush(QtGui.QBrush(QtGui.QColor(self.color)))
            painter.drawEllipse(0, 0, self.width(), self.height())
            painter.end()
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())

            drop_action = drag.exec_(QtCore.Qt.CopyAction)


class ConnectionLine(QtWidgets.QWidget):
    def __init__(self, start_dot, end_dot, parent=None):
        super().__init__(parent)
        self.start_dot = start_dot
        self.end_dot = end_dot
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(parent.rect())
        self.update_position()
        self.show()

    def update_position(self):
        self.start_pos = self.start_dot.mapTo(self.parent(), self.start_dot.rect().center())
        self.end_pos = self.end_dot.mapTo(self.parent(), self.end_dot.rect().center())
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtGui.QPen(QtCore.Qt.blue, 2))
        painter.drawLine(self.start_pos, self.end_pos)


class DropWorkspace(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: white; border: 1px solid black;")
        self.nodes = []
        self.current_connection = None

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
                # Create a new node with dots
                new_node = NodeWithDots(description=source.description, parent=self)
                new_node.setText(source.text())
                new_node.setIcon(source.icon())
                new_node.setIconSize(source.iconSize())
                new_node.move(event.pos())
                new_node.show()
                self.nodes.append(new_node)
                event.setDropAction(QtCore.Qt.MoveAction)
                event.acceptProposedAction()
            elif isinstance(source, Dot):
                if source.color == "blue" and self.current_connection is None:
                    # Start a new connection
                    self.current_connection = ConnectionLine(start_dot=source, end_dot=None, parent=self)
                    self.current_connection.show()
                elif source.color == "red" and self.current_connection is not None:
                    # Complete the connection
                    self.current_connection.end_dot = source
                    self.current_connection.update_position()
                    source.parent_node.connections.append(self.current_connection)
                    self.current_connection = None
                    event.acceptProposedAction()
                else:
                    event.ignore()


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
        self.tabs = QtWidgets.QTabWidget()
        self.tab1 = self.create_tab("Tab 1")
        self.tab2 = self.create_tab("Tab 2")
        self.tab3 = self.create_tab("Tab 3")
        self.tab4 = self.create_tab("Tab 4")

        self.tabs.addTab(self.tab1, "Tab 1")
        self.tabs.addTab(self.tab2, "Tab 2")
        self.tabs.addTab(self.tab3, "Tab 3")
        self.tabs.addTab(self.tab4, "Tab 4")

        # Left panel (node icons and descriptions)
        left_panel_widget = QtWidgets.QWidget()
       
