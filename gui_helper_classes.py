from PyQt5.QtWidgets import (
    QVBoxLayout,
    QDialog, QDialogButtonBox, QLabel, QGraphicsEllipseItem, QFileDialog, QListWidget, QListWidgetItem, QLineEdit
)
import pyqtgraph as pg
from pyqtgraph import PlotWidget
import numpy as np

from connector import LocalDatabase


def form_extractor(form, field):
    x, y = field
    return form.itemAt(x, y).widget().text()


short_nutrient_labels = ['Energy', 'Fat', 'Sat. Fat', 'Carbs', 'Sugar', 'Fiber', 'Protein', 'Salt']
long_nutrient_labels = ['Energy [kcal/100g]', 'Fat [g/100g]', '\t\tOf which are saturated fats [g/100g]',
                        'Carbs [g/100g]', '\t\tOf which is sugar [g/100g]', 'Fiber [g/100g]', 'Protein [g/100g]',
                        'Salt [g/100g]']


class NutrientPieChart(PlotWidget):
    def __init__(self, data: list[float] = None, labels: list[str] = None):
        super().__init__()
        self.setBackground('w')
        self.setXRange(0, 1.1)
        self.setYRange(0, 1.1)
        self.setAspectLocked(True)
        self.setMouseEnabled(x=False, y=False)
        self.hideButtons()

        plot = self.getPlotItem()

        plot.hideAxis('bottom')
        plot.hideAxis('left')

        if data is None:
            return

        self.reduced_data = [data[1], data[3], data[5], data[6], data[7]]
        self.reduced_labels = [labels[1], labels[3], labels[5], labels[6], labels[7]]

        self.slices = []
        self.labels = []
        self.spans = []
        self.start_angles = []
        self.colors = ['#af529f', '#2a94b6', '#ffa4b6', '#f9310e', '#1fb835']

        full_circle = 360 * 16
        start_angle = full_circle * 0.75
        norm_fac = float(1 / sum(self.reduced_data))
        for i, d in enumerate(self.reduced_data):
            p_ellipse = QGraphicsEllipseItem(0, 0, 1, 1)
            p_ellipse.setPen(pg.mkPen(255, 255, 255))
            p_ellipse.setBrush(pg.mkBrush(self.colors[i]))

            p_ellipse.setStartAngle(start_angle)
            span = d * norm_fac * full_circle
            p_ellipse.setSpanAngle(span)

            center_angle_radian = (start_angle - full_circle * 0.75 + 0.5 * span) * 2 / full_circle * np.pi

            radius = 0.4
            if span < full_circle * 0.025:
                radius = 0.55
            if span != 0:
                text = pg.TextItem(self.reduced_labels[i], (0, 0, 0), anchor=(0, 0))
                text.setPos(radius * np.sin(center_angle_radian) + 0.45, radius * np.cos(center_angle_radian) + 0.525)
                self.labels.append(text)

            self.addItem(p_ellipse)
            self.slices.append(p_ellipse)
            self.start_angles.append(start_angle)
            self.spans.append(span)

            start_angle += span

        pair_inds = [0, 1]
        self.add_colors = ['#af94ee', '#12cbff']
        self.add_labels = ['Sat. Fat', 'Sugar']

        for i, d in enumerate([data[2], data[4]]):
            p_ellipse = QGraphicsEllipseItem(0, 0, 1, 1)
            p_ellipse.setPen(pg.mkPen(255, 255, 255))
            p_ellipse.setBrush(pg.mkBrush(self.add_colors[i]))
            p_ellipse.setOpacity(0.6)

            p_ellipse.setStartAngle(self.start_angles[pair_inds[i]])
            span = d * norm_fac * full_circle
            p_ellipse.setSpanAngle(span)
            p_ellipse.setOpacity(0.4)

            center_angle_radian = (self.start_angles[
                                       pair_inds[i]] - full_circle * 0.75 + 0.5 * span) * 2 / full_circle * np.pi

            radius = 0.4
            if span < full_circle * 0.025:
                radius = 0.55
            if span != 0:
                text = pg.TextItem(self.add_labels[i], (0, 0, 0), anchor=(0, 0))
                text.setPos(radius * np.sin(center_angle_radian) + 0.45, radius * np.cos(center_angle_radian) + 0.525)
                self.labels.append(text)

            self.addItem(p_ellipse)

        for t in self.labels:
            self.addItem(t)


class RemoveDialog(QDialog):
    def __init__(self, local_database: LocalDatabase, in_name: str):
        super().__init__()
        self.db = local_database
        self.in_name = in_name
        q_btn = QDialogButtonBox.Yes | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(q_btn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Are you sure you want to permanently delete the selected ingredient?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def accept(self) -> None:
        self.db.delete_ingredient_by_name(self.in_name)
        self.close()


class ExitNow(QDialog):
    def __init__(self):
        super().__init__()

        q_btn = QDialogButtonBox.Yes | QDialogButtonBox.No

        self.buttonBox = QDialogButtonBox(q_btn)
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


class IngredientList(QListWidget):
    def __init__(self, local_database: LocalDatabase):
        super().__init__()
        self.db = local_database

        self.setSortingEnabled(True)

    def update_from_db(self):
        self.clear()
        names = self.db.get_ingredient_names()
        for name in names:
            self.addItem(QListWidgetItem(name))

    def update_from_search(self, hits: list[str]):
        self.clear()
        for name in hits:
            self.addItem(QListWidgetItem(name))


class SearchBar(QLineEdit):
    def __init__(self, local_database: LocalDatabase, ingredient_list: IngredientList):
        super().__init__()
        self.db = local_database
        self.in_list = ingredient_list

        self.setPlaceholderText('Type to search...')

    def content_changed(self):
        text = self.text().strip()
        if text == '':
            return
        hits = self.db.search_ingredients_by_name(text)
        self.in_list.update_from_search(hits=hits)

    def left_bar(self):
        if self.text() == '':
            self.in_list.update_from_db()
