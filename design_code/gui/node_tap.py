from PyQt5.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout, QLabel, QProxyStyle, QStyleFactory,
    QGraphicsRectItem, QVBoxLayout, QWidget, QGraphicsItem, QGraphicsTextItem, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsScene, QGraphicsView
)
from PyQt5.QtGui import QIcon, QColor, QPen, QBrush
from PyQt5.QtCore import QSize, QPointF, Qt, QLineF


class CustomTabStyle(QProxyStyle):
    def __init__(self):
        super().__init__(QStyleFactory.create("Fusion"))

class NodeTap(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setTabBarAutoHide(False)
        self.setMovable(False)

        # 아이콘 크기 설정
        self.setIconSize(QSize(32, 32))

        # 커스텀 스타일 적용
        self.setStyleSheet("""
            QTabWidget::pane {
                margin: 0px;  /* 콘텐츠 영역 외부 여백 제거 */
                padding: 0px; /* 콘텐츠 영역 내부 여백 제거 */
            }
            QTabBar::tab {
                width: 96;
                background: #ffffff;
                margin: 4px;  /* 탭 간의 간격을 추가 */
                color: #000000;
                border: none;  /* 기본 테두리는 제거 */
            }
            QTabBar::tab:selected {
                width: 96;
                background: #ffffff;
                border: 4px solid black;  /* 검정색 테두리 추가 */
                margin: 4px;  /* 선택된 탭이 약간 더 안쪽으로 들어오도록 설정 */
                color: #000000;
            }
        """)

        # 탭 추가
        self.addTab(FileNodeTap(), QIcon("resource/file_node_tap_icon.png"), "File")
        self.addTab(VisualizationNodeTap(), QIcon("resource/visualization_node_tap_icon.png"), "Visualization")
        self.addTab(TransfromNodeTap(), QIcon("resource/transform_node_tap_icon.png"), "Transform")
        self.addTab(ModelNodeTap(), QIcon("resource/model_node_tap_icon.png"), "Model")
        self.addTab(EvaluateNodeTap(), QIcon("resource/evaluate_node_tap_icon.png"), "Evaluate")


# 개별 탭 클래스 정의
class FileNodeTap(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("File Node Tap")
        layout.addWidget(label)

        self.scene = QGraphicsScene(layout)

        self.setLayout(layout)

        self.fposition = [
            ["업로드", 60, 70], ["Node 2", 160, 70], ["Node 3", 260, 70], ["Node 4", 360, 70],
            ["Node 5", 60, 190], ["Node 6", 160, 190], ["Node 7", 260, 190], ["Node 8", 360, 190]
        ]

        # 노드 선택 패널에 노드 추가 (아이콘 및 이름 형태로 구성)
        for node_info in self.fposition:
            self.addNodeToPanel(node_info[0], QPointF(node_info[1], node_info[2]))

    def addNodeToPanel(self, text, position):
        # 패널에 노드 추가
        node = DraggableNode(0, 0, 80, 80, text)
        node.setPos(position)
        self.scene.addItem(node)

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

class ModelNodeTap(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Model Node Tap")
        layout.addWidget(label)
        self.setLayout(layout)

class EvaluateNodeTap(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Evaluate Node Tap")
        layout.addWidget(label)
        self.setLayout(layout)