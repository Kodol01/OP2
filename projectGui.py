import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QVBoxLayout, QWidget, QPushButton, QGraphicsItem, QGraphicsTextItem, QGraphicsEllipseItem, QGraphicsLineItem
)
from PyQt5.QtCore import Qt, QPointF, QRectF, QPoint, QLineF
from PyQt5.QtGui import QColor, QPen, QBrush, QMouseEvent


class EasyMLWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Easy MachineLearning")
        self.setGeometry(100, 100, 2000, 1200)
        self.initUI()
        self.previous_node = None
        self.lines = []

    def initUI(self):
        # 초기 화면 설정
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        main_layout = QVBoxLayout(self.main_widget)

        # 타이틀 및 시작 버튼
        title = QLabel("Easy MachineLearning", self)
        title.setStyleSheet("font-size: 100px;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        start_btn = QPushButton("시작하기", self)
        start_btn.setStyleSheet("font-size: 40px;")
        start_btn.clicked.connect(self.showWorkspace)
        main_layout.addWidget(start_btn)

    def showWorkspace(self):
        # 워크스페이스 화면 설정
        self.main_widget.deleteLater()
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(50, 50, 1900, 1100)

        # 작업 공간 설정 (하나의 QGraphicsView로 좌우 분리된 화면 구성)
        self.view = UnifiedGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)

        # 왼쪽 1/4 부분을 사각형 선으로 분리하여 노드 선택 패널과 작업 공간을 구분
        self.left_boundary = QGraphicsRectItem(50, 50, 400, 1100)
        self.left_boundary.setPen(QPen(Qt.black, 2))  # 사각형 선 표시
        self.scene.addItem(self.left_boundary)

        self.fposition = [
            ["업로드", 60, 70], ["Node 2", 160, 70], ["Node 3", 260, 70], ["Node 4", 360, 70],
            ["Node 5", 60, 190], ["Node 6", 160, 190], ["Node 7", 260, 190], ["Node 8", 360, 190],
            ["Node 9", 60, 310], ["Node 10", 160, 310], ["Node 11", 260, 310], ["Node 12", 360, 310],
            ["Node 13", 60, 430], ["Node 14", 160, 430], ["Node 15", 260, 430], ["Node 16", 360, 430],
            ["Node 17", 60, 550], ["Node 18", 160, 550], ["Node 19", 260, 550], ["Node 20", 360, 550]
        ]

        # 노드 선택 패널에 노드 추가 (아이콘 및 이름 형태로 구성)
        for node_info in self.fposition:
            self.addNodeToPanel(node_info[0], QPointF(node_info[1], node_info[2]))

        # 작업 공간에 Start 노드 생성
        self.createStartNode()

        # 오른쪽 작업 공간 테두리 추가
        self.right_boundary = QGraphicsRectItem(450, 50, 1500, 1100)
        self.right_boundary.setPen(QPen(Qt.black, 2))  # 사각형 선 표시
        self.scene.addItem(self.right_boundary)

        # 노드 설명 영역 추가
        self.description_box = QGraphicsRectItem(50, 650, 400, 500)
        self.description_box.setPen(QPen(Qt.black, 2))
        self.scene.addItem(self.description_box)
        description_label = QGraphicsTextItem("Node Description", self.description_box)
        description_label.setPos(150, 900)

    def addNodeToPanel(self, text, position):
        # 패널에 노드 추가
        node = DraggableNode(0, 0, 80, 80, text)
        node.setPos(position)
        self.scene.addItem(node)

    def createStartNode(self):
        # 작업 공간에 Start 노드 생성
        node = DraggableNode(0, 0, 80, 80, "Start")
        node.setBrush(QBrush(QColor("lightgreen")))
        center_x = 1200 - 30  # 오른쪽 3/4 부분 중앙에 위치
        center_y = (self.scene.height() / 2) - 30
        node.setPos(center_x, center_y)
        self.scene.addItem(node)
        self.previous_node = node


class DraggableNode(QGraphicsRectItem):
    def __init__(self, x, y, width, height, label_text):
        super().__init__(x, y, width, height)

        self.setBrush(QBrush(QColor("lightblue")))
        self.setFlag(QGraphicsItem.ItemIsMovable, True)  # 드래그 가능
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)  # 선택 가능
        self.label_text = label_text

        # 텍스트 추가
        self.text_item = QGraphicsTextItem(label_text, self)
        self.text_item.setPos(width / 2 - self.text_item.boundingRect().width() / 2, height / 2 - self.text_item.boundingRect().height() / 2)

        self.setAcceptDrops(True)  # 드래그 허용
        self._drag_offset = QPointF(0, 0)  # 마우스와 노드 간의 상대적 오프셋 저장

        # 왼쪽 빨간 점 추가
        self.left_dot = QGraphicsEllipseItem(-5, height / 2, 20, 20, self)
        self.left_dot.setBrush(QBrush(QColor("red")))
        self.left_dot.setZValue(5)  # 노드 위에 보이도록 설정

        # 오른쪽 파란 점 추가
        self.right_dot = QGraphicsEllipseItem(width - 5, height / 2, 20, 20, self)
        self.right_dot.setBrush(QBrush(QColor("blue")))
        self.right_dot.setZValue(5)  # 노드 위에 보이도록 설정

        self.is_dragging_line = False
        self.temp_line = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.right_dot.contains(event.pos()):
                # 오른쪽 점 클릭 시 선 드래그 시작
                self.is_dragging_line = True
                self.temp_line = QGraphicsLineItem(QLineF(self.right_dot.sceneBoundingRect().center(), event.scenePos()))
                self.temp_line.setPen(QPen(Qt.black, 2, Qt.DashLine))
                self.scene().addItem(self.temp_line)
            else:
                # 드래그 시작
                self.setCursor(Qt.ClosedHandCursor)  # 드래그 중 커서 변경
                self._drag_offset = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_dragging_line:
            # 선 드래그 중 업데이트
            line = self.temp_line.line()
            line.setP2(event.scenePos())
            self.temp_line.setLine(line)
        elif event.buttons() == Qt.LeftButton:
            # 노드 드래그
            new_pos = self.mapToParent(event.pos() - self._drag_offset)
            scene_rect = self.scene().sceneRect()
            node_rect = self.rect()

            if new_pos.x() < scene_rect.left():
                new_pos.setX(scene_rect.left())
            elif new_pos.x() + node_rect.width() > scene_rect.right():
                new_pos.setX(scene_rect.right() - node_rect.width())

            if new_pos.y() < scene_rect.top():
                new_pos.setY(scene_rect.top())
            elif new_pos.y() + node_rect.height() > scene_rect.bottom():
                new_pos.setY(scene_rect.bottom() - node_rect.height())

            self.setPos(new_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.is_dragging_line:
            self.is_dragging_line = False
            end_items = self.scene().items(event.scenePos())
            for item in end_items:
                if isinstance(item, QGraphicsEllipseItem) and item != self.right_dot and item.parentItem() != self:
                    if item == self.left_dot:
                        # 연결 완료 - 선을 확정하고 종료
                        self.temp_line.setPen(QPen(Qt.black, 2))
                        break
            else:
                # 연결 실패 - 임시 선 삭제
                self.scene().removeItem(self.temp_line)
            self.temp_line = None
        super().mouseReleaseEvent(event)


class UnifiedGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        # 드롭된 위치에 노드 생성
        text = event.mimeData().text()
        position = self.mapToScene(event.pos())
        node = DraggableNode(0, 0, 80, 80, text)
        node.setBrush(QColor("lightblue"))
        node.setFlag(QGraphicsItem.ItemIsMovable, True)  # 드롭된 노드는 이동 가능
        node.setPos(position)

        if not self.sceneRect().contains(node.sceneBoundingRect()):
            return

        self.scene().addItem(node)
        event.acceptProposedAction()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EasyMLWindow()
    window.show()
    sys.exit(app.exec_())
