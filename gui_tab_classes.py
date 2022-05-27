from PyQt5.QtWidgets import (
    QHBoxLayout, QVBoxLayout,
    QWidget, QLineEdit, QPushButton, QTableWidget, QListWidget, QTableWidgetItem, QListWidgetItem
)

from connector import LocalDatabase
from gui_helper_classes import PieChart, RemoveDialog
from gui_popup_classes import AddIngredientDialog


class IngredientTab(QWidget):
    def __init__(self, local_database: LocalDatabase):
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
        self.ingredients_list.itemSelectionChanged.connect(self.update_ingredient_details)

        left_third_layout = QVBoxLayout()
        left_third_layout.addLayout(search_filter_add)
        left_third_layout.addWidget(self.ingredients_list)

        self.nutrients_table_and_graph = QHBoxLayout()
        self.nutrients_table_layout = QHBoxLayout()
        self.nutrients_table_left = QTableWidget(8, 1)
        self.nutrients_table_left.setItem(0, 0, QTableWidgetItem('Test'))

        self.nutrients_table_left.horizontalHeader().hide()
        self.nutrients_table_left.setVerticalHeaderItem(0, QTableWidgetItem('Energy'))
        self.nutrients_table_left.setVerticalHeaderItem(1, QTableWidgetItem('Fat'))
        self.nutrients_table_left.setVerticalHeaderItem(2, QTableWidgetItem('Sat. Fat'))
        self.nutrients_table_left.setVerticalHeaderItem(3, QTableWidgetItem('Fiber'))
        self.nutrients_table_left.setVerticalHeaderItem(4, QTableWidgetItem('Carbs'))
        self.nutrients_table_left.setVerticalHeaderItem(5, QTableWidgetItem('Sugar'))
        self.nutrients_table_left.setVerticalHeaderItem(6, QTableWidgetItem('Protein'))
        self.nutrients_table_left.setVerticalHeaderItem(7, QTableWidgetItem('Salt'))

        self.nutrients_table_left.setShowGrid(False)

        self.nutrients_table_layout.addWidget(self.nutrients_table_left)

        # nutrients_graph = PlotWidget()
        data = [i for i in range(3)]
        # nutrients_graph.pie(data)

        self.nutrients_chart = PieChart(data, ['test', 'test2', 'test3'])

        self.nutrients_table_and_graph.addLayout(self.nutrients_table_layout, 1)
        self.nutrients_table_and_graph.addWidget(self.nutrients_chart, 1)

        additional_info_layout = QHBoxLayout()
        self.right_table = QTableWidget(3, 1)
        self.right_table.setItem(0, 0, QTableWidgetItem('Energy density'))
        self.right_table.setItem(0, 1, QTableWidgetItem('Energy density'))
        self.right_table.setItem(0, 2, QTableWidgetItem('Energy density'))

        self.right_table.setVerticalHeaderItem(0, QTableWidgetItem('Energy Density'))
        self.right_table.setVerticalHeaderItem(1, QTableWidgetItem('Price per Unit'))
        self.right_table.setVerticalHeaderItem(2, QTableWidgetItem('Unit Size'))

        self.left_table = QTableWidget(3, 1)
        self.left_table.setItem(0, 0, QTableWidgetItem('5'))
        self.left_table.setItem(0, 1, QTableWidgetItem('Yes'))
        self.left_table.setItem(0, 2, QTableWidgetItem('Yes'))

        self.left_table.setVerticalHeaderItem(0, QTableWidgetItem('Price per 100g'))
        self.left_table.setVerticalHeaderItem(1, QTableWidgetItem('Cooking Required'))
        self.left_table.setVerticalHeaderItem(2, QTableWidgetItem('Water Required'))

        self.right_table.horizontalHeader().hide()
        self.left_table.horizontalHeader().hide()
        self.right_table.setShowGrid(False)
        self.left_table.setShowGrid(False)

        additional_info_layout.addWidget(self.right_table)
        additional_info_layout.addWidget(self.left_table)

        buttons_layout = QHBoxLayout()
        edit_btn = QPushButton('Edit')
        add_to_meal_btn = QPushButton('Add to meal')
        buttons_layout.addWidget(edit_btn)
        buttons_layout.addWidget(add_to_meal_btn)

        right_two_thirds_layout = QVBoxLayout()
        right_two_thirds_layout.addLayout(self.nutrients_table_and_graph)
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

    def update_ingredient_details(self):
        item = self.ingredients_list.selectedItems()[0]
        ingredient = self.db.get_ingredient_by_name(item.text())

        self.right_table.setItem(0, 0, QTableWidgetItem(f'{ingredient.nutritional_values[0] * 0.01:.2f}'))
        self.right_table.setItem(0, 1, QTableWidgetItem(f'{ingredient.price_per_unit:.2f}'))
        self.right_table.setItem(0, 2, QTableWidgetItem(f'{ingredient.unit_size:.0f}'))

        if ingredient.cooking:
            cooking = 'Yes'
        else:
            cooking = 'No'

        if ingredient.water:
            water = 'Yes'
        else:
            water = 'No'

        self.left_table.setItem(0, 0, QTableWidgetItem(f'{ingredient.price_per_gram * 100:.2f}'))
        self.left_table.setItem(0, 1, QTableWidgetItem(cooking))
        self.left_table.setItem(0, 2, QTableWidgetItem(water))

        for i in range(len(ingredient.nutritional_values)):
            self.nutrients_table_left.setItem(i, 0, QTableWidgetItem(f'{ingredient.nutritional_values[i]:.2f}'))


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

        # nutrients_graph = PlotWidget()
        # data = [i for i in range(10)]
        # nutrients_graph.plot(data, data)

        ingredients_and_nutrients_layout = QHBoxLayout()
        ingredients_and_nutrients_layout.addLayout(ingredient_layout, 1)
        # ingredients_and_nutrients_layout.addWidget(nutrients_graph, 1)

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
