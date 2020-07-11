import sys
import PyQt5.QtWidgets as QW


class WidgetRecommendList(QW.QWidget):
    def __init__(self, parent=None):
        super(WidgetRecommendList, self).__init__(parent)

        self.list = QW.QListWidget()
        self.btn_posi = QW.QPushButton("Positive")
        self.btn_nega = QW.QPushButton("Negative")

        self.init_ui()

    def init_ui(self):
        # widget
        self.setFixedHeight(120)

        # list
        self.list.insertItem(0, 'Region #0')
        self.list.insertItem(1, 'Region #1')
        self.list.insertItem(2, 'Region #2')
        self.list.insertItem(3, 'Region #3')
        self.list.insertItem(4, 'Region #4')

        # button
        self.btn_posi.setStyleSheet("background-color: red; color: white")
        self.btn_nega.setStyleSheet("background-color: blue; color: white")

        # layout
        vbox0 = QW.QVBoxLayout()
        vbox0.addWidget(self.btn_posi)
        vbox0.addWidget(self.btn_nega)

        hbox0 = QW.QHBoxLayout()
        hbox0.addWidget(self.list)
        hbox0.addLayout(vbox0)
        self.setLayout(hbox0)



def main():
    app = QW.QApplication(sys.argv)

    w = WidgetRecommendList()
    w.move(200, 200)
    w.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
