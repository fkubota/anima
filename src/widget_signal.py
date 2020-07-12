import sys
import numpy as np
import librosa
import PyQt5.QtWidgets as QW
import pyqtgraph as pg


class WidgetSignal(QW.QWidget):
    def __init__(self, parent=None):
        super(WidgetSignal, self).__init__(parent)
        # widget
        self.w_pg_signal = pg.GraphicsWindow()
        self.p_pg0 = self.w_pg_signal.addPlot(row=1, col=0)
        self.p_pg1 = self.w_pg_signal.addPlot(row=2, col=0)
        self.pg_signal0 = self.p_pg0.plot(pen=('#0F8EBB50'))
        self.pg_signal1 = self.p_pg1.plot(pen=('#0F8EBB50'))
        self.focus_region = pg.LinearRegionItem(brush='F0EB5750', pen=None)

        self.init_ui()
        self.init_event()

    def init_ui(self):
        self.w_pg_signal.setBackground('#FFFFFF00')
        self.p_pg0.setMouseEnabled(x=False, y=False)
        self.p_pg1.setMouseEnabled(x=True, y=False)
        self.p_pg0.setLabel('bottom', 'Time', 'sec')
        self.p_pg1.setLabel('bottom', 'Time', 'sec')
        self.p_pg0.showGrid(x=True, y=True, alpha=0.7)
        self.p_pg1.showGrid(x=True, y=True, alpha=0.7)
        self.p_pg0.addItem(self.pg_signal0)
        self.p_pg1.addItem(self.pg_signal1)
        self.p_pg0.addItem(self.focus_region)
        self.focus_region.setRegion([0, 10])  # focus regionの初期化

        # layout
        hbox0 = QW.QHBoxLayout()
        hbox0.addWidget(self.w_pg_signal)
        self.setLayout(hbox0)

        # method
        self.update_focus()

    def init_event(self):
        self.p_pg1.sigRangeChanged.connect(self.update_pg1_range)
        self.focus_region.sigRegionChanged.connect(self.update_focus)

    def update_plot(self):
        self.pg_signal0.setData(self.x, self.y)
        self.pg_signal1.setData(self.x, self.y)

    def set_signal(self, signal, sr):
        self.x = np.arange(0, len(signal))/sr
        signal = signal[::100]
        self.x = self.x[::100]
        signal = signal.astype('float16')
        self.y = signal
        self.update_plot()

    def update_focus(self):
        # self.focus_region.setZValue(10)
        minX, maxX = self.focus_region.getRegion()
        self.p_pg1.setXRange(minX, maxX, padding=0)

    def update_pg1_range(self, window, view_range):
        rgn = view_range[0]
        self.focus_region.setRegion(rgn)


def main():
    app = QW.QApplication(sys.argv)

    filename = librosa.util.example_audio_file()
    data, sr = librosa.load(filename, sr=None)
    w = WidgetSignal()
    w.set_signal(data, sr)

    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
