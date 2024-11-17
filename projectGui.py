import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QGraphicsProxyWidget, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QGraphicsItem, QGraphicsTextItem, QGraphicsLineItem, QGraphicsPolygonItem
)
from PyQt5.QtCore import Qt, QPointF, QRectF, QTimer
from PyQt5.QtGui import QColor, QPen, QPainterPath, QBrush, QPolygonF
import math


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

        # 노드 선택 패널에 노드 추가 (아이콘 및 이름 형태로 구성)
        self.addNodeToPanel("업로드", QPointF(60, 70))
        self.addNodeToPanel("Node 2", QPointF(160, 70))
        self.addNodeToPanel("Node 3", QPointF(260, 70))
        self.addNodeToPanel("Node 4", QPointF(360, 70))
        self.addNodeToPanel("Node 5", QPointF(60, 190))
        self.addNodeToPanel("Node 6", QPointF(160, 190))
        self.addNodeToPanel("Node 7", QPointF(260, 190))
        self.addNodeToPanel("Node 8", QPointF(360, 190))
        self.addNodeToPanel("Node 9", QPointF(60, 310))
        self.addNodeToPanel("Node 10", QPointF(160, 310))
        self.addNodeToPanel("Node 11", QPointF(260, 310))
        self.addNodeToPanel("Node 12", QPointF(360, 310))
        self.addNodeToPanel("Node 13", QPointF(60, 430))
        self.addNodeToPanel("Node 14", QPointF(160, 430))
        self.addNodeToPanel("Node 15", QPointF(260, 430))
        self.addNodeToPanel("Node 16", QPointF(360, 430))
        self.addNodeToPanel("Node 17", QPointF(60, 550))
        self.addNodeToPanel("Node 18", QPointF(160, 550))
        self.addNodeToPanel("Node 19", QPointF(260, 550))
        self.addNodeToPanel("Node 20", QPointF(360, 550))

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

        # 타이머 설정: 노드 위치 변경 시 라인 업데이트
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateLines)
        self.timer.start(100)

    def addNodeToPanel(self, text, position):
        # 패널에 노드 추가
        node = DraggableNode(0, 0, 80, 80, text)
        node.setPos(position)
        self.scene.addItem(node)

    def createStartNode(self):
        # 작업 공간에 Start 노드 생성
        node = DraggableNode(0, 0, 80, 80, "Start")
        node.setBrush(QColor("lightgreen"))
        center_x = 1200 - 30  # 오른쪽 3/4 부분 중앙에 위치
        center_y = (self.scene.height() / 2) - 30
        node.setPos(center_x, center_y)
        self.scene.addItem(node)
        self.previous_node = node

    # 노드 간의 화살표 연결 추가
    def connectNode(self, node):
        if self.previous_node is not None:
            line = QGraphicsLineItem(
                self.previous_node.sceneBoundingRect().center().x(),
                self.previous_node.sceneBoundingRect().center().y(),
                node.sceneBoundingRect().center().x(),
                node.sceneBoundingRect().center().y()
            )
            pen = QPen(Qt.black, 3, Qt.SolidLine)
            pen.setCapStyle(Qt.RoundCap)
            line.setPen(pen)
            line.setZValue(-1)  # 화살표가 노드 뒤로 가지 않도록 설정
            self.scene.addItem(line)
            self.lines.append((line, self.previous_node, node))

            
        self.previous_node = node

    def updateLines(self):
        for line, start_node, end_node in self.lines:
            if isinstance(line, QGraphicsLineItem):
                line.setLine(
                    start_node.sceneBoundingRect().center().x(),
                    start_node.sceneBoundingRect().center().y(),
                    end_node.sceneBoundingRect().center().x(),
                    end_node.sceneBoundingRect().center().y()
                )
            

class DraggableNode(QGraphicsRectItem):
    def mouseDoubleClickEvent(self, event):
        if self.label_text == "업로드":
            self.showUploadWindow()
        super().mouseDoubleClickEvent(event)

    def showUploadWindow(self):
        # 파일 업로드 창 생성
        self.upload_window = QWidget()
        self.upload_window.setWindowTitle("파일 업로드")
        self.upload_window.setGeometry(200, 200, 1000, 600)
        self.upload_window.setAcceptDrops(True)
        self.upload_window.dragEnterEvent = self.dragEnterEvent
        self.upload_window.dropEvent = self.dropEvent

        layout = QVBoxLayout()
        label = QLabel("드래그앤드롭으로 파일을 업로드하세요", self.upload_window)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.upload_window.setLayout(layout)
        self.upload_window.show()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            print(f"업로드된 파일: {file_path}")
            # 파일 처리 로직 추가 가능
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
            # GUI 경계 내로만 이동하도록 제한
            scene_rect = self.scene().sceneRect()
            node_rect = self.rect()

            # X축 경계 확인
            if new_pos.x() < scene_rect.left():
                new_pos.setX(scene_rect.left())
            elif new_pos.x() + node_rect.width() > scene_rect.right():
                new_pos.setX(scene_rect.right() - node_rect.width())

            # Y축 경계 확인
            if new_pos.y() < scene_rect.top():
                new_pos.setY(scene_rect.top())
            elif new_pos.y() + node_rect.height() > scene_rect.bottom():
                new_pos.setY(scene_rect.bottom() - node_rect.height())

            self.setPos(new_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 드래그 종료 시 커서를 원래대로 복구
            self.setCursor(Qt.ArrowCursor)
            parent_window = self.scene().views()[0].parent()
            if isinstance(parent_window, EasyMLWindow):
                parent_window.connectNode(self)
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

        # 작업 공간 내에 있는지 확인
        if not self.sceneRect().contains(node.sceneBoundingRect()):
            return  # 작업 공간 밖이면 추가하지 않음

        self.scene().addItem(node)
        event.acceptProposedAction()
        parent_window = self.parent()
        if isinstance(parent_window, EasyMLWindow):
            parent_window.connectNode(node)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EasyMLWindow()
    window.show()
    sys.exit(app.exec_())
