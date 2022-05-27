from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QWidget, QDialog, QDialogButtonBox, QLabel, QGraphicsEllipseItem, QFileDialog
)

from connector import LocalDatabase


def form_extractor(form, field):
    x, y = field
    return form.itemAt(x, y).widget().text()


class PieChart(QWidget):
    def __init__(self, data: list[float], labels: list[str]):
        super().__init__()
        self.slices = []
        for i, d in enumerate(data):
            this_slice = QGraphicsEllipseItem()
            self.slices.append(this_slice)


class RemoveDialog(QDialog):
    def __init__(self):
        super().__init__()

        QBtn = QDialogButtonBox.Yes | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Are you sure you want to permanently delete the selected ingredient?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class ExitNow(QDialog):
    def __init__(self):
        super().__init__()

        QBtn = QDialogButtonBox.Yes | QDialogButtonBox.No

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Save before exiting?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class FileSaveDialog(QFileDialog):
    def __init__(self, local_database: LocalDatabase):
        super().__init__()
        self.db = local_database
        self.f_name = self.getSaveFileName(self, 'Save File', filter='*.txt')[0]
        if self.f_name == '':
            return
        data_name = self.f_name.split('.')[0]
        with open(self.f_name, 'w') as file:
            file.write(f'{data_name}_ingredients.csv')
        self.db.save(data_name)


class FileLoadDialog(QFileDialog):
    def __init__(self, local_database: LocalDatabase):
        super().__init__()
        self.db = local_database
        self.f_name = self.getOpenFileName(self, 'Load File', filter='*.txt')[0]
        with open(self.f_name, 'r') as file:
            in_file = file.readline()

        self.db.load([in_file])
