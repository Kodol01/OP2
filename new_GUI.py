from PyQt5 import QtWidgets, QtGui, QtCore
import sys

class DraggableButton(QtWidgets.QPushButton):
    def __init__(self, parent=None, description="This is a description of the node."):
        super().__init__(parent)
        self.setAcceptDrops(False)
        self.description = description
        self.left_dot = None
        self.right_dot = None
        self.in_workspace = False
        self.create_dots()
        self.update_dots_visibility()

    def create_dots(self):
        if self.left_dot:
            self.left_dot.deleteLater()
        if self.right_dot:
            self.right_dot.deleteLater()

        # Create left dot (red) - only accepts drops
        self.left_dot = ConnectionDot(self.parent(), is_source=False)
        self.left_dot.setStyleSheet("background-color: red; border-radius: 5px;")
        self.left_dot.setFixedSize(10, 10)
        self.left_dot.hide()
        self.left_dot.button = self  # Reference to parent button

        # Create right dot (blue) - only allows drag
        self.right_dot = ConnectionDot(self.parent(), is_source=True)
        self.right_dot.setStyleSheet("background-color: blue; border-radius: 5px;")
        self.right_dot.setFixedSize(10, 10)
        self.right_dot.hide()
        self.right_dot.button = self  # Reference to parent button

    def update_dots_visibility(self):
        if self.in_workspace and self.parent():
            if self.left_dot and self.right_dot:
                # Update positions relative to the button's position in the workspace
                button_pos = self.pos()
                self.left_dot.move(button_pos.x() - 15, button_pos.y() + self.height() // 2 - 5)
                self.right_dot.move(button_pos.x() + self.width() + 5, button_pos.y() + self.height() // 2 - 5)
                self.left_dot.raise_()
                self.right_dot.raise_()
                self.left_dot.show()
                self.right_dot.show()
        else:
            if self.left_dot and self.right_dot:
                self.left_dot.hide()
                self.right_dot.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Adjust dot positions when the button is resized
        if self.left_dot and self.right_dot:
            self.left_dot.move(-15, self.height() // 2 - 5)
            self.right_dot.move(self.width() + 5, self.height() // 2 - 5)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            # Hide dots before starting drag
            if self.left_dot:
                self.left_dot.hide()
            if self.right_dot:
                self.right_dot.hide()
            
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

    def moveEvent(self, event):
        super().moveEvent(event)
        self.update_dots_visibility()  # Update dots position when button moves

    def closeEvent(self, event):
        # Clean up dots when the button is closed
        if self.left_dot:
            self.left_dot.deleteLater()
        if self.right_dot:
            self.right_dot.deleteLater()
        super().closeEvent(event)


class ConnectionDot(QtWidgets.QLabel):
    def __init__(self, parent=None, is_source=True):
        super().__init__(parent)
        self.is_source = is_source  # True for blue (source), False for red (target)
        self.setAcceptDrops(not is_source)  # Only red dots accept drops
        self.button = None  # Reference to parent button
        self.connection_line = None

    def mousePressEvent(self, event):
        if self.is_source and event.button() == QtCore.Qt.LeftButton:
            # Only blue dots can initiate drag
            drag = QtGui.QDrag(self)
            mime_data = QtCore.QMimeData()
            mime_data.setText('connection')
            drag.setMimeData(mime_data)
            
            # Create a pixmap for the drag visual
            pixmap = QtGui.QPixmap(self.size())
            pixmap.fill(QtGui.QColor(0, 0, 255, 100))
            drag.setPixmap(pixmap)
            
            # Start position for the connection line
            self.start_pos = self.mapToParent(self.rect().center())
            
            # Execute drag
            drag.exec_(QtCore.Qt.MoveAction)

    def dragEnterEvent(self, event):
        if not self.is_source and event.mimeData().hasText():
            if event.mimeData().text() == 'connection':
                event.acceptProposedAction()

    def dropEvent(self, event):
        if not self.is_source and event.mimeData().hasText():
            if event.mimeData().text() == 'connection':
                source_dot = event.source()
                if source_dot and isinstance(source_dot, ConnectionDot):
                    # Create the connection line
                    self.create_connection(source_dot, self)
                event.acceptProposedAction()

    def create_connection(self, source_dot, target_dot):
        # Get the workspace widget
        workspace = self.parent()
        if workspace:
            # Create a new connection line
            connection = ConnectionLine(
                workspace,
                source_dot.mapToParent(source_dot.rect().center()),
                target_dot.mapToParent(target_dot.rect().center())
            )
            connection.source_dot = source_dot
            connection.target_dot = target_dot
            connection.show()
            
            # Store the connection in the workspace
            if hasattr(workspace, 'connections'):
                workspace.connections.append(connection)
            else:
                workspace.connections = [connection]


class ConnectionLine(QtWidgets.QWidget):
    def __init__(self, parent, start_pos, end_pos):
        super().__init__(parent)
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.source_dot = None
        self.target_dot = None
        self.setGeometry(0, 0, parent.width(), parent.height())
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, event):
        if self.source_dot and self.target_dot:
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
            
            # Update positions in case dots have moved
            start_pos = self.source_dot.mapToParent(self.source_dot.rect().center())
            end_pos = self.target_dot.mapToParent(self.target_dot.rect().center())
            
            painter.drawLine(start_pos, end_pos)


class DropWorkspace(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: white; border: 1px solid black;")
        self.nodes = []
        self.connections = []  # Store connection lines

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
                new_node = DraggableButton(description=source.description, parent=self)
                new_node.setText(source.text())
                new_node.setIcon(source.icon())
                new_node.setIconSize(source.iconSize())
                new_node.move(event.pos())
                new_node.in_workspace = True
                new_node.show()
                new_node.update_dots_visibility()  # Update dots visibility after showing
                self.nodes.append(new_node)
                event.setDropAction(QtCore.Qt.MoveAction)
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
        left_panel_widget.setMaximumWidth(300)

        self.node_description = QtWidgets.QLabel("Node Description")
        self.node_description.setAlignment(QtCore.Qt.AlignCenter)
        self.node_description.setMinimumHeight(100)

        left_panel_layout.addWidget(self.tabs)
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

        nodes_info = [
            {"name": "UpLoad", "description": f"Description for {tab_name} UpLoad", "row": 0, "col": 0},
            {"name": "Node 0-1", "description": f"Description for {tab_name} Node 0-1", "row": 0, "col": 1},
            {"name": "Node 0-2", "description": f"Description for {tab_name} Node 0-2", "row": 0, "col": 2},
            {"name": "Node 0-3", "description": f"Description for {tab_name} Node 0-3", "row": 0, "col": 3},
            {"name": "Node 1-0", "description": f"Description for {tab_name} Node 1-0", "row": 2, "col": 0},
            {"name": "Node 1-1", "description": f"Description for {tab_name} Node 1-1", "row": 2, "col": 1},
            {"name": "Node 1-2", "description": f"Description for {tab_name} Node 1-2", "row": 2, "col": 2},
            {"name": "Node 1-3", "description": f"Description for {tab_name} Node 1-3", "row": 2, "col": 3}
        ]

        for index, node_info in enumerate(nodes_info):
            icon_button = DraggableButton(description=node_info["description"])
            icon_button.setText(node_info["name"])
            icon_button.setIcon(QtGui.QIcon("resource/transform_node_tap_icon.png"))
            icon_button.setIconSize(QtCore.QSize(50, 50))
            icon_button.setMinimumHeight(80)
            tab_layout.addWidget(icon_button, node_info["row"], node_info["col"])
            node_name_label = QtWidgets.QLabel(node_info["name"])
            node_name_label.setAlignment(QtCore.Qt.AlignCenter)
            tab_layout.addWidget(node_name_label, node_info["row"] + 1, node_info["col"])
        
        tab.setLayout(tab_layout)
        return tab

    def reset_tab_nodes(self):
        # Remove and recreate tabs to reset nodes to their initial state
        self.tabs.clear()
        self.tab1 = self.create_tab("Tab 1")
        self.tab2 = self.create_tab("Tab 2")
        self.tab3 = self.create_tab("Tab 3")
        self.tab4 = self.create_tab("Tab 4")
        
        self.tabs.addTab(self.tab1, "Tab 1")
        self.tabs.addTab(self.tab2, "Tab 2")
        self.tabs.addTab(self.tab3, "Tab 3")
        self.tabs.addTab(self.tab4, "Tab 4")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = EasyMLApp()
    window.show()
    sys.exit(app.exec_())
