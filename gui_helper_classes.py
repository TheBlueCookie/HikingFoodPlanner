from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QDialog, QDialogButtonBox, QLabel, QGraphicsEllipseItem, QFileDialog, QListWidget, QListWidgetItem, QLineEdit,
    QPushButton, QSlider,
)
import pyqtgraph as pg
from pyqtgraph import PlotWidget
import numpy as np

from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator

from connector import LocalDatabase
from food_backend import LocalDatabaseComponent, Meal, Ingredient


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
        self.colors = ['#af529f', '#2a94b6', '#ffa4b6', '#f9310e', '#1fb835']
        self.extra_colors = ['#af94ee', '#12cbff']
        self.extra_labels = ['Sat. Fat', 'Sugar']

        self.setXRange(0, 1.1)
        self.setYRange(0, 1.1)
        self.setAspectLocked(True)
        self.setMouseEnabled(x=False, y=False)
        self.hideButtons()

        self.plot = self.getPlotItem()

        self.plot.hideAxis('bottom')
        self.plot.hideAxis('left')

        self.reduced_data = []
        self.reduced_labels = []
        self.slices = []
        self.labels = []
        self.spans = []
        self.start_angles = []
        self.full_circle = 360 * 16

        if data is None or sum(data) == 0:
            return
        else:
            self.update_chart(data=data, labels=labels)

    def update_chart(self, data: list[float] = None, labels: list[str] = None):
        self.plot.clear()
        if data is not None and sum(data) != 0:
            self.reduced_data = [data[1], data[3], data[5], data[6], data[7]]
            self.reduced_labels = [labels[1], labels[3], labels[5], labels[6], labels[7]]

            self.slices = []
            self.labels = []
            self.spans = []
            self.start_angles = []

            start_angle = self.full_circle * 0.75
            norm_fac = float(1 / sum(self.reduced_data))
            for i, d in enumerate(self.reduced_data):
                p_ellipse = QGraphicsEllipseItem(0, 0, 1, 1)
                p_ellipse.setPen(pg.mkPen(255, 255, 255))
                p_ellipse.setBrush(pg.mkBrush(self.colors[i]))

                p_ellipse.setStartAngle(start_angle)
                span = d * norm_fac * self.full_circle
                if np.isnan(span):
                    span = 0
                p_ellipse.setSpanAngle(span)

                center_angle_radian = (start_angle - self.full_circle * 0.75 + 0.5 * span) * 2 / self.full_circle * np.pi

                self.add_labels_to_plot(span=span, center_angle=center_angle_radian, index=i)

                self.addItem(p_ellipse)
                self.slices.append(p_ellipse)
                self.start_angles.append(start_angle)
                self.spans.append(span)

                start_angle += span

            pair_inds = [0, 1]

            for i, d in enumerate([data[2], data[4]]):
                p_ellipse = QGraphicsEllipseItem(0, 0, 1, 1)
                p_ellipse.setPen(pg.mkPen(255, 255, 255))
                p_ellipse.setBrush(pg.mkBrush(self.extra_colors[i]))
                p_ellipse.setOpacity(0.6)

                p_ellipse.setStartAngle(self.start_angles[pair_inds[i]])
                span = d * norm_fac * self.full_circle
                p_ellipse.setSpanAngle(span)
                p_ellipse.setOpacity(0.4)

                center_angle_radian = (self.start_angles[
                                           pair_inds[i]] - self.full_circle * 0.75 + 0.5 * span) * 2 / self.full_circle * np.pi

                self.add_labels_to_plot(span=span, center_angle=center_angle_radian, index=i)

                self.addItem(p_ellipse)

            for t in self.labels:
                self.addItem(t)

    def add_labels_to_plot(self, span: float, center_angle: float, index: int):
        radius = 0.4
        if span < self.full_circle * 0.025:
            radius = 0.55
        if span != 0:
            text = pg.TextItem(self.reduced_labels[index], (0, 0, 0), anchor=(0, 0))
            text.setPos(radius * np.sin(center_angle) + 0.45, radius * np.cos(center_angle) + 0.525)
            self.labels.append(text)


class RemoveDialog(QDialog):
    def __init__(self, local_database: LocalDatabase, item: LocalDatabaseComponent, msg: str, ):
        super().__init__()
        self.db = local_database
        self.item = item
        q_btn = QDialogButtonBox.Yes | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(q_btn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel(msg)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def accept(self) -> None:
        self.db.remove_item(item=self.item)
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


class ListLinkedToDatabase(QListWidget):
    def __init__(self, local_database: LocalDatabase):
        super().__init__()
        self.db = local_database
        self.setSortingEnabled(True)

    def get_db(self) -> LocalDatabase:
        return self.db

    def update_from_search(self, hits: list[str]) -> None:
        self.clear()
        for name in hits:
            self.addItem(QListWidgetItem(name))

    def get_selected_item_str(self) -> Union[str, bool]:
        selection = self.selectedItems()
        if selection:
            return selection[0].text()
        return False


class IngredientList(ListLinkedToDatabase):
    def __init__(self, local_database: LocalDatabase):
        super().__init__(local_database=local_database)

    def update_from_db(self):
        self.clear()
        names = super().get_db().get_ingredient_names()
        for name in names:
            self.addItem(QListWidgetItem(name))


class MealList(ListLinkedToDatabase):
    def __init__(self, local_database: LocalDatabase):
        super().__init__(local_database=local_database)

    def update_from_db(self):
        self.clear()
        meals = self.db.get_meal_names()
        for meal in meals:
            self.addItem(QListWidgetItem(meal))


class SearchBar(QLineEdit):
    def __init__(self, local_database: LocalDatabase, linked_list_widget: QListWidget):
        super().__init__()
        self.db = local_database
        self.linked_list = linked_list_widget

        if type(self.linked_list) is IngredientList:
            self.mode = 'ingredients'
        elif type(self.linked_list) is MealList:
            self.mode = 'meals'
        else:
            return

        self.setPlaceholderText('Type to search...')

    def content_changed(self):
        text = self.text().strip()
        if text == '':
            return
        hits = self.db.search_by_name(mode=self.mode, search_text=text)
        self.linked_list.update_from_search(hits=hits)

    def left_bar(self):
        if self.text() == '':
            self.linked_list.update_from_db()


class FilterAddRemoveButtons(QHBoxLayout):
    def __init__(self):
        super().__init__()
        self.filter_btn = QPushButton('Filter')
        self.add_btn = QPushButton('Add')
        self.remove_btn = QPushButton('Remove')

        self.addWidget(self.filter_btn)
        self.addWidget(self.add_btn)
        self.addWidget(self.remove_btn)


class LabelFieldSlider(QHBoxLayout):
    def __init__(self, label_text: str, slider_config: tuple[float, float, float]):
        super().__init__()

        self.label_text = label_text
        self.min, self.max, self.step = slider_config

        self.label = QLabel(self.label_text)
        self.edit_field = QLineEdit()
        self.edit_field.setValidator(QDoubleValidator())

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(self.min)
        self.slider.setMaximum(self.max)
        self.slider.setSingleStep(self.step)
        self.slider.setValue(self.min)

        self.addWidget(self.label, 2)
        self.addWidget(self.edit_field, 4)
        self.addWidget(self.slider, 4)

        self.slider.valueChanged.connect(self.slider_value_changed)
        self.edit_field.editingFinished.connect(self.field_value_changed)

    def slider_value_changed(self):
        self.edit_field.setText(f'{self.slider.value():.2f}')

    def field_value_changed(self):
        val = float(self.edit_field.text())
        if val < 0:
            val = 0
            self.edit_field.setText('0')
        elif val > self.max:
            self.max = val
            self.slider.setMaximum(self.max)
        elif val < self.min:
            self.min = val
            self.slider.setMinimum(self.min)

        self.slider.setValue(val)
