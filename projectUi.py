import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MachineLearning Gui")
        self.setGeometry(1000, 1000, 1000, 1000)

        # QStackedWidget 생성
        self.stacked_widget = QStackedWidget()
        self.background_label = QLabel(self)

         # 배경 이미지 설정
        self.set_background_image("startBack.jpeg")

        # 레이아웃에 QStackedWidget 추가
        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)

        # QWidget을 컨테이너로 설정하고 메인 레이아웃 배치
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 배경을 맨뒤로 설정
        self.background_label.lower()

        # 페이지 생성
        # ------------------------------- 페이지 추가 시 여기서 추가하시면 됩니다!!!!!!!!
        self.start_page = startPage(self)
        self.upload_page = uploadPage(self)
        self.fChoice_page = fChoicePage(self)

        # 페이지를 QStackedWidget에 추가
        self.stacked_widget.addWidget(self.start_page)
        self.stacked_widget.addWidget(self.upload_page)
        self.stacked_widget.addWidget(self.fChoice_page)

        # 처음에는 start_page를 표시
        self.stacked_widget.setCurrentWidget(self.start_page)

        #-------------------------------------------------------------------------------

    def resizeEvent(self, event):
        # 창 크기 조정 시 배경 이미지 크기 조정
        self.background_label.setGeometry(self.rect())
        super().resizeEvent(event)

    def go_to_start_page(self):
        # start_page로 전환
        self.stacked_widget.setCurrentWidget(self.start_page)

    def go_to_upload_page(self):
        # upload_page로 전환
        self.stacked_widget.setCurrentWidget(self.upload_page)
    
    def go_to_fChoice_page(self):
        # fChoice_page로 전환
        self.stacked_widget.setCurrentWidget(self.fChoice_page)

    def set_background_image(self, image_path):
        # QLabel에 배경 이미지 설정
        pixmap = QPixmap(image_path)
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)

class startPage(QWidget): #시작페이지
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("Easy Gui MachineLearning")
        title.setFont(QFont("Arial", 24))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        nextBtn = QPushButton(text="시작하기")
        layout.addWidget(nextBtn)
        nextBtn.move(500,500)
        self.setLayout(layout)

        nextBtn.clicked.connect(self.main_window.go_to_upload_page)

class uploadPage(QWidget):  # 엑셀 업로드 페이지
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        # 업로드 영역 레이블 추가
        self.drop_area_label = QLabel("엑셀 파일을 여기로 드래그 앤 드롭하세요")
        self.drop_area_label.setAlignment(Qt.AlignCenter)
        self.drop_area_label.setFixedSize(800, 600)
        self.drop_area_label.setStyleSheet("""
            QLabel {
                border: 2px dashed red;
                font-size: 32px;
                color: black;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.drop_area_label, alignment=Qt.AlignCenter)

        # 업로드 파일명 표시 레이블
        self.uploaded_file_label = QLabel("")
        self.uploaded_file_label.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;  /* 글씨를 굵게 설정 */
                color: black;
            }
        """)
        
        layout.addWidget(self.uploaded_file_label, alignment=Qt.AlignCenter)

        # 이전 및 다음 버튼 추가
        button_layout = QHBoxLayout()
        
        prevBtn = QPushButton("이전")
        prevBtn.clicked.connect(self.main_window.go_to_start_page)
        button_layout.addWidget(prevBtn)

        nextBtn = QPushButton("다음")
        nextBtn.clicked.connect(self.main_window.go_to_fChoice_page)
        button_layout.addWidget(nextBtn)
        
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # 드래그 앤 드롭 수락
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        file_path = event.mimeData().urls()[0].toLocalFile()
        # 업로드 파일이 엑셀파일인지 확인
        if file_path.endswith(('.xls', '.xlsx', '.csv')):
            self.uploaded_file_label.setText(f"업로드된 파일: {file_path.split('/')[-1]}")
        else:
            # 엑셀파일이 아니면 경고메시지 생성
            QMessageBox.warning(self, "경고", "엑셀 파일만 업로드할 수 있습니다.")
            self.uploaded_file_label.setText("")
            
        event.acceptProposedAction()

class fChoicePage(QWidget):  # 엑셀 업로드 페이지
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # 레이아웃 설정
        layout = QVBoxLayout()

app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec_()