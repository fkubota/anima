import sys
import librosa
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
        self.le_wav_path = QW.QLineEdit()
        self.btn_plot = QW.QPushButton('plot')
        self.btn_recommend = QW.QPushButton('recommend')

        # event
        self.btn_plot.clicked.connect(self.clicked_btn_plot)

        # init method
        self.init_ui()

    def init_ui(self):
        self.resize(1400, 600)

        # layout
        self.setCentralWidget(self.w0)
        hbox0 = QW.QHBoxLayout()
        hbox0.addWidget(self.btn_plot)
        hbox0.addWidget(self.le_wav_path)
        vbox0 = QW.QVBoxLayout()
        vbox0.addLayout(hbox0)
        vbox0.addWidget(self.w_signal)
        vbox0.addWidget(self.btn_recommend)
        vbox0.addWidget(self.w_list)
        self.w0.setLayout(vbox0)

    def clicked_btn_plot(self):
        '''
        textboxに入力されているパスの音声ファイルをロードし、プロット
        '''
        path = self.le_wav_path.text()
        self.signal, self.sr = librosa.load(path, sr=None)
        self.w_signal.set_signal(self.signal, self.sr)

        # enable = False
        self.btn_plot.setEnabled(False)
        self.le_wav_path.setEnabled(False)


def main():
    app = QW.QApplication(sys.argv)

    w = MainWindow()
    w.move(300, 500)
    filename = librosa.util.example_audio_file()
    w.le_wav_path.setText(filename)

    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
