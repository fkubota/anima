import sys
import PyQt5.QtWidgets as QW


class WidgetRecommendList(QW.QWidget):
    def __init__(self, parent=None):
        super(WidgetRecommendList, self).__init__(parent)

        self.list = QW.QListWidget()
        self.btn_posi = QW.QPushButton("Positive")
        self.btn_nega = QW.QPushButton("Negative")
        self.btn_find = QW.QPushButton("Find Similar Regions")

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
        self.btn_posi.setStyleSheet("background-color: blue; color: white")
        self.btn_nega.setStyleSheet("background-color: red; color: white")
        self.btn_find.setStyleSheet("background-color: orange; color: white")
        self.btn_find.setSizePolicy(QW.QSizePolicy.Minimum,
                                    QW.QSizePolicy.Expanding)
        self.btn_posi.clicked.connect(self.clicked_btn_posi_nega)
        self.btn_nega.clicked.connect(self.clicked_btn_posi_nega)

        # layout
        vbox0 = QW.QVBoxLayout()
        vbox0.addWidget(self.btn_posi)
        vbox0.addWidget(self.btn_nega)

        hbox0 = QW.QHBoxLayout()
        hbox0.addWidget(self.list)
        hbox0.addLayout(vbox0)
        hbox0.addWidget(self.btn_find)
        self.setLayout(hbox0)

    def clicked_btn_posi_nega(self):
        sender = self.sender()
        row = self.list.currentRow()
        if sender == self.btn_posi:
            text = f'Region #{row} ---> Positive'
            self.list.item(row).setText(text)
        elif sender == self.btn_nega:
            text = f'Region #{row} ---> Negative'
            self.list.item(row).setText(text)


def main():
    app = QW.QApplication(sys.argv)

    w = WidgetRecommendList()
    w.move(600, 500)
    w.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
