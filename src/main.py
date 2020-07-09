import sys
import librosa
import PyQt5.QtWidgets as QW
from widget_main import MainWindow


class ISedPyqt5(MainWindow):
    def __inint__(self, parent=None):
        super(ISedPyqt5, self).__init__(parent)

        self.target_region = []


def main():
    app = QW.QApplication(sys.argv)

    w = ISedPyqt5()
    filename = librosa.util.example_audio_file()
    w.le_wav_path.setText(filename)
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
