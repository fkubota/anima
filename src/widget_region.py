import sys
import numpy as np
import librosa
import pyqtgraph as pg
import PyQt5.QtWidgets as QW


class WidgetRegion(pg.LinearRegionItem):
    def __init__(self, brush, pen):
        super(WidgetRegion, self).__init__(brush=brush, pen=brush)
        self.id = None
        self.class_ = None

    def set_id(self, id_):
        self.id = id_

    def set_class(self, class_):
        self.class_ = class_


def main():
    app = QW.QApplication(sys.argv)

    filename = librosa.util.example_audio_file()
    data, sr = librosa.load(filename, sr=None)
    x = np.arange(0, len(data))/sr
    w_pg_signal = pg.GraphicsWindow()
    p_pg0 = w_pg_signal.addPlot()
    pg_signal0 = p_pg0.plot()
    pg_signal0.setData(x, data)
    r = WidgetRegion('test')
    r.setBrush('88000088')
    p_pg0.addItem(r)

    w_pg_signal.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
