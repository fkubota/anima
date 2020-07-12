import sys
# import librosa
import PyQt5.QtWidgets as QW
from widget_signal import WidgetSignal
from widget_recommend_list import WidgetRecommendList

ICON = './../data/icon_file/'


class MainWindow(QW.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.signal = 0
        self.sr = 0

        # widget
        self.w0 = QW.QWidget()
        self.w_signal = WidgetSignal()
        self.w_list = WidgetRecommendList()
        self.lbl_file = QW.QLabel('No File Chosen')
        self.btn_open = QW.QPushButton('Open')
        self.btn_recommend = QW.QPushButton('recommend')

        # event
        self.btn_open.clicked.connect(self.clicked_btn_open)

        # init method
        self.init_ui()

    def init_ui(self):
        self.resize(1400, 600)
        self.btn_open.setFixedWidth(100)

        # layout
        self.setCentralWidget(self.w0)
        hbox0 = QW.QHBoxLayout()
        hbox0.addWidget(self.btn_open)
        hbox0.addWidget(self.lbl_file)
        vbox0 = QW.QVBoxLayout()
        vbox0.addLayout(hbox0)
        vbox0.addWidget(self.w_signal)
        vbox0.addWidget(self.btn_recommend)
        vbox0.addWidget(self.w_list)
        self.w0.setLayout(vbox0)

    def clicked_btn_open(self):
        '''
        ファイルダイアログからファイルを取得
        '''
        filename, _ = QW.QFileDialog.getOpenFileName(
                        self,
                        'Open Music File',
                        filter="Audio Files (*.wav *.mp3 *.ogg)"
                        )
        self.lbl_file.setText(filename)

        # enable = False
        self.btn_open.setEnabled(False)


def main():
    app = QW.QApplication(sys.argv)

    w = MainWindow()
    w.move(300, 500)
    # filename = librosa.util.example_audio_file()
    # w.lbl_file.setText(filename)

    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
