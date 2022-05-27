from PyQt5.QtWidgets import (
    QHBoxLayout, QVBoxLayout,
    QDialog, QFormLayout, QLineEdit, QLabel, QCheckBox, QPushButton
)
import numpy as np

from gui_helper_classes import form_extractor
from connector import LocalDatabase
from food_backend import n_nutrients

from gui_helper_classes import long_nutrient_labels


class AddOrEditIngredientDialog(QDialog):
    def __init__(self, local_database: LocalDatabase, mode: str = 'add', ingredient_name: str = ''):
        super().__init__()
        self.db = local_database
        self.setWindowTitle('Add new ingredient')
        self.setGeometry(500, -800, 1000, 500)

        self.in_name = ingredient_name

        self.nutrients = QFormLayout()
        self.nutrient_fields = []
        for label in long_nutrient_labels:
            self.nutrient_fields.append(QLineEdit())
            self.nutrients.addRow(label, self.nutrient_fields[-1])

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
            self.accept_button.clicked.connect(self.save_ingredient_info_to_local_db)

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
                self.db.delete_ingredient_by_name(self.in_name)

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
            field.setText(f'{item.nutritional_values[i]:.2f}')

        for i in item.types:
            self.type_fields[i].setChecked(True)

        if item.cooking:
            self.cooking_check.setChecked(True)

        if item.water:
            self.water_check.setChecked(True)

        self.unit_size_field.setText(f'{item.unit_size:.2f}')
        self.price_field.setText(f'{item.price_per_unit:.2f}')
