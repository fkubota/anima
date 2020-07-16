import sys
import librosa
import PyQt5.QtWidgets as QW
from widget_signal import WidgetSignal
from widget_recommend_list import WidgetRecommendList
from widget_music_player import WidgetMusicPlayer
from widget_export import WidgetExport


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
        self.w_mp = WidgetMusicPlayer()
        self.w_export = WidgetExport()
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

        vbox1 = QW.QVBoxLayout()
        vbox1.addWidget(self.w_mp)
        vbox1.addWidget(self.w_list)

        hbox1 = QW.QHBoxLayout()
        hbox1.addLayout(vbox1)
        hbox1.addWidget(self.w_export)
        hbox1.addStretch()

        vbox2 = QW.QVBoxLayout()
        vbox2.addLayout(vbox0)
        vbox2.addLayout(hbox1)

        self.w0.setLayout(vbox2)

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

        # file load
        signal, sr = librosa.load(filename, sr=None)
        self.signal = signal
        self.sr = sr
        self.w_signal.set_signal(signal, sr)

        # set music player
        self.w_mp.set_contents(filename)

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
