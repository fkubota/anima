import sys
import numpy as np
import librosa
import pyqtgraph as pg
import PyQt5.QtWidgets as QW


class WidgetRegion(pg.LinearRegionItem):
    def __init__(self, name):
        super(WidgetRegion, self).__init__()
        self.name = name


def main():
    app = QW.QApplication(sys.argv)

    filename = librosa.util.example_audio_file()
    data, sr = librosa.load(filename, sr=None)
    x = np.arange(0, len(data))/sr
    w_pg_signal = pg.GraphicsWindow()
    p_pg = w_pg_signal.addPlot()
    pg_signal = p_pg.plot()
    pg_signal.setData(x, data)
    r = WidgetRegion('test')
    r.setBrush('88000088')
    p_pg.addItem(r)

    w_pg_signal.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
