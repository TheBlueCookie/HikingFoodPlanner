import os.path

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTabWidget, QGridLayout, QTextEdit, QPushButton,
    QListWidget, QListWidgetItem, QDialog, QFormLayout, QLineEdit, QHBoxLayout, QComboBox, QLabel, QCheckBox,
    QTableWidget, QTableWidgetItem, QMainWindow, QDialogButtonBox, QFileDialog, QMessageBox
)

from pyqtgraph import PlotWidget, plot
import numpy as np
import sys
from connector import LocalDatabase
from food_backend import n_nutrients


def form_extractor(form, field):
    x, y = field
    return form.itemAt(x, y).widget().text()


class MainWindow(QMainWindow):
    def __init__(self, local_database: LocalDatabase):
        super().__init__()
        self.db = local_database
        self.setWindowTitle('Hiking Food Planner')

        self.top_level_layout = QVBoxLayout()

        self.save_name = ''

        self.menu = self.menuBar().addMenu('&File')
        self.menu.addAction('&Save', self.save_btn_clicked)
        self.menu.addAction('&Save as...')
        self.menu.addAction('&Load', self.load_btn_clicked)
        self.menu.addAction('&Save and Exit')

        self.tabs = QTabWidget()
        self.ingredient_tab = IngredientTab(self.db)
        self.tabs.addTab(self.ingredient_tab, 'Ingredients')
        self.tabs.addTab(MealTab(self.db), 'Meals')
        self.top_level_layout.addWidget(self.tabs)

        self.setCentralWidget(self.tabs)

        self.setLayout(self.top_level_layout)
        self.showMaximized()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Window Close', 'Save before exiting?',
                                     QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            self.save_btn_clicked()
            event.accept()
        elif reply == QMessageBox.No:
            event.accept()
        else:
            event.ignore()

    def save_btn_clicked(self):
        if self.save_name == '':
            dlg = FileSaveDialog(local_database=self.db)
            self.save_name = dlg.f_name
            self.setWindowTitle(f'Hiking Food Planner: {os.path.basename(self.save_name)}')
        else:
            self.db.save(self.save_name.split('.')[0])

    def load_btn_clicked(self):
        dlg = FileLoadDialog(local_database=self.db)
        self.save_name = dlg.f_name
        self.setWindowTitle(f'Hiking Food Planner: {os.path.basename(self.save_name)}')
        self.ingredient_tab.update_ingredient_list()


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

    def get_ingredient_info(self):
        nut_vals = np.zeros(n_nutrients)
        meal_types = []
        try:
            name = form_extractor(self.name, (0, 1))
            if name == '':
                self.accept_button.setText('Name cannot be empty!')
                self.accept_button.setStyleSheet('QPushButton {border: 2px solid crimson}')
                return False
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
            return True
        except ValueError as ex:
            self.accept_button.setText('Error: Cannot add ingredient!')
            self.accept_button.setStyleSheet('QPushButton {border: 2px solid crimson}')
            return False


class Application(QApplication):
    def __init__(self):
        super().__init__(sys.argv)

        stylesheet = 'style.css'
        with open(stylesheet, 'r') as file:
            self.setStyleSheet(file.read())


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


class IngredientTab(QWidget):
    def __init__(self, local_database):
        super().__init__()
        self.db = local_database

        search_filter_add = QHBoxLayout()

        search_bar = QLineEdit()
        filter_btn = QPushButton('Filter')
        add_btn = QPushButton('Add')
        rmv_btn = QPushButton('Remove')

        add_btn.clicked.connect(self.add_ingredient_clicked)
        rmv_btn.clicked.connect(self.rmv_button_clicked)

        search_filter_add.addWidget(search_bar, 6)
        search_filter_add.addWidget(filter_btn, 1)
        search_filter_add.addWidget(add_btn, 1)
        search_filter_add.addWidget(rmv_btn, 1)

        self.ingredients_list = QListWidget()

        left_third_layout = QVBoxLayout()
        left_third_layout.addLayout(search_filter_add)
        left_third_layout.addWidget(self.ingredients_list)

        nutrients_table_and_graph = QHBoxLayout()
        nutrients_table_layout = QHBoxLayout()
        nutrients_table_left = QTableWidget(8, 1)
        nutrients_table_left.setItem(0, 0, QTableWidgetItem('Test'))

        nutrients_table_left.horizontalHeader().hide()
        nutrients_table_left.setVerticalHeaderItem(0, QTableWidgetItem('Energy'))
        nutrients_table_left.setVerticalHeaderItem(1, QTableWidgetItem('Fat'))
        nutrients_table_left.setVerticalHeaderItem(2, QTableWidgetItem('Sat. Fat'))
        nutrients_table_left.setVerticalHeaderItem(3, QTableWidgetItem('Fiber'))
        nutrients_table_left.setVerticalHeaderItem(4, QTableWidgetItem('Carbs'))
        nutrients_table_left.setVerticalHeaderItem(5, QTableWidgetItem('Sugar'))
        nutrients_table_left.setVerticalHeaderItem(6, QTableWidgetItem('Protein'))
        nutrients_table_left.setVerticalHeaderItem(7, QTableWidgetItem('Salt'))

        nutrients_table_left.setShowGrid(False)

        nutrients_table_layout.addWidget(nutrients_table_left)

        nutrients_graph = PlotWidget()
        data = [i for i in range(10)]
        nutrients_graph.plot(data, data)

        nutrients_table_and_graph.addLayout(nutrients_table_layout, 1)
        nutrients_table_and_graph.addWidget(nutrients_graph, 1)

        additional_info_layout = QHBoxLayout()
        right_table = QTableWidget(3, 1)
        right_table.setItem(0, 0, QTableWidgetItem('Energy density'))
        right_table.setItem(0, 1, QTableWidgetItem('Energy density'))
        right_table.setItem(0, 2, QTableWidgetItem('Energy density'))

        right_table.setVerticalHeaderItem(0, QTableWidgetItem('Energy Density'))
        right_table.setVerticalHeaderItem(1, QTableWidgetItem('Price per Unit'))
        right_table.setVerticalHeaderItem(2, QTableWidgetItem('Unit Size'))

        left_table = QTableWidget(3, 1)
        left_table.setItem(0, 0, QTableWidgetItem('5'))
        left_table.setItem(0, 1, QTableWidgetItem('Yes'))
        left_table.setItem(0, 2, QTableWidgetItem('Yes'))

        left_table.setVerticalHeaderItem(0, QTableWidgetItem('Price per 100g'))
        left_table.setVerticalHeaderItem(1, QTableWidgetItem('Cooking Required'))
        left_table.setVerticalHeaderItem(2, QTableWidgetItem('Water Required'))

        right_table.horizontalHeader().hide()
        left_table.horizontalHeader().hide()
        right_table.setShowGrid(False)
        left_table.setShowGrid(False)

        additional_info_layout.addWidget(right_table)
        additional_info_layout.addWidget(left_table)

        buttons_layout = QHBoxLayout()
        edit_btn = QPushButton('Edit')
        add_to_meal_btn = QPushButton('Add to meal')
        buttons_layout.addWidget(edit_btn)
        buttons_layout.addWidget(add_to_meal_btn)

        right_two_thirds_layout = QVBoxLayout()
        right_two_thirds_layout.addLayout(nutrients_table_and_graph)
        right_two_thirds_layout.addLayout(additional_info_layout)
        right_two_thirds_layout.addLayout(buttons_layout)
        right_two_thirds_layout.addStretch()

        super_layout = QHBoxLayout()
        super_layout.addLayout(left_third_layout, 1)
        super_layout.addLayout(right_two_thirds_layout, 2)
        super_layout.addStretch()

        self.update_ingredient_list()
        self.setLayout(super_layout)

    def add_ingredient_clicked(self):
        popup = AddIngredientDialog(local_database=self.db)
        popup.exec_()
        self.update_ingredient_list()

    def rmv_button_clicked(self):
        popup = RemoveDialog()
        popup.exec_()

    def update_ingredient_list(self):
        self.ingredients_list.clear()
        names = self.db.get_ingredient_names()
        for name in names:
            self.ingredients_list.addItem(QListWidgetItem(name))


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


class MealTab(QWidget):
    def __init__(self, local_database):
        super().__init__()
        self.db = local_database

        search_filter_add = QHBoxLayout()

        search_bar = QLineEdit()
        filter_btn = QPushButton('Filter')
        add_btn = QPushButton('Add')
        rmv_btn = QPushButton('Remove')

        search_filter_add.addWidget(search_bar, 6)
        search_filter_add.addWidget(filter_btn, 1)
        search_filter_add.addWidget(add_btn, 1)
        search_filter_add.addWidget(rmv_btn, 1)

        meal_list = QListWidget()
        meal_list.addItem(QListWidgetItem('Test 1'))
        meal_list.addItem(QListWidgetItem('Test 2'))

        left_super_layout = QVBoxLayout()
        left_super_layout.addLayout(search_filter_add)
        left_super_layout.addWidget(meal_list)

        ingredients_table = QTableWidget(0, 2)
        ingredients_table.setHorizontalHeaderItem(0, QTableWidgetItem('Ingredient'))
        ingredients_table.setHorizontalHeaderItem(1, QTableWidgetItem('Amount [g]'))
        ingredients_table.verticalHeader().hide()
        ingredients_table.setShowGrid(False)

        add_btn = QPushButton('Add Ingredient')

        ingredient_layout = QVBoxLayout()
        ingredient_layout.addWidget(ingredients_table)
        ingredient_layout.addWidget(add_btn)

        nutrients_graph = PlotWidget()
        data = [i for i in range(10)]
        nutrients_graph.plot(data, data)

        ingredients_and_nutrients_layout = QHBoxLayout()
        ingredients_and_nutrients_layout.addLayout(ingredient_layout, 1)
        ingredients_and_nutrients_layout.addWidget(nutrients_graph, 1)

        additional_info_layout = QHBoxLayout()
        right_table = QTableWidget(3, 1)
        right_table.setItem(0, 0, QTableWidgetItem('Energy density'))
        right_table.setItem(0, 1, QTableWidgetItem('Energy density'))
        right_table.setItem(0, 2, QTableWidgetItem('Energy density'))

        right_table.setVerticalHeaderItem(0, QTableWidgetItem('Energy Density'))
        right_table.setVerticalHeaderItem(1, QTableWidgetItem('Total Weight'))
        right_table.setVerticalHeaderItem(2, QTableWidgetItem('Total Cost'))

        left_table = QTableWidget(3, 1)
        left_table.setItem(0, 0, QTableWidgetItem('5'))
        left_table.setItem(0, 1, QTableWidgetItem('Yes'))
        left_table.setItem(0, 2, QTableWidgetItem('Yes'))

        left_table.setVerticalHeaderItem(0, QTableWidgetItem('Type'))
        left_table.setVerticalHeaderItem(1, QTableWidgetItem('Cooking Required'))
        left_table.setVerticalHeaderItem(2, QTableWidgetItem('Water Required'))

        right_table.horizontalHeader().hide()
        left_table.horizontalHeader().hide()
        right_table.setShowGrid(False)
        left_table.setShowGrid(False)

        additional_info_layout.addWidget(right_table)
        additional_info_layout.addWidget(left_table)

        right_super_layout = QVBoxLayout()
        right_super_layout.addLayout(ingredients_and_nutrients_layout)
        right_super_layout.addLayout(additional_info_layout)

        super_layout = QHBoxLayout()
        super_layout.addLayout(left_super_layout, 1)
        super_layout.addLayout(right_super_layout, 2)

        self.setLayout(super_layout)


database = LocalDatabase()
app = Application()
dlg = MainWindow(local_database=database)
dlg.show()
sys.exit(app.exec_())

# if 1: # __name__ == 'main':
#     app = QApplication(sys.argv)
#     window = Window()
#     window.show()
#     sys.exit(app.exec_())
