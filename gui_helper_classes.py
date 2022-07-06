from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QDialog, QDialogButtonBox, QLabel, QGraphicsEllipseItem, QFileDialog, QListWidget, QListWidgetItem, QLineEdit,
    QPushButton, QSlider, QCheckBox, QScrollArea, QWidget, QFrame, QSizePolicy, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QLayout
)
import pyqtgraph as pg
from pyqtgraph import PlotWidget
import numpy as np

from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QColor

from connector import LocalDatabase
from error_handling import ItemUsedElsewhereError
from food_backend import LocalDatabaseComponent, MealType, Meal, Ingredient
from trip_backend import Trip


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

                center_angle_radian = (
                                              start_angle - self.full_circle * 0.75 + 0.5 * span) * 2 / self.full_circle * np.pi

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

                center_angle_radian = (self.start_angles[pair_inds[
                    i]] - self.full_circle * 0.75 + 0.5 * span) * 2 / self.full_circle * np.pi

                self.add_labels_to_plot(span=span, center_angle=center_angle_radian, index=i, mode='extra')

                self.addItem(p_ellipse)

            for t in self.labels:
                self.addItem(t)

    def add_labels_to_plot(self, span: float, center_angle: float, index: int, mode: str = 'standard'):
        radius = 0.4
        if mode == 'extra':
            lab = self.extra_labels
        elif mode == 'standard':
            lab = self.reduced_labels
        else:
            return
        if span < self.full_circle * 0.025:
            radius = 0.55
        if span != 0:
            text = pg.TextItem(lab[index], (0, 0, 0), anchor=(0, 0))
            text.setPos(radius * np.sin(center_angle) + 0.45, radius * np.cos(center_angle) + 0.525)
            self.labels.append(text)


class RemoveDialog(QDialog):
    def __init__(self, local_database: LocalDatabase, item: LocalDatabaseComponent, msg: str):
        super().__init__()
        self.db = local_database
        self.item = item
        q_btn = QDialogButtonBox.Yes | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(q_btn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.message = QLabel(msg)
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def accept(self) -> None:
        try:
            self.db.remove_item(item=self.item)
            self.close()
        except ItemUsedElsewhereError:
            self.message.setText(f'Cannot remove {self.item.name} since it is used somewhere!')


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
            file.write(f'{data_name}_ingredients.csv\n')
            file.write(f'{data_name}_meals.csv')
        self.db.save(data_name)


class FileLoadDialog(QFileDialog):
    def __init__(self, local_database: LocalDatabase):
        super().__init__()
        self.db = local_database
        self.f_name = self.getOpenFileName(self, 'Load File', filter='*.txt')[0]
        with open(self.f_name, 'r') as file:
            file_paths = file.read().splitlines()

        self.db.load(file_paths)


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

    def update_from_db(self):
        self.clear()
        names = super().get_db().get_ingredient_names()
        for name in names:
            self.addItem(QListWidgetItem(name))

    def mark_ingredients_in_meal(self, meal: Meal):
        items = [self.item(i) for i in range(self.count())]
        meal_names = meal.get_all_ingredient_names()
        for i, item in enumerate(items):
            if item.text() in meal_names:
                item.setBackground(QColor('#daffda'))
            else:
                item.setBackground(QColor('white'))


class MealList(ListLinkedToDatabase):

    def update_from_db(self):
        self.clear()
        meals = self.db.get_meal_names()
        for meal in meals:
            self.addItem(QListWidgetItem(meal))


class SearchBar(QLineEdit):
    def __init__(self, local_database: LocalDatabase, linked_list_widget: Union[MealList, IngredientList]):
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
    def __init__(self, filter_only=False):
        super().__init__()
        self.filter_btn = QPushButton('Filter')
        if not filter_only:
            self.add_btn = QPushButton('Add')
            self.remove_btn = QPushButton('Remove')

        self.addWidget(self.filter_btn)
        if not filter_only:
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


class TypeSelectionCheckBoxes(QHBoxLayout):
    def __init__(self, local_database: LocalDatabase):
        super().__init__()
        self.db = local_database

        self.type_selection_boxes = []
        for i in self.db.meal_types:
            self.type_selection_boxes.append(QCheckBox(i.name))
            self.addWidget(self.type_selection_boxes[-1])

    def get_selected_types(self) -> list[MealType]:
        selection = []
        for i, box in enumerate(self.type_selection_boxes):
            if box.isChecked():
                selection.append(self.db.num_to_meal_type(i))

        return selection


class DayOverview(QScrollArea):
    def __init__(self, local_database: LocalDatabase, trip: Trip):
        super().__init__()
        self.db = local_database
        self.trip = trip

        self.setWidgetResizable(True)

        self.super_widget = QWidget()
        self.super_layout = QHBoxLayout()

        self.days = []
        self.shadow_days = QListWidget()

        self.super_widget.setLayout(self.super_layout)
        self.setWidget(self.super_widget)

        for i in range(self.trip.duration):
            self.add_day(init_mode=True)

    def single_day_clicked(self, sender: int):
        current_selection = self.shadow_days.selectedIndexes()
        if current_selection:
            current_day = current_selection[0].row()
            print('sender', sender, 'current', current_day)
            if current_day != sender:
                self.shadow_days.setCurrentRow(sender)
                self.days[current_day].deselected()

    def add_day(self, init_mode: bool = False):
        if init_mode:
            check = True
        else:
            check = self.trip.add_day()

        if check:
            ind = len(self.days)
            self.days.append(SingleDay(day_overview=self, index=ind))
            self.shadow_days.addItem(QListWidgetItem(f'shadow_item_{ind:03d}'))
            if ind > 0:
                self.super_layout.addWidget(QVSeparationLine())
            self.super_layout.addWidget(self.days[-1])
            if ind == 0:
                self.shadow_days.setCurrentRow(0)

    def update_view(self):
        day_ind = self.get_current_day()
        if day_ind is not None:
            self.days[day_ind].update_details_list()

    def get_current_day(self):
        current_selection = self.shadow_days.selectedIndexes()
        if current_selection:
            return current_selection[0].row()
        else:
            return None


class SingleDay(QWidget):
    def __init__(self, day_overview: DayOverview, index: int):
        super().__init__()
        self.day_overview = day_overview
        self.index = index

        self.setMinimumWidth(200)

        self.super_layout = QVBoxLayout()

        self.header = QPushButton(f'Day {self.index + 1}')
        self.header.setStyleSheet('QPushButton {border: none}')

        self.header.clicked.connect(self.selected)

        self.details_list = QListWidget()
        self.details_list.setStyleSheet('QListWidget {border: none}')

        self.super_layout.addWidget(self.header)
        self.super_layout.addWidget(self.details_list)

        self.setLayout(self.super_layout)

    def selected(self):
        self.setStyleSheet('QPushButton {background-color: blue}')
        self.day_overview.single_day_clicked(sender=self.index)

    def deselected(self):
        self.setStyleSheet('QPushButton {background-color: none}')

    def update_details_list(self):
        self.details_list.clear()
        meal_types = self.day_overview.db.get_meal_type_names()

        for i, meal in enumerate(self.day_overview.trip.meal_plan[self.index].values()):
            if meal is not None:
                self.details_list.addItem(QListWidgetItem(f'{meal_types[i]}: {meal.name}'))


class QVSeparationLine(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(20)
        self.setMinimumHeight(1)
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)


class DayViewMealInfo(QWidget):
    def __init__(self, local_database: LocalDatabase, trip: Trip, meal_type: MealType, day_ind: Union[int, None]):
        super().__init__()
        self.db = local_database
        self.trip = trip
        self.day_ind = day_ind
        self.meal_type = meal_type

        self.super_layout = QVBoxLayout()

        self.header_layout = QHBoxLayout()
        self.type_label = QLabel(f'{meal_type.name}:')
        self.add_remove_btn = QPushButton()

        self.header_layout.addWidget(self.type_label)
        self.header_layout.addWidget(self.add_remove_btn)

        self.meal_name = QLabel()

        self.meal_short_info_layout = QHBoxLayout()
        self.cal_label = QLabel()
        self.weight_label = QLabel()
        self.cost_label = QLabel()

        self.meal_short_info_layout.addWidget(self.cal_label)
        self.meal_short_info_layout.addWidget(self.weight_label)
        self.meal_short_info_layout.addWidget(self.cost_label)

        self.update_info()

        self.super_layout.addLayout(self.header_layout)
        self.super_layout.addWidget(self.meal_name)
        self.super_layout.addLayout(self.meal_short_info_layout)

        self.setLayout(self.super_layout)

    def update_info(self):
        if self.day_ind is not None:
            meal = self.trip.meal_plan[self.day_ind][self.meal_type.CODE]
            if meal is None:
                self.meal_name.setText('')
                self.add_remove_btn.setText('Add meal')
                self.cal_label.setText('-- kcal')
                self.weight_label.setText('-- g')
                self.cost_label.setText('-- Euro')
            else:
                self.meal_name.setText(f'<h3>{meal.name}</h3>')
                self.add_remove_btn.setText('Change meal')
                self.cal_label.setText(f'{meal.nutrition[0]:.2f} kcal')
                self.weight_label.setText(f'{meal.weight:.2f} g')
                self.cost_label.setText(f'{meal.cost:.2f} Euro')

    def day_changed(self, new_ind: int):
        self.day_ind = new_ind
        self.update_info()


class IngredientTable(QTableWidget):
    def __init__(self, meal: Meal = None, editable: bool = False):
        super().__init__(0, 2)
        self.meal = meal

        self.setHorizontalHeaderItem(0, QTableWidgetItem('Ingredient'))
        self.setHorizontalHeaderItem(1, QTableWidgetItem('Amount [g]'))

        self.verticalHeader().hide()
        self.setShowGrid(False)
        if not editable:
            self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def update_contents(self, meal: Meal):
        self.meal = meal
        self.setRowCount(0)

        for ind, tup in enumerate(self.get_sorted_ingredient_list(meal=meal)):
            print(tup)
            i, a = tup
            self.insertRow(ind)
            self.setItem(ind, 0, QTableWidgetItem(i.name))
            self.setItem(ind, 1, QTableWidgetItem(f'{a:.2f}'))

    def get_sorted_ingredient_list(self, meal: Meal) -> list[list[Union[Ingredient, float]]]:
        self.meal = meal
        sort_inds = np.argsort(meal.get_all_ingredient_amounts())
        return [meal.ingredients[i] for i in sort_inds[::-1]]
