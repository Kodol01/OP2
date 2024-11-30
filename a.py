import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QPainter, QColor, QMouseEvent, QPen, QPainterPath
from PyQt5.QtCore import QRect, QPoint, Qt

class Node:
    """각 노드를 나타내는 클래스, 노드의 위치 및 연결 지점을 관리"""

    def __init__(self, rect):
        # 노드의 위치와 크기를 나타내는 QRect 객체로 초기화
        self.rect = rect

    def get_connection_point(self, point_type):
        """
        특정 위치의 연결 지점을 반환하는 함수.
        :param point_type: 연결할 점의 위치 ("left" 또는 "right")
        :return: QPoint 객체 (해당 위치의 좌표)
        """
        offset_distance = 15  # 점이 노드의 중심으로부터 떨어진 거리
        if point_type == "left":
            # 노드 왼쪽 외부의 좌표 반환 (왼쪽 연결을 위해 사용)
            return QPoint(self.rect.left() - offset_distance, self.rect.center().y())
        elif point_type == "right":
            # 노드 오른쪽 외부의 좌표 반환 (오른쪽 연결을 위해 사용)
            return QPoint(self.rect.right() + offset_distance, self.rect.center().y())

    def move(self, new_position, drag_offset):
        """
        노드를 새 위치로 이동하는 함수.
        :param new_position: 마우스 커서의 현재 위치
        :param drag_offset: 드래그 시작 시 마우스 커서와 노드 위치의 차이
        """
        # 마우스 위치에서 처음 드래그 시작 시의 오프셋을 빼서 새로운 노드 위치 계산
        self.rect.moveTopLeft(new_position - drag_offset)

    def draw(self, painter):
        """
        노드 및 연결 점을 그리는 함수.
        :param painter: QPainter 객체 (그리기 작업에 사용)
        """
        # 노드(원) 그리기 (파란색 원)
        painter.setBrush(QColor(100, 150, 200))  # 노드의 색상 설정
        painter.setPen(QColor(0, 0, 0))  # 노드 외곽선의 색상 설정 (검정색)
        painter.drawEllipse(self.rect)  # 원형 노드 그리기

        # 연결 점 그리기 (빨간색 점)
        painter.setBrush(QColor(255, 0, 0))  # 연결 점의 색상 설정
        painter.setPen(Qt.NoPen)  # 연결 점에 외곽선 없음

        # 노드의 왼쪽 및 오른쪽 연결 점 좌표 계산
        offset_distance = 15  # 점이 노드로부터 떨어진 거리
        left_point = QPoint(self.rect.left() - offset_distance, self.rect.center().y())
        right_point = QPoint(self.rect.right() + offset_distance, self.rect.center().y())

        # 왼쪽 및 오른쪽 연결 점 그리기 (반지름 5의 원형 점)
        painter.drawEllipse(left_point, 5, 5)  # 왼쪽 연결 점
        painter.drawEllipse(right_point, 5, 5)  # 오른쪽 연결 점


class CircleNodeWindow(QMainWindow):
    """노드들을 포함하고 있으며 드래그, 연결 기능을 제공하는 메인 윈도우 클래스"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Draggable Circle Nodes Example")
        self.setGeometry(100, 100, 800, 600)  # 창의 위치와 크기 설정

        # 노드들의 리스트 초기화 (각 노드는 Node 클래스의 인스턴스)
        self.nodes = [
            Node(QRect(100, 100, 100, 100)),
            Node(QRect(300, 150, 100, 100)),
            Node(QRect(500, 200, 100, 100)),
            Node(QRect(200, 300, 100, 100)),
            Node(QRect(400, 350, 100, 100))
        ]

        # 드래그 및 연결 관련 변수 초기화
        self.dragging_node = None  # 현재 드래그 중인 노드의 인덱스
        self.drag_offset = QPoint()  # 드래그 시작 시 마우스와 노드의 거리
        self.connecting = False  # 현재 연결 중인지 여부
        self.start_connection_node = None  # 연결을 시작한 노드의 인덱스
        self.connections = []  # 연결된 노드들의 정보를 저장하는 리스트 [(노드1 인덱스, 노드2 인덱스)]
        self.current_mouse_pos = None  # 마우스의 현재 위치를 저장 (연결 중인 선을 위해)

    def paintEvent(self, event):
        """
        창이 그려질 때 호출되는 함수.
        노드 및 연결된 선들을 화면에 그린다.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 반올림으로 부드러운 선 그리기 설정

        # 연결된 선 그리기 (대시 선)
        pen = QPen(QColor(100, 100, 100), 2, Qt.DashLine)  # 선의 색상, 두께, 스타일 설정
        painter.setPen(pen)

        # 각 노드 간 연결을 부드러운 곡선으로 그리기
        initial_offset_distance = 50  # 시작점에서 부드럽게 이동할 거리

        for node1_idx, node2_idx in self.connections:
            # 출발 노드의 오른쪽 연결 지점
            start = self.nodes[node1_idx].get_connection_point("right")
            # 도착 노드의 왼쪽 연결 지점
            end = self.nodes[node2_idx].get_connection_point("left")

            # QPainterPath 객체를 사용하여 부드러운 곡선 그리기
            path = QPainterPath(start)

            # 부드럽게 시작하기 위한 첫 번째 제어점
            control_point_start = QPoint(start.x() + initial_offset_distance, start.y())

            # 두 개의 제어점을 사용하여 큐비 곡선 그리기 (제어점을 통해 곡선의 형태가 결정됨)
            control_point1 = QPoint(control_point_start.x(), start.y() + (end.y() - start.y()) // 2)
            control_point2 = QPoint(end.x(), start.y() + (end.y() - start.y()) // 2)

            # 큐비 곡선을 통한 연결
            path.cubicTo(control_point1, control_point2, end)
            painter.drawPath(path)

        # 드래그 중인 연결선을 화면에 그리기
        if self.connecting and self.current_mouse_pos:
            # 출발 노드의 오른쪽 연결 지점에서 시작
            start = self.nodes[self.start_connection_node].get_connection_point("right")
            end = self.current_mouse_pos

            # QPainterPath를 사용하여 연결 선 생성
            path = QPainterPath(start)
            control_point_start = QPoint(start.x() + initial_offset_distance, start.y())

            # 부드럽게 연결되도록 제어점 설정
            control_point1 = QPoint(control_point_start.x(), start.y() + (end.y() - start.y()) // 2)
            control_point2 = QPoint(end.x(), start.y() + (end.y() - start.y()) // 2)
            path.cubicTo(control_point1, control_point2, end)
            painter.drawPath(path)

        # 각 노드를 화면에 그리기
        for node in self.nodes:
            node.draw(painter)

    def mousePressEvent(self, event: QMouseEvent):
        """
        마우스 버튼을 눌렀을 때 호출되는 함수.
        노드를 드래그하거나 연결 작업을 시작할 수 있다.
        """
        # 오른쪽 연결 점을 클릭하여 연결 시작
        for i, node in enumerate(self.nodes):
            right_point = node.get_connection_point("right")

            if (right_point - event.pos()).manhattanLength() < 10:
                # 오른쪽 연결 점을 클릭한 경우 연결을 시작
                self.connecting = True
                self.start_connection_node = i  # 연결을 시작한 노드 인덱스 저장
                self.current_mouse_pos = event.pos()  # 마우스 위치 저장
                return

        # 노드 클릭 시 드래그 시작
        for i, node in enumerate(self.nodes):
            if node.rect.contains(event.pos()) and event.button() == Qt.LeftButton:
                # 클릭된 노드를 드래그하기 시작
                self.dragging_node = i
                self.drag_offset = event.pos() - node.rect.topLeft()  # 마우스와 노드의 상대적 거리 계산
                break

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        마우스를 움직일 때 호출되는 함수.
        노드를 드래그하거나 연결 중인 선을 따라가게 한다.
        """
        # 노드를 드래그하여 이동
        if self.dragging_node is not None:
            new_position = event.pos()  # 마우스 현재 위치
            self.nodes[self.dragging_node].move(new_position, self.drag_offset)  # 노드 위치 업데이트
            self.update()  # 화면 업데이트

        # 연결 중인 선의 끝을 마우스 위치로 업데이트
        if self.connecting:
            self.current_mouse_pos = event.pos()  # 마우스 위치 업데이트
            self.update()  # 화면 업데이트

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        마우스 버튼을 뗄 때 호출되는 함수.
        드래그를 종료하거나 연결 작업을 마무리한다.
        """
        # 연결 작업 종료
        if self.connecting:
            # 왼쪽 연결 점에 도착했는지 확인
            for i, node in enumerate(self.nodes):
                left_point = node.get_connection_point("left")

                if (left_point - event.pos()).manhattanLength() < 10:
                    # 연결을 저장 (출발 노드와 도착 노드)
                    self.connections.append((self.start_connection_node, i))
                    break

            # 연결 상태 종료
            self.connecting = False
            self.start_connection_node = None
            self.current_mouse_pos = None

        # 드래그 상태 종료
        self.dragging_node = None
        self.update()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """
        마우스를 더블 클릭할 때 호출되는 함수.
        노드 설정 창을 띄운다.
        """
        for node in self.nodes:
            if node.rect.contains(event.pos()):
                # 더블 클릭된 노드에 대한 설정 창을 띄움
                self.showNodeSettingsDialog()
                break

    def showNodeSettingsDialog(self):
        """노드 설정 창을 띄우는 함수"""
        dialog = NodeSettingsDialog(self)
        dialog.exec_()


class NodeSettingsDialog(QDialog):
    """노드 설정을 위한 다이얼로그 클래스"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Node Settings")
        self.setGeometry(200, 200, 300, 200)  # 다이얼로그 창 위치와 크기 설정

        # 다이얼로그에 들어갈 레이아웃과 요소들 추가
        layout = QVBoxLayout()

        label = QLabel("This is the node settings dialog.")  # 설명 레이블 추가
        layout.addWidget(label)

        close_button = QPushButton("Close")  # 닫기 버튼 추가
        close_button.clicked.connect(self.accept)  # 버튼 클릭 시 다이얼로그 닫기
        layout.addWidget(close_button)

        self.setLayout(layout)


if __name__ == "__main__":
    # 애플리케이션 생성 및 실행
    app = QApplication(sys.argv)
    window = CircleNodeWindow()
    window.show()  # 메인 윈도우 띄우기
    sys.exit(app.exec_())