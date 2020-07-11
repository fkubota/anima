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
        self.p_pg = self.w_pg_signal.addPlot()
        self.pg_signal = self.p_pg.plot(pen=('#0F8EBB50'))

        self.init_ui()

    def init_ui(self):
        self.w_pg_signal.setBackground('#FFFFFF00')
        self.p_pg.setLabel('bottom', 'Time', 'sec')
        self.p_pg.showGrid(x=True, y=True, alpha=0.7)
        self.p_pg.addItem(self.pg_signal)

        # layout
        hbox0 = QW.QHBoxLayout()
        hbox0.addWidget(self.w_pg_signal)
        self.setLayout(hbox0)

    def update_plot(self):
        self.pg_signal.setData(self.x, self.y)

    def set_signal(self, signal, sr):
        self.x = np.arange(0, len(signal))/sr
        signal = signal[::100]
        self.x = self.x[::100]
        signal = signal.astype('float16')
        self.y = signal
        self.update_plot()


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
