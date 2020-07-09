import sys
import librosa
import PyQt5.QtWidgets as QW
from widget_signal import SignalWidget

ICON = './../data/icon_file/'


class MainWindow(QW.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # widget
        self.w0 = QW.QWidget()
        self.w_signal = SignalWidget()
        self.le_wav_path = QW.QLineEdit()
        self.btn_plot = QW.QPushButton('plot')
        self.btn_calc = QW.QPushButton('calc')

        # event
        self.btn_plot.clicked.connect(self.clicked_btn_plot)
        # self.btn_calc.clicked.connect(self.hoge)

        # init method
        self.init_widget()

    def init_widget(self):
        # layout
        self.setCentralWidget(self.w0)
        hbox0 = QW.QHBoxLayout()
        hbox0.addWidget(self.le_wav_path)
        hbox0.addWidget(self.btn_plot)
        vbox0 = QW.QVBoxLayout()
        vbox0.addWidget(self.w_signal)
        vbox0.addLayout(hbox0)
        vbox0.addWidget(self.btn_calc)
        self.w0.setLayout(vbox0)

    def clicked_btn_plot(self):
        '''
        textboxに入力されているパスの音声ファイルをロードし、プロット
        '''
        path = self.le_wav_path.text()
        data, sr = librosa.load(path, sr=None)
        self.w_signal.set_signal(data, sr)


def main():
    app = QW.QApplication(sys.argv)

    w = MainWindow()
    filename = librosa.util.example_audio_file()
    w.le_wav_path.setText(filename)

    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
