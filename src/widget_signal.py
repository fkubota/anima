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
        self.w_pg_signal = pg.GraphicsWindow()
        self.p_pg_signal = self.w_pg_signal.addPlot()
        # self.pg_signal = pg.ScatterPlotItem()
        self.pg_signal = self.p_pg_signal.plot(pen=('#0F8EBB50'))
        self.x = np.arange(0, 10, 0.01)
        self.y = np.sin(self.x)

        self.init_widget()
        self.update_plot()

    def init_widget(self):
        self.w_pg_signal.setBackground('#FFFFFF00')
        self.p_pg_signal.setLabel('bottom', 'Time', 'sec')
        self.p_pg_signal.showGrid(x=True, y=True, alpha=0.7)
        self.p_pg_signal.addItem(self.pg_signal)

        # layout
        self.setCentralWidget(self.w0)
        hbox0 = QW.QHBoxLayout()
        hbox0.addWidget(self.w_pg_signal)
        self.w0.setLayout(hbox0)

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
    w = SignalWidget()
    w.set_signal(data, sr)

    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
