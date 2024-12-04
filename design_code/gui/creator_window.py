from PyQt5.QtWidgets import QWidget

class CreatorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUi()
    
    def initUi(self):
        # 윈도우 제목
        self.setWindowTitle("만든이")
        # 윈도우 사이즈
        self.resize(240, 135)

        