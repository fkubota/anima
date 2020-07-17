import sys
import pandas as pd
import PyQt5.QtWidgets as QW


class WidgetExport(QW.QWidget):
    def __init__(self):
        super().__init__()

        self.lbl = QW.QLabel()
        self.table = QW.QTableWidget(0, 2)
        self.btn_export = QW.QPushButton("export labels")

        self.init_ui()
        self.init_event()

    def init_ui(self):
        self.setFixedWidth(500)
        self.lbl.setText('Positive Label (sec)')
        self.table.setHorizontalHeaderLabels(['left', 'right'])

        # layout
        hbox0 = QW.QHBoxLayout()
        hbox0.addStretch()
        hbox0.addWidget(self.btn_export)
        vbox0 = QW.QVBoxLayout()
        vbox0.addWidget(self.lbl)
        vbox0.addWidget(self.table)
        vbox0.addLayout(hbox0)
        self.setLayout(vbox0)

    def init_event(self):
        self.btn_export.clicked.connect(self.export_labels_csv)

    def add_label(self, left, right):
        n_row = self.table.rowCount()
        self.table.setRowCount(n_row+1)
        left_item = QW.QTableWidgetItem(str(left))
        right_item = QW.QTableWidgetItem(str(right))
        self.table.setItem(n_row, 0, left_item)
        self.table.setItem(n_row, 1, right_item)

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

    def export_labels_csv(self):
        # create df
        df = pd.DataFrame(columns=['left_sec', 'right_sec'])
        for column in range(self.table.columnCount()):
            column_data = []
            for row in range(self.table.rowCount()):
                item = self.table.item(row, column).text()
                item = float(item)
                column_data.append(item)
            df.iloc[:, column] = column_data

        # save
        filename = self.get_file_name()
        df.to_csv(filename, index=False)

    def get_file_name(self):
        filename, _ = QW.QFileDialog.getSaveFileName(
                        self,
                        'Save CSV',
                        filter="CSV Files (*.csv)")
        return filename


def main():
    app = QW.QApplication(sys.argv)

    w = WidgetExport()
    w.move(600, 500)
    w.add_label(2.33, 3.45)
    w.add_label(20.03984, 25.2898)
    w.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
