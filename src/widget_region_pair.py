import sys
import numpy as np
import librosa
import pyqtgraph as pg
import PyQt5.QtWidgets as QW


class WidgetRegionPair(QW.QWidget):
    '''
    一方が動けば、もう一方も動くようにする
    '''
    def __init__(self, brush, pen):
        super(WidgetRegionPair, self).__init__()
        self.id = None
        self.class_ = None
        self.region0 = pg.LinearRegionItem(brush=brush, pen=pen)
        self.region1 = pg.LinearRegionItem(brush=brush, pen=pen)

        # init method
        self.init_event()

    def init_event(self):
        self.region0.sigRegionChanged.connect(self.update_pos)
        self.region1.sigRegionChanged.connect(self.update_pos)

    def set_id(self, id_):
        self.id = id_

    def set_class(self, class_):
        self.class_ = class_

    def update_pos(self):
        sender = self.sender()
        left, right = sender.getRegion()
        if sender == self.region0:
            self.region1.setRegion([left, right])
        elif sender == self.region1:
            self.region0.setRegion([left, right])


def main():
    app = QW.QApplication(sys.argv)

    filename = librosa.util.example_audio_file()
    data, sr = librosa.load(filename, sr=None)
    x = np.arange(0, len(data))/sr

    w_pg_signal = pg.GraphicsWindow()
    p_pg0 = w_pg_signal.addPlot(row=1, col=0)
    p_pg1 = w_pg_signal.addPlot(row=2, col=0)
    pg_signal0 = p_pg0.plot(pen=('#0F8EBB50'))
    pg_signal1 = p_pg1.plot(pen=('#0F8EBB50'))
    pg_signal0.setData(x, data)
    pg_signal1.setData(x, data)

    r = WidgetRegionPair(brush='AA000088', pen='AA0000AA')
    p_pg0.addItem(r.region0)
    p_pg1.addItem(r.region1)

    w_pg_signal.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
