import sys
import numpy as np
import librosa
import PyQt5.QtWidgets as QW
import pyqtgraph as pg


class SignalWidget(QW.QMainWindow):
    def __init__(self, parent=None):
        super(SignalWidget, self).__init__(parent)
        # widget
        self.w0 = QW.QWidget()


def main():
    app = QW.QApplication(sys.argv)

    filename = librosa.util.example_audio_file()
    data, sr = librosa.load(filename, sr=None)
    w = SignalWidget()
    w.set_signal(data, sr)

    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
