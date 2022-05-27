from PyQt5.QtWidgets import (
    QHBoxLayout, QVBoxLayout,
    QDialog, QFormLayout, QLineEdit, QLabel, QCheckBox, QPushButton
)
import numpy as np

from gui_helper_classes import form_extractor
from connector import LocalDatabase
from food_backend import n_nutrients


class AddIngredientDialog(QDialog):
    def __init__(self, local_database: LocalDatabase):
        super().__init__()
        self.db = local_database
        self.setWindowTitle('Add new ingredient')
        self.setGeometry(500, -800, 1000, 500)

        self.nutrients = QFormLayout()
        for label in ['Energy [kcal]:', 'Fat:', 'Saturated Fats:', 'Fiber:', 'Carbs:', 'Sugar:', 'Protein:', 'Salt:']:
            self.nutrients.addRow(label, QLineEdit())

        self.name = QFormLayout()
        self.name.addRow('Name:', QLineEdit())

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

        self.cooking_water_ticks = QHBoxLayout()

        self.cooking_check = QCheckBox('Cooking')
        self.water_check = QCheckBox('Added Water')

        self.cooking_water_ticks.addWidget(QLabel('Extra Requirements:'))
        self.cooking_water_ticks.addWidget(self.cooking_check)
        self.cooking_water_ticks.addWidget(self.water_check)

        self.unit_and_price = QFormLayout()
        self.unit_and_price.addRow('Unit size [g]:', QLineEdit())
        self.unit_and_price.addRow('Price:', QLineEdit())

        self.accept_button = QPushButton('Add')
        self.accept_button.clicked.connect(self.get_ingredient_info)

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

    def get_ingredient_info(self) -> None:
        nut_vals = np.zeros(n_nutrients)
        meal_types = []
        try:
            name = form_extractor(self.name, (0, 1))
            if name == '':
                self.accept_button.setText('Name cannot be empty!')
                self.accept_button.setStyleSheet('QPushButton {border: 2px solid crimson}')
            if name in self.db.get_ingredient_names():
                self.accept_button.setText('An ingredient with this name already exists!')
                self.accept_button.setStyleSheet('QPushButton {border: 2px solid crimson}')
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

            self.db.add_ingredient(name=name, nutrients=nut_vals, water=self.water_check.isChecked(),
                                   types=np.array(meal_types), cooking=self.cooking_check.isChecked(),
                                   price_per_unit=price, unit_size=unit_size)

            self.close()
        except ValueError as ex:
            self.accept_button.setText('Error: Cannot add ingredient!')
            self.accept_button.setStyleSheet('QPushButton {border: 2px solid crimson}')
