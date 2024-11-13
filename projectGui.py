import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QFileDialog, QGraphicsLineItem, QVBoxLayout, QWidget, QGraphicsProxyWidget, QDialog
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen

class EasyMLWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Easy MachineLearning")
        self.setGeometry(100, 100, 2400, 1400)  # 창 크기를 설정
        self.initUI()

    def initUI(self):
        # 메인 화면 위젯 설정
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # 타이틀 레이블
        title = QLabel("Easy MachineLearning")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 시작하기 버튼
        start_btn = QPushButton("시작하기")
        start_btn.clicked.connect(self.showNodesPage)
        layout.addWidget(start_btn)

    def showNodesPage(self):
        self.centralWidget().deleteLater()  # 초기 위젯 제거
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)

        # Start 노드 생성
        self.start_node = self.createNode("Start", QPointF(100, 250))

        # 시작 노드 클릭 시 업로드 노드 생성
        self.start_node.mousePressEvent = lambda event: self.createUploadNode()

    def createNode(self, text, position):
        # 노드 생성 함수
        node = QGraphicsEllipseItem(0, 0, 180, 180)
        node.setPos(position)
        self.scene.addItem(node)
        
        # 텍스트 라벨 추가
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setFixedSize(180, 180)
        proxy = QGraphicsProxyWidget()
        proxy.setWidget(label)
        proxy.setPos(position)
        self.scene.addItem(proxy)
        
        return node

    def createUploadNode(self):
        # 업로드 노드 생성
        upload_node = self.createNode("업로드", QPointF(200, 250))
        upload_node.mouseDoubleClickEvent = lambda event: self.openDragDropWindow()

    def openDragDropWindow(self):
        # 드래그앤드롭 창 생성
        self.drag_drop_window = DragDropWindow()
        self.drag_drop_window.exec_()

class DragDropWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("파일 업로드")
        self.setGeometry(300, 300, 800, 500)
        self.setAcceptDrops(True)  # 드래그앤드롭 활성화

        # 파일명 표시 레이블
        self.label = QLabel("파일을 여기에 드롭하세요.", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(50, 50, 300, 100)

        # 제출 버튼 생성 및 비활성화
        self.submit_btn = QPushButton("제출", self)
        self.submit_btn.setGeometry(150, 180, 100, 40)
        self.submit_btn.setEnabled(False)
        self.submit_btn.clicked.connect(self.submitFile)

        # 파일 경로 저장 변수
        self.file_path = ""

    def dragEnterEvent(self, event):
        # 드래그된 파일이 있을 때만 허용
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        # 드롭된 파일의 경로를 저장하고 레이블에 표시
        urls = event.mimeData().urls()
        if urls:
            self.file_path = urls[0].toLocalFile()
            self.label.setText(f"업로드된 파일: {self.file_path}")
            self.submit_btn.setEnabled(True)  # 제출 버튼 활성화

    def submitFile(self):
        # 제출 버튼 클릭 시 파일명 출력 또는 처리
        print(f"제출된 파일: {self.file_path}")
        self.close()  # 창 닫기

    def displayFileName(self, file_name):
        # 업로드 노드에 파일명 표시
        upload_label = QLabel(f"업로드: {file_name}")
        upload_label.setAlignment(Qt.AlignCenter)
        upload_label.setFixedSize(200, 30)
        upload_label.move(200, 310)
        self.scene.addWidget(upload_label)
        
        # 새 노드 생성 및 연결
        next_node = self.createNode("노드", QPointF(300, 250))
        self.drawArrow(self.scene.items()[-2], next_node)  # 이전 노드와 연결

    def drawArrow(self, start_item, end_item):
        # 두 노드 사이에 화살표 그리기
        line = QGraphicsLineItem(start_item.pos().x() + 30, start_item.pos().y() + 30,
                                 end_item.pos().x() + 30, end_item.pos().y() + 30)
        line.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        self.scene.addItem(line)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EasyMLWindow()
    window.show()
    sys.exit(app.exec_())
