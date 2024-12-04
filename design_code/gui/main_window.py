from PyQt5.QtWidgets import QMainWindow, QAction, QWidget, QHBoxLayout, QVBoxLayout, qApp
from PyQt5.QtCore import Qt
from gui.creator_window import CreatorWindow
from gui.node_tap import NodeTap
from gui.work_space import WorkSpace
from gui.node_information import NodeInformation

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUi()
    
    def initUi(self):
        # 윈도우 제목
        self.setWindowTitle("비개발자를 위한 GUI 기반 머신 러닝 프로그램")
        self.resize(1920, 1080)

        # 메뉴바 생성
        self.menubar = self.menuBar()
        self.menubar.setNativeMenuBar(False)

        self.info_menu = self.menubar.addMenu("정보")
        self.file_menu = self.menubar.addMenu("파일")

        self.creator_action = QAction("만든이", self)
        self.save_action = QAction("저장", self)
        self.load_action = QAction("불러오기", self)
        self.exit_action = QAction("닫기", self)

        self.info_menu.addAction(self.creator_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.load_action)
        self.file_menu.addAction(self.exit_action)

        self.exit_action.triggered.connect(qApp.quit)

        self.creator_window = None
        self.creator_action.triggered.connect(self.show_creator_window)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 메인 레이아웃
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)

        # 왼쪽 영역
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        left_widget.setLayout(left_layout)

        # NodeTap 추가
        node_tab = NodeTap()
        left_layout.addWidget(node_tab)

        node_information = NodeInformation()
        left_layout.addWidget(node_information)

        # 오른쪽 영역
        work_space = WorkSpace()
        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(work_space, 3)

    def show_creator_window(self):
        if self.creator_window is None:
            self.creator_window = CreatorWindow()
            self.creator_window.show()
        else:
            self.creator_window.activateWindow()