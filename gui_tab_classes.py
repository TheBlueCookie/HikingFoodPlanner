from PyQt5.QtWidgets import (
    QHBoxLayout, QVBoxLayout,
    QWidget, QPushButton, QTableWidget, QListWidget, QTableWidgetItem, QListWidgetItem, QAbstractItemView
)

from connector import LocalDatabase
from gui_helper_classes import NutrientPieChart, RemoveDialog, DayOverview, DayViewMealInfo, IngredientTable
from gui_major_popup_classes import AddOrEditIngredientDialog, AddIngredientToMeal, CreateNewMeal

from gui_helper_classes import (
    short_nutrient_labels, long_nutrient_labels, IngredientList, SearchBar, FilterAddRemoveButtons, MealList
)
from trip_backend import Trip


class IngredientTab(QWidget):
    def __init__(self, local_database: LocalDatabase):
        super().__init__()
        self.db = local_database

        self.search_bar_and_btn = QHBoxLayout()

        self.btn = FilterAddRemoveButtons()

        self.btn.add_btn.clicked.connect(self.add_ingredient_clicked)
        self.btn.remove_btn.clicked.connect(self.rmv_button_clicked)

        self.ingredients_list = IngredientList(local_database=self.db)
        self.ingredients_list.itemSelectionChanged.connect(self.update_ingredient_details)
        self.ingredients_list.doubleClicked.connect(self.edit_ingredient_clicked)

        self.search_bar = SearchBar(local_database=self.db, linked_list_widget=self.ingredients_list)
        self.search_bar.cursorPositionChanged.connect(self.search_bar.content_changed)
        self.search_bar.editingFinished.connect(self.search_bar.left_bar)

        self.search_bar_and_btn.addWidget(self.search_bar, 3)
        self.search_bar_and_btn.addLayout(self.btn)

        self.left_third_layout = QVBoxLayout()
        self.left_third_layout.addLayout(self.search_bar_and_btn)
        self.left_third_layout.addWidget(self.ingredients_list)

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
        right_two_thirds_layout.addStretch()
        right_two_thirds_layout.addLayout(buttons_layout)

        super_layout = QHBoxLayout()
        super_layout.addLayout(self.left_third_layout, 1)
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
            ingredient = self.db.get_ingredient_by_name(name)
            popup = AddOrEditIngredientDialog(local_database=self.db, mode='edit', ingredient_name=ingredient.name,
                                              ingredient_code=ingredient.CODE)
            popup.exec_()
            self.ingredients_list.update_from_db()

    def rmv_button_clicked(self):
        name = self.ingredients_list.selectedItems()
        if name:
            name = name[0].text()
            popup = RemoveDialog(local_database=self.db, item=self.db.get_ingredient_by_name(name),
                                 msg='Are you sure you want to remove this ingredient?')
            popup.exec_()
            self.ingredients_list.update_from_db()
            self.clear_ingredient_details()

    def update_ingredient_details(self):
        text = self.ingredients_list.get_selected_item_str()
        if text:
            ingredient = self.db.get_ingredient_by_name(text)

            self.right_table.setItem(0, 0, QTableWidgetItem(f'{ingredient.nutrition[0] * 0.01:.2f}'))
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

            for i in range(len(ingredient.nutrition)):
                self.nutrients_table_left.setItem(i, 0, QTableWidgetItem(f'{ingredient.nutrition[i]:.2f}'))

            self.nutrients_chart.update_chart(data=ingredient.nutrition, labels=short_nutrient_labels)

    def clear_ingredient_details(self):
        self.left_table.clearContents()
        self.nutrients_chart.update_chart()
        self.right_table.clearContents()
        self.nutrients_table_left.clearContents()


class MealTab(QWidget):
    def __init__(self, local_database):
        super().__init__()
        self.db = local_database

        self.meal_list = MealList(local_database=self.db)
        self.search_bar = SearchBar(local_database=self.db, linked_list_widget=self.meal_list)
        self.search_bar.cursorPositionChanged.connect(self.search_bar.content_changed)
        self.search_bar.editingFinished.connect(self.search_bar.left_bar)

        self.meal_list.itemSelectionChanged.connect(self.update_meal_details)
        self.meal_list.doubleClicked.connect(self.add_ingredient_to_meal_btn_clicked)

        self.btn = FilterAddRemoveButtons()

        self.btn.add_btn.clicked.connect(self.add_meal_btn_clicked)
        self.btn.remove_btn.clicked.connect(self.remove_meal_btn_clicked)

        self.search_and_btn = QHBoxLayout()

        self.search_and_btn.addWidget(self.search_bar)
        self.search_and_btn.addLayout(self.btn)

        self.left_super_layout = QVBoxLayout()
        self.left_super_layout.addLayout(self.search_and_btn)
        self.left_super_layout.addWidget(self.meal_list)

        self.ingredients_table = IngredientTable()

        # self.ingredients_table = QTableWidget(0, 2)
        # self.ingredients_table.setHorizontalHeaderItem(0, QTableWidgetItem('Ingredient'))
        # self.ingredients_table.setHorizontalHeaderItem(1, QTableWidgetItem('Amount [g]'))
        #
        # self.ingredients_table.verticalHeader().hide()
        # self.ingredients_table.setShowGrid(False)
        # self.ingredients_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.nutrient_chart = NutrientPieChart()

        self.add_ingredient_to_meal_btn = QPushButton('Edit meal')
        self.add_ingredient_to_meal_btn.clicked.connect(self.add_ingredient_to_meal_btn_clicked)

        self.ingredient_layout = QVBoxLayout()
        self.ingredient_layout.addWidget(self.ingredients_table)
        self.ingredient_layout.addWidget(self.add_ingredient_to_meal_btn)

        self.ingredients_and_nutrients_layout = QHBoxLayout()
        self.ingredients_and_nutrients_layout.addLayout(self.ingredient_layout, 1)
        self.ingredients_and_nutrients_layout.addWidget(self.nutrient_chart, 1)

        self.additional_info_layout = QHBoxLayout()
        self.right_table = QTableWidget(3, 1)

        self.right_table_items = []
        for i in range(3):
            self.right_table_items.append(QTableWidgetItem())
            self.right_table.setItem(i, 0, self.right_table_items[-1])

        self.right_table.setVerticalHeaderItem(0, QTableWidgetItem('Meal Type(s)'))
        self.right_table.setVerticalHeaderItem(1, QTableWidgetItem('Cooking required'))
        self.right_table.setVerticalHeaderItem(2, QTableWidgetItem('Water required'))

        self.left_table = QTableWidget(4, 1)

        self.left_table_items = []
        for i in range(4):
            self.left_table_items.append(QTableWidgetItem())
            self.left_table.setItem(i, 0, self.left_table_items[-1])

        self.left_table.setVerticalHeaderItem(0, QTableWidgetItem('Total Energy [kcal]'))
        self.left_table.setVerticalHeaderItem(1, QTableWidgetItem('Energy Density [kcal/g]'))
        self.left_table.setVerticalHeaderItem(2, QTableWidgetItem('Total Weight [g]'))
        self.left_table.setVerticalHeaderItem(3, QTableWidgetItem('Total Cost [Euro]'))

        self.right_table.horizontalHeader().hide()
        self.left_table.horizontalHeader().hide()
        self.right_table.setShowGrid(False)
        self.left_table.setShowGrid(False)

        self.additional_info_layout.addWidget(self.left_table)
        self.additional_info_layout.addWidget(self.right_table)

        self.right_super_layout = QVBoxLayout()
        self.right_super_layout.addLayout(self.ingredients_and_nutrients_layout)
        self.right_super_layout.addLayout(self.additional_info_layout)
        self.right_super_layout.addStretch()

        self.super_layout = QHBoxLayout()
        self.super_layout.addLayout(self.left_super_layout, 1)
        self.super_layout.addLayout(self.right_super_layout, 2)

        self.setLayout(self.super_layout)

    def add_ingredient_to_meal_btn_clicked(self):
        meal_name = self.meal_list.get_selected_item_str()
        if meal_name:
            meal = self.db.get_meal_by_name(meal_name)
            popup = AddIngredientToMeal(local_database=self.db, selected_meal=meal)
            popup.exec_()
            self.update_meal_details()
            self.nutrient_chart.update_chart(data=meal.nutrition, labels=short_nutrient_labels)

    def add_meal_btn_clicked(self):
        popup = CreateNewMeal(local_database=self.db)
        popup.exec_()
        self.meal_list.update_from_db()
        self.update_meal_details()

    def remove_meal_btn_clicked(self):
        meal_name = self.meal_list.get_selected_item_str()
        if meal_name:
            popup = RemoveDialog(local_database=self.db, item=self.db.get_meal_by_name(meal_name),
                                 msg='Are you sure you want to remove this meal?')
            popup.exec_()
            self.db.remove_meal_by_name(meal_name)
            self.meal_list.update_from_db()
            self.clear_meal_details()

    def update_meal_details(self):
        meal_name = self.meal_list.get_selected_item_str()
        if meal_name:
            meal = self.db.get_meal_by_name(meal_name)
            self.clear_meal_details()
            self.nutrient_chart.update_chart(data=meal.nutrition, labels=short_nutrient_labels)
            self.ingredients_table.update_contents(meal=meal)
            # for ind, tup in enumerate(meal.ingredients):
            #     i, a = tup
            #     self.ingredients_table.insertRow(ind)
            #     self.ingredients_table.setItem(ind, 0, QTableWidgetItem(i.name))
            #     self.ingredients_table.setItem(ind, 1, QTableWidgetItem(f'{a:.2f}'))

            if meal.weight != 0:
                iter_list = [meal.get_total_energy(), meal.nutrition[0] / meal.weight, meal.weight, meal.cost]
            else:
                iter_list = [0, 0, 0, 0]
            for i, val in enumerate(iter_list):
                self.left_table_items.append(QTableWidgetItem(f'{val:.2f}'))

            self.right_table_items = [QTableWidgetItem() for i in range(3)]

            meal.update_cooking_and_water()

            if meal.cooking:
                text = 'Yes'
            else:
                text = 'No'

            self.right_table_items[2].setText(text)

            if meal.water:
                text = 'Yes'
            else:
                text = 'No'

            self.right_table_items[1].setText(text)

            self.right_table_items[0].setText(meal.get_own_type_str())

            for i, item in enumerate(self.right_table_items):
                self.right_table.setItem(i, 0, item)

            for i, item in enumerate(self.left_table_items):
                self.left_table.setItem(i, 0, item)

    def clear_meal_details(self):
        self.ingredients_table.clearContents()
        self.nutrient_chart.update_chart()
        self.right_table.clearContents()
        self.left_table.clearContents()
        self.left_table_items = []
        self.right_table_items = []


class TripTab(QWidget):
    def __init__(self, local_database: LocalDatabase, trip: Trip):
        super().__init__()
        self.db = local_database
        self.trip = trip

        self.super_layout = QVBoxLayout()

        self.upper_btns_layout = QHBoxLayout()
        self.global_view_btn = QPushButton('Trip Summary')
        self.add_day_btn = QPushButton('Add day')
        self.rmv_day_btn = QPushButton('Remove day')

        self.add_day_btn.clicked.connect(self.add_day_btn_clicked)

        self.upper_btns_layout.addWidget(self.global_view_btn, 1)
        self.upper_btns_layout.addWidget(self.add_day_btn, 1)
        self.upper_btns_layout.addWidget(self.rmv_day_btn, 1)

        self.day_overview = DayOverview(local_database=self.db, trip=self.trip)
        self.day_overview.shadow_days.itemSelectionChanged.connect(self.day_selection_changed)

        self.day_details_widget = TripTabDayView(trip_tab=self)

        self.super_layout.addLayout(self.upper_btns_layout, 1)
        self.super_layout.addWidget(self.day_overview, 3)
        self.super_layout.addWidget(self.day_details_widget, 6)

        self.setLayout(self.super_layout)

    def add_day_btn_clicked(self):
        self.day_overview.add_day()

    def day_selection_changed(self):
        new_day = self.day_overview.get_current_day()
        if new_day is not None:
            self.day_details_widget.update_info(new_day)


class TripTabDayView(QWidget):
    def __init__(self, trip_tab: TripTab):
        super().__init__()
        self.trip_tab = trip_tab

        self.super_layout = QHBoxLayout()

        self.meal_types_info_layout = QVBoxLayout()
        self.meal_types_info_widgets = []

        for meal_type in self.trip_tab.db.meal_types:
            self.meal_types_info_widgets.append(
                DayViewMealInfo(local_database=self.trip_tab.db, trip=self.trip_tab.trip, meal_type=meal_type,
                                day_ind=None))
            self.meal_types_info_layout.addWidget(self.meal_types_info_widgets[-1], 1)

        self.super_layout.addLayout(self.meal_types_info_layout, 1)
        self.super_layout.addStretch(2)

        self.setLayout(self.super_layout)

    def update_info(self, new_ind: int):
        for i in self.meal_types_info_widgets:
            i.day_changed(new_ind)
