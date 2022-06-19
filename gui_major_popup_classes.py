from PyQt5.QtWidgets import (
    QHBoxLayout, QVBoxLayout,
    QDialog, QFormLayout, QLineEdit, QLabel, QCheckBox, QPushButton, QComboBox
)
import numpy as np

from error_handling import NoIngredientPassedError
from gui_helper_classes import form_extractor, short_nutrient_labels, MealList
from connector import LocalDatabase
from food_backend import n_nutrients, Meal
from PyQt5.QtGui import QDoubleValidator

from gui_helper_classes import (
    long_nutrient_labels, IngredientList, SearchBar, FilterAddRemoveButtons, NutrientPieChart, LabelFieldSlider,
    TypeSelectionCheckBoxes
)
from trip_backend import Trip


class AddOrEditIngredientDialog(QDialog):
    def __init__(self, local_database: LocalDatabase, mode: str = 'add', ingredient_name: str = '',
                 ingredient_code: int = None):
        super().__init__()
        self.db = local_database
        self.setWindowTitle('Add new ingredient')

        self.in_name = ingredient_name
        self.ingredient_code = ingredient_code

        self.nutrients = QFormLayout()
        self.nutrient_fields = []
        for label in long_nutrient_labels:
            self.nutrient_fields.append(QLineEdit())
            self.nutrients.addRow(label, self.nutrient_fields[-1])
            self.nutrient_fields[-1].setValidator(QDoubleValidator())

        self.name = QFormLayout()
        self.name_field = QLineEdit()
        self.name.addRow('Name:', self.name_field)

        self.type_selection = QHBoxLayout()
        self.breakfast = QCheckBox('Breakfast')
        self.lunch = QCheckBox('Lunch')
        self.dinner = QCheckBox('Dinner')
        self.snack = QCheckBox('Snack')

        self.type_selection.addWidget(QLabel('Type:'))
        self.type_selection.addWidget(self.breakfast)
        self.type_selection.addWidget(self.lunch)
        self.type_selection.addWidget(self.dinner)
        self.type_selection.addWidget(self.snack)

        self.type_fields = [self.breakfast, self.lunch, self.dinner, self.snack]

        self.cooking_water_ticks = QHBoxLayout()

        self.cooking_check = QCheckBox('Cooking')
        self.water_check = QCheckBox('Added Water')

        self.cooking_water_ticks.addWidget(QLabel('Extra Requirements:'))
        self.cooking_water_ticks.addWidget(self.cooking_check)
        self.cooking_water_ticks.addWidget(self.water_check)

        self.unit_and_price = QFormLayout()

        self.unit_size_field = QLineEdit()
        self.price_field = QLineEdit()
        self.unit_size_field.setValidator(QDoubleValidator())
        self.price_field.setValidator(QDoubleValidator())

        self.unit_and_price.addRow('Unit size [g]:', self.unit_size_field)
        self.unit_and_price.addRow('Price:', self.price_field)

        if mode == 'edit':
            self.setWindowTitle('Edit ingredient')
            self.accept_button = QPushButton('Save changes')
            self.fill_fields_with_known_info()
            self.accept_button.clicked.connect(lambda: self.save_ingredient_info_to_local_db(mode='edit'))
        else:
            self.setWindowTitle('Add new ingredient')
            self.accept_button = QPushButton('Add to database')
            self.accept_button.clicked.connect(lambda: self.save_ingredient_info_to_local_db(mode='add'))

        self.right_super_layout = QVBoxLayout()
        self.right_super_layout.addLayout(self.type_selection)
        self.right_super_layout.addLayout(self.cooking_water_ticks)
        self.right_super_layout.addLayout(self.unit_and_price)
        self.right_super_layout.addWidget(self.accept_button)
        self.right_super_layout.addStretch()

        self.child_layout = QHBoxLayout()
        self.child_layout.addLayout(self.nutrients, 1)
        self.child_layout.addLayout(self.right_super_layout, 1)

        self.super_layout = QVBoxLayout()
        self.super_layout.addLayout(self.name)
        self.super_layout.addLayout(self.child_layout)

        self.setLayout(self.super_layout)

    def save_ingredient_info_to_local_db(self, mode: str = 'add') -> None:
        nut_vals = np.zeros(n_nutrients)
        meal_types = []
        try:
            name = form_extractor(self.name, (0, 1))
            print(name)
            if name.replace(' ', '') == '':
                self.accept_button.setText('Name cannot be empty!')
                self.accept_button.setStyleSheet('QPushButton {border: 2px solid crimson}')
                raise Exception
            if mode == 'add' and name in self.db.get_ingredient_names():
                self.accept_button.setText('An ingredient with this name already exists!')
                self.accept_button.setStyleSheet('QPushButton {border: 2px solid crimson}')
                raise Exception
            for i in range(n_nutrients):
                temp = form_extractor(self.nutrients, (i, 1))
                if temp != '':
                    nut_vals[i] = float(temp)
                else:
                    nut_vals[i] = 0

            if self.breakfast.isChecked():
                meal_types.append(0)
            if self.lunch.isChecked():
                meal_types.append(1)
            if self.dinner.isChecked():
                meal_types.append(2)
            if self.snack.isChecked():
                meal_types.append(3)

            temp = form_extractor(self.unit_and_price, (0, 1))
            if temp != '':
                unit_size = float(temp)
            else:
                unit_size = np.nan
            temp = form_extractor(self.unit_and_price, (1, 1))
            if temp != '':
                price = float(temp)
            else:
                price = np.nan

            if mode == 'edit':
                if self.ingredient_code is None:
                    raise NoIngredientPassedError
                self.db.update_ingredient(in_code=self.ingredient_code, name=name, nutrition=nut_vals,
                                          water=self.water_check.isChecked(), types=np.array(meal_types),
                                          cooking=self.cooking_check.isChecked(), price_per_unit=price,
                                          unit_size=unit_size)
            else:
                self.db.add_ingredient(name=name, nutrients=nut_vals, water=self.water_check.isChecked(),
                                       types=np.array(meal_types), cooking=self.cooking_check.isChecked(),
                                       price_per_unit=price, unit_size=unit_size)

            self.close()
        except ValueError:
            self.accept_button.setText('Error: Cannot add ingredient!')
            self.accept_button.setStyleSheet('QPushButton {border: 2px solid crimson}')

    def fill_fields_with_known_info(self):
        item = self.db.get_ingredient_by_name(self.in_name)
        self.name_field.setText(item.name)

        for i, field in enumerate(self.nutrient_fields):
            field.setText(f'{item.nutrition[i]:.2f}')

        for i in item.types:
            self.type_fields[i].setChecked(True)

        if item.cooking:
            self.cooking_check.setChecked(True)

        if item.water:
            self.water_check.setChecked(True)

        self.unit_size_field.setText(f'{item.unit_size:.2f}')
        self.price_field.setText(f'{item.price_per_unit:.2f}')


class AddIngredientToMeal(QDialog):
    def __init__(self, local_database: LocalDatabase, selected_meal: Meal):
        super().__init__()
        self.db = local_database
        self.meal = selected_meal

        self.ingredient_list = IngredientList(local_database=self.db)
        self.ingredient_list.update_from_db()
        self.ingredient_list.itemSelectionChanged.connect(self.update_ingredient_nutrients_chart)
        self.ingredient_list.itemSelectionChanged.connect(self.update_meal_nutrient_chart)
        self.ingredient_list.mark_ingredients_in_meal(self.meal)

        self.search_bar = SearchBar(local_database=self.db, linked_list_widget=self.ingredient_list)
        self.search_bar.cursorPositionChanged.connect(self.search_bar.content_changed)
        self.search_bar.editingFinished.connect(self.search_bar.left_bar)

        self.btn = FilterAddRemoveButtons(filter_only=True)

        self.search_and_btn = QHBoxLayout()
        self.search_and_btn.addWidget(self.search_bar)
        self.search_and_btn.addLayout(self.btn)

        self.left_super_layout = QVBoxLayout()
        self.left_super_layout.addLayout(self.search_and_btn)
        self.left_super_layout.addWidget(self.ingredient_list)

        self.ingredient_nutrient_chart_title = QLabel()
        self.meal_nutrient_chart_title = QLabel()

        self.chart_titles = QHBoxLayout()
        self.chart_titles.addWidget(self.ingredient_nutrient_chart_title, 1)
        self.chart_titles.addWidget(self.meal_nutrient_chart_title, 1)

        self.ingredient_nutrient_chart = NutrientPieChart()
        self.updated_meal_nutrient_chart = NutrientPieChart(data=self.meal.nutrition, labels=short_nutrient_labels)

        self.nutrient_charts = QHBoxLayout()
        self.nutrient_charts.addWidget(self.ingredient_nutrient_chart, 1)
        self.nutrient_charts.addWidget(self.updated_meal_nutrient_chart, 1)

        self.amount_toggle = LabelFieldSlider(label_text='Amount:', slider_config=(0, 100, 20))
        self.amount_toggle.slider.valueChanged.connect(self.update_meal_nutrient_chart)
        self.amount_toggle.edit_field.editingFinished.connect(self.update_meal_nutrient_chart)

        self.add_to_meal_btn = QPushButton('Add to meal')
        self.remove_from_meal_btn = QPushButton('Remove from meal')
        self.cancel_btn = QPushButton('Done')

        self.add_to_meal_btn.clicked.connect(self.add_to_meal_btn_clicked)
        self.remove_from_meal_btn.clicked.connect(self.remove_from_meal_btn_clicked)
        self.cancel_btn.clicked.connect(self.cancel_btn_clicked)

        self.add_done_btn = QHBoxLayout()
        self.add_done_btn.addWidget(self.add_to_meal_btn)
        self.add_done_btn.addWidget(self.remove_from_meal_btn)
        self.add_done_btn.addWidget(self.cancel_btn)

        self.right_super_layout = QVBoxLayout()
        self.right_super_layout.addWidget(QLabel('<h3>Nutritional Values</h3>'))
        self.right_super_layout.addLayout(self.chart_titles)
        self.right_super_layout.addLayout(self.nutrient_charts)
        self.right_super_layout.addLayout(self.amount_toggle)
        self.right_super_layout.addLayout(self.add_done_btn)

        self.super_layout = QHBoxLayout()
        self.super_layout.addLayout(self.left_super_layout, 1)
        self.super_layout.addLayout(self.right_super_layout, 2)

        self.setLayout(self.super_layout)

    def update_ingredient_nutrients_chart(self):
        text = self.ingredient_list.get_selected_item_str()
        ingredient = self.db.get_ingredient_by_name(text)
        self.ingredient_nutrient_chart_title.setText(f'<h4>{text}</h4>')
        self.ingredient_nutrient_chart.update_chart(data=ingredient.nutrition, labels=short_nutrient_labels)
        self.remove_from_meal_btn.setText('Remove from meal')
        if text in self.meal.get_all_ingredient_names():
            self.amount_toggle.slider.setValue(self.meal.get_amount_of_ingredient_by_name(text))
            self.add_to_meal_btn.setText('Change amount')
        else:
            self.add_to_meal_btn.setText('Add ingredient')

    def update_meal_nutrient_chart(self):
        add_val = self.amount_toggle.slider.value()
        ingredient_name = self.ingredient_list.get_selected_item_str()
        if ingredient_name and self.amount_toggle.slider.value() > 0:
            self.meal_nutrient_chart_title.setText(
                f'<h4>{self.meal.name} after adding {self.amount_toggle.slider.value():.2f} '
                f'g of {ingredient_name}</h4>')
            temp_copy = self.meal.get_copy()
            temp_copy.add_ingredient(item=self.db.get_ingredient_by_name(ingredient_name), amount=add_val)
            self.updated_meal_nutrient_chart.update_chart(data=temp_copy.nutrition, labels=short_nutrient_labels)

    def remove_from_meal_btn_clicked(self):
        text = self.ingredient_list.get_selected_item_str()
        if self.meal.remove_ingredient_by_name(text):
            self.remove_from_meal_btn.setText(f'{text} removed!')
            self.add_to_meal_btn.setText('Add ingredient')
            self.updated_meal_nutrient_chart.update_chart(data=self.meal.nutrition, labels=short_nutrient_labels)
            self.amount_toggle.slider.setValue(0)
            self.ingredient_list.mark_ingredients_in_meal(meal=self.meal)
        else:
            self.remove_from_meal_btn.setText(f'Could not remove {text}')

    def add_to_meal_btn_clicked(self):
        add_val = self.amount_toggle.slider.value()
        ingredient_name = self.ingredient_list.get_selected_item_str()
        if ingredient_name:
            if ingredient_name in self.meal.get_all_ingredient_names():
                if add_val == 0:
                    self.remove_from_meal_btn_clicked()
                else:
                    self.add_to_meal_btn.setText('Amount changed!')
            else:
                self.add_to_meal_btn.setText('Ingredient added!')
            self.meal.add_ingredient(item=self.db.get_ingredient_by_name(ingredient_name), amount=add_val)
            self.update_meal_nutrient_chart()

        self.ingredient_list.mark_ingredients_in_meal(meal=self.meal)

    def cancel_btn_clicked(self):
        self.close()


class CreateNewMeal(QDialog):
    def __init__(self, local_database: LocalDatabase):
        super().__init__()
        self.db = local_database

        self.name_field = QLineEdit()
        self.name_label = QLabel('Name:')
        self.type_selection = TypeSelectionCheckBoxes(local_database=self.db)

        self.add_btn = QPushButton('Create Meal')
        self.cancel_btn = QPushButton('Cancel')

        self.add_btn.clicked.connect(self.create_btn_clicked)

        self.top_layout = QHBoxLayout()
        self.top_layout.addWidget(self.name_label, 1)
        self.top_layout.addWidget(self.name_field, 2)

        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.addWidget(self.add_btn)
        self.bottom_layout.addWidget(self.cancel_btn)

        self.super_layout = QVBoxLayout()
        self.super_layout.addLayout(self.top_layout)
        self.super_layout.addLayout(self.type_selection)
        self.super_layout.addLayout(self.bottom_layout)

        self.setLayout(self.super_layout)

    def create_btn_clicked(self):
        name = self.name_field.text()

        if name == '':
            self.add_btn.setText('Enter name!')
            self.add_btn.setStyleSheet('QPushButton {border: 2px solid crimson}')
            return

        elif name in self.db.get_meal_names():
            self.add_btn.setText('Name already exists!')
            self.add_btn.setStyleSheet('QPushButton {border: 2px solid crimson}')
            return

        else:
            sel_types = self.type_selection.get_selected_types()
            self.db.add_meal(name=name, own_type=sel_types)

        self.close()


class AssignMealToDay(QDialog):
    def __init__(self, local_database: LocalDatabase, trip: Trip):
        super().__init__()
        self.db = local_database
        self.trip = trip

        self.super_layout = QHBoxLayout()

        self.left_layout = QVBoxLayout()
        self.meal_list = MealList(local_database=self.db)
        self.search_bar = SearchBar(local_database=self.db, linked_list_widget=self.meal_list)
        self.filter_btn = FilterAddRemoveButtons(filter_only=True)

        self.center_layout = QVBoxLayout()
