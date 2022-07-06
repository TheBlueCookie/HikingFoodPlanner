from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget,
    QVBoxLayout,
    QMessageBox
)

from PyQt5.QtCore import QSettings

import os.path
import sys

from app.connector import LocalDatabase
from gui.tab_classes import IngredientTab, MealTab, TripTab
from gui.helper_classes import FileLoadDialog, FileSaveDialog
from backend.trip import Trip


class MainWindow(QMainWindow):
    def __init__(self, local_database: LocalDatabase, trip: Trip):
        super().__init__()
        self.db = local_database
        self.trip = trip
        self.setWindowTitle('Hiking Food Planner')
        self.force_quit = False

        self.top_level_layout = QVBoxLayout()

        self.save_name = ''
        self.settings = QSettings('Hiking Food Planner')

        self.menu = self.menuBar().addMenu('&File')
        self.menu.addAction('&Save', self.save_btn_clicked)
        self.menu.addAction('&Save as...', self.save_as_btn_clicked)
        self.menu.addAction('&Load', self.load_btn_clicked)
        self.menu.addAction('&Save and Exit', self.save_and_exit_btn_clicked)

        self.tabs = QTabWidget()
        self.ingredient_tab = IngredientTab(self.db)
        self.tabs.addTab(self.ingredient_tab, 'Ingredients')
        self.meal_tab = MealTab(self.db)
        self.tabs.addTab(self.meal_tab, 'Meals')
        self.trip_tab = TripTab(local_database=self.db, trip=self.trip)
        self.tabs.addTab(self.trip_tab, 'Trip')
        self.top_level_layout.addWidget(self.tabs)

        self.setCentralWidget(self.tabs)

        self.showMaximized()

        if os.path.isfile('..\\config\\config.ini'):
            with open('..\\config\\config.ini', 'r') as file:
                f_path = file.readline()
                print(f_path)
                if f_path.strip() != '':
                    self.setWindowTitle(f'Hiking Food Planner: {f_path}')
                    self.save_name = os.path.join('..', 'config', f_path)
                    print('save name', self.save_name)
                    self.db.load_from_basefile(self.save_name)
                    self.ingredient_tab.ingredients_list.update_from_db()
                    self.meal_tab.meal_list.update_from_db()

    def closeEvent(self, event):
        if not self.force_quit:
            reply = QMessageBox.question(self, 'Window Close', 'Save before exiting?',
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)

            if reply == QMessageBox.Yes:
                self.save_btn_clicked()
                self.save_current_config()
                event.accept()
            elif reply == QMessageBox.No:
                self.save_current_config()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def save_btn_clicked(self):
        if self.save_name == '':
            diag = FileSaveDialog(local_database=self.db)
            self.save_name = diag.f_name
            self.setWindowTitle(f'Hiking Food Planner: {os.path.basename(self.save_name)}')
        else:
            self.save_database_base_file()
            self.db.save(self.save_name.split('.')[0])

    def save_and_exit_btn_clicked(self):
        self.save_btn_clicked()
        self.force_quit = True
        self.save_current_config()
        self.close()

    def load_btn_clicked(self):
        diag = FileLoadDialog(local_database=self.db)
        self.save_name = os.path.join('..', 'config', os.path.basename(diag.f_name))
        self.setWindowTitle(f'Hiking Food Planner: {os.path.basename(self.save_name)}')
        self.ingredient_tab.ingredients_list.update_from_db()
        self.meal_tab.meal_list.update_from_db()

    def save_as_btn_clicked(self):
        diag = FileSaveDialog(local_database=self.db)
        self.save_name = os.path.join('..', 'config', os.path.basename(diag.f_name))
        self.setWindowTitle(f'Hiking Food Planner: {os.path.basename(self.save_name)}')

    def save_current_config(self):
        with open('..\\config\\config.ini', 'w') as file:
            if self.save_name != '':
                print(self.save_name)
                file.write(self.save_name)

    def save_database_base_file(self):
        data_name = self.save_name.split('.')[0]
        with open(self.save_name, 'w') as file:
            if self.db.has_ingredients():
                file.write(f'..\\data\\{data_name}_ingredients.csv\n')
            if self.db.has_meals():
                file.write(f'..\\data\\{data_name}_meals.csv')


class Application(QApplication):
    def __init__(self):
        super().__init__(sys.argv)

        stylesheet = '..\\gui\\style.css'
        with open(stylesheet, 'r') as file:
            self.setStyleSheet(file.read())
