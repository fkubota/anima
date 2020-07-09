import sys
import librosa
import PyQt5.QtWidgets as QW
import pyqtgraph as pg
from widget_main import MainWindow


class ISedPyqt5(MainWindow):
    def __init__(self, parent=None):
        super(ISedPyqt5, self).__init__(parent)
        print('h')

        # region
        self.target_region_l = 0
        self.target_region_r = 2
        self.target_region = pg.LinearRegionItem(brush='DAFF3720')

        # event
        self.target_region.sigRegionChanged.connect(self.update_target_region)
        self.btn_calc.clicked.connect(self.calc)

        # init method
        self.init_gui()

    def init_gui(self):
        self.w_signal.p_pg_signal.addItem(self.target_region)

    def update_target_region(self):
        print('\n--- update_target_region')
        region = self.sender()
        left, right = region.getRegion()
        self.target_region_l = left
        self.target_region_r = right

    def calc(self):
        print('\n--- calc')


def main():
    app = QW.QApplication(sys.argv)

    w = ISedPyqt5()
    filename = librosa.util.example_audio_file()
    w.le_wav_path.setText(filename)
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
