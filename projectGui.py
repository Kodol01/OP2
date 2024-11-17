import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QGraphicsProxyWidget, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QGraphicsItem, QGraphicsTextItem
)
from PyQt5.QtCore import Qt, QPointF, QMimeData
from PyQt5.QtGui import QColor, QDrag, QPen


class EasyMLWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Easy MachineLearning")
        self.setGeometry(100, 100, 2000, 1200)
        self.initUI()

    def initUI(self):
        # 초기 화면 설정
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        main_layout = QVBoxLayout(self.main_widget)

        # 타이틀 및 시작 버튼
        title = QLabel("Easy MachineLearning", self)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        start_btn = QPushButton("시작하기", self)
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

        # 왼쪽 노드 선택 패널에 노드 추가 (아이콘 및 이름 형태로 구성)
        for i in range(5):
            for j in range(4):
                position = QPointF(60 + j * 100, 70 + i * 120)
                self.addNodeToPanel(f"Node {i * 4 + j + 1}", position)

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
        node = QGraphicsRectItem(0, 0, 80, 80)
        node.setBrush(QColor("lightgreen"))
        center_x = 1200 - 30  # 오른쪽 3/4 부분 중앙에 위치
        center_y = (self.scene.height() / 2) - 30
        node.setPos(center_x, center_y)
        self.scene.addItem(node)

        label = QLabel("Start")
        label.setAlignment(Qt.AlignCenter)
        label.setFixedSize(80, 80)
        proxy = QGraphicsProxyWidget()
        proxy.setWidget(label)
        proxy.setPos(node.pos())
        self.scene.addItem(proxy)


class DraggableNode(QGraphicsRectItem):
    def __init__(self, x, y, width, height, label_text):
        super().__init__(x, y, width, height)
        self.setBrush(QColor("lightblue"))
        self.setFlag(QGraphicsItem.ItemIsMovable, True)  # 드래그 가능
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)  # 선택 가능
        self.label_text = label_text

        # 텍스트 추가
        self.text_item = QGraphicsTextItem(label_text, self)
        self.text_item.setPos(width / 2 - self.text_item.boundingRect().width() / 2, height / 2 - self.text_item.boundingRect().height() / 2)

        self.setAcceptDrops(True)  # 드래그 허용
        self._drag_offset = QPointF(0, 0)  # 마우스와 노드 간의 상대적 오프셋 저장

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 드래그 시작
            self.setCursor(Qt.ClosedHandCursor)  # 드래그 중 커서 변경
            # 마우스 클릭 지점과 노드의 상대 위치 계산
            self._drag_offset = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # 마우스 위치를 기준으로 노드 위치 업데이트
            new_pos = self.mapToParent(event.pos() - self._drag_offset)
            self.setPos(new_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 드래그 종료 시 커서를 원래대로 복구
            self.setCursor(Qt.ArrowCursor)
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
        self.scene().addItem(node)

        event.acceptProposedAction()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EasyMLWindow()
    window.show()
    sys.exit(app.exec_())
