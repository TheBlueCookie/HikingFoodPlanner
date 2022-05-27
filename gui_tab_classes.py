from PyQt5.QtWidgets import (
    QHBoxLayout, QVBoxLayout,
    QWidget, QPushButton, QTableWidget, QListWidget, QTableWidgetItem, QListWidgetItem, QAbstractItemView
)

from connector import LocalDatabase
from gui_helper_classes import NutrientPieChart, RemoveDialog
from gui_major_popup_classes import AddOrEditIngredientDialog

from gui_helper_classes import short_nutrient_labels, long_nutrient_labels, IngredientList, SearchBar


class IngredientTab(QWidget):
    def __init__(self, local_database: LocalDatabase):
        super().__init__()
        self.db = local_database

        search_filter_add = QHBoxLayout()

        filter_btn = QPushButton('Filter')
        add_btn = QPushButton('Add')
        rmv_btn = QPushButton('Remove')

        add_btn.clicked.connect(self.add_ingredient_clicked)
        rmv_btn.clicked.connect(self.rmv_button_clicked)

        self.ingredients_list = IngredientList(local_database=self.db)
        self.ingredients_list.itemSelectionChanged.connect(self.update_ingredient_details)

        self.search_bar = SearchBar(local_database=self.db, ingredient_list=self.ingredients_list)
        self.search_bar.cursorPositionChanged.connect(self.search_bar.content_changed)
        self.search_bar.editingFinished.connect(self.search_bar.left_bar)

        search_filter_add.addWidget(self.search_bar, 6)
        search_filter_add.addWidget(filter_btn, 1)
        search_filter_add.addWidget(add_btn, 1)
        search_filter_add.addWidget(rmv_btn, 1)

        left_third_layout = QVBoxLayout()
        left_third_layout.addLayout(search_filter_add)
        left_third_layout.addWidget(self.ingredients_list)

        self.nutrients_table_and_graph = QHBoxLayout()
        self.nutrients_table_layout = QHBoxLayout()
        self.nutrients_table_left = QTableWidget(8, 1)

        self.nutrients_table_left.horizontalHeader().hide()
        for i, label in enumerate(long_nutrient_labels):
            self.nutrients_table_left.setVerticalHeaderItem(i, QTableWidgetItem(label))

        self.nutrients_table_left.setShowGrid(False)
        self.nutrients_table_left.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.nutrients_table_layout.addWidget(self.nutrients_table_left)

        self.nutrients_chart = NutrientPieChart()

        self.nutrients_table_and_graph.addLayout(self.nutrients_table_layout, 1)
        self.nutrients_table_and_graph.addWidget(self.nutrients_chart, 1)

        additional_info_layout = QHBoxLayout()
        self.right_table = QTableWidget(3, 1)

        self.right_table.setVerticalHeaderItem(0, QTableWidgetItem('Energy Density'))
        self.right_table.setVerticalHeaderItem(1, QTableWidgetItem('Price per Unit'))
        self.right_table.setVerticalHeaderItem(2, QTableWidgetItem('Unit Size'))

        self.left_table = QTableWidget(3, 1)

        self.left_table.setVerticalHeaderItem(0, QTableWidgetItem('Price per 100g'))
        self.left_table.setVerticalHeaderItem(1, QTableWidgetItem('Cooking Required'))
        self.left_table.setVerticalHeaderItem(2, QTableWidgetItem('Water Required'))

        self.right_table.horizontalHeader().hide()
        self.left_table.horizontalHeader().hide()
        self.right_table.setShowGrid(False)
        self.left_table.setShowGrid(False)
        self.right_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.left_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        additional_info_layout.addWidget(self.right_table)
        additional_info_layout.addWidget(self.left_table)

        buttons_layout = QHBoxLayout()
        self.edit_btn = QPushButton('Edit')
        self.edit_btn.clicked.connect(self.edit_ingredient_clicked)
        add_to_meal_btn = QPushButton('Add to meal')
        buttons_layout.addWidget(self.edit_btn)
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

        self.ingredients_list.update_from_db()
        self.setLayout(super_layout)

    def add_ingredient_clicked(self):
        popup = AddOrEditIngredientDialog(local_database=self.db)
        popup.exec_()
        self.ingredients_list.update_from_db()

    def edit_ingredient_clicked(self):
        name = self.ingredients_list.selectedItems()
        if name:
            name = name[0].text()
            popup = AddOrEditIngredientDialog(local_database=self.db, mode='edit', ingredient_name=name)
            popup.exec_()
            self.ingredients_list.update_from_db()

    def rmv_button_clicked(self):
        name = self.ingredients_list.selectedItems()
        if name:
            name = name[0].text()
            popup = RemoveDialog(local_database=self.db, in_name=name)
            popup.exec_()
            self.ingredients_list.update_from_db()
            self.clear_ingredient_details()

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

        self.nutrients_table_and_graph.removeWidget(self.nutrients_chart)
        self.nutrients_chart = NutrientPieChart(ingredient.nutritional_values, short_nutrient_labels)
        self.nutrients_table_and_graph.addWidget(self.nutrients_chart, 1)

    def clear_ingredient_details(self):
        self.left_table.clearContents()
        self.nutrients_table_and_graph.removeWidget(self.nutrients_chart)
        self.nutrients_chart = NutrientPieChart()
        self.nutrients_table_and_graph.addWidget(self.nutrients_chart, 1)
        self.right_table.clearContents()
        self.nutrients_table_left.clearContents()


class MealTab(QWidget):
    def __init__(self, local_database):
        super().__init__()
        self.db = local_database

        search_filter_add = QHBoxLayout()

        #search_bar = S
        filter_btn = QPushButton('Filter')
        add_btn = QPushButton('Add')
        rmv_btn = QPushButton('Remove')

        #search_filter_add.addWidget(search_bar, 6)
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

        ingredients_and_nutrients_layout = QHBoxLayout()
        ingredients_and_nutrients_layout.addLayout(ingredient_layout, 1)

        additional_info_layout = QHBoxLayout()
        self.right_table = QTableWidget(3, 1)
        self.right_table.setItem(0, 0, QTableWidgetItem('Energy density'))
        self.right_table.setItem(0, 1, QTableWidgetItem('Energy density'))
        self.right_table.setItem(0, 2, QTableWidgetItem('Energy density'))

        self.right_table.setVerticalHeaderItem(0, QTableWidgetItem('Energy Density'))
        self.right_table.setVerticalHeaderItem(1, QTableWidgetItem('Total Weight'))
        self.right_table.setVerticalHeaderItem(2, QTableWidgetItem('Total Cost'))

        left_table = QTableWidget(3, 1)
        left_table.setItem(0, 0, QTableWidgetItem('5'))
        left_table.setItem(0, 1, QTableWidgetItem('Yes'))
        left_table.setItem(0, 2, QTableWidgetItem('Yes'))

        left_table.setVerticalHeaderItem(0, QTableWidgetItem('Type'))
        left_table.setVerticalHeaderItem(1, QTableWidgetItem('Cooking Required'))
        left_table.setVerticalHeaderItem(2, QTableWidgetItem('Water Required'))

        self.right_table.horizontalHeader().hide()
        left_table.horizontalHeader().hide()
        self.right_table.setShowGrid(False)
        left_table.setShowGrid(False)

        additional_info_layout.addWidget(self.right_table)
        additional_info_layout.addWidget(left_table)

        right_super_layout = QVBoxLayout()
        right_super_layout.addLayout(ingredients_and_nutrients_layout)
        right_super_layout.addLayout(additional_info_layout)

        super_layout = QHBoxLayout()
        super_layout.addLayout(left_super_layout, 1)
        super_layout.addLayout(right_super_layout, 2)

        self.setLayout(super_layout)
