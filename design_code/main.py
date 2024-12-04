import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    # 애플리케이션 객체 생성
    app = QApplication(sys.argv)

    # MainWindow 객체 생성 및 실행
    main_window = MainWindow()
    main_window.show()

    # 애플리케이션 이벤트 루프 실행
    sys.exit(app.exec_())

# 메인 실행 진입점 설정
if __name__ == "__main__":
    main()
