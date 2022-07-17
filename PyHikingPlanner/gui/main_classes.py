from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QFileDialog,
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

        self.database_dir = '..\\saves\\databases\\'
        self.trip_dir = '..\\saves\\trips\\'
        self.config_dir = '..\\config\\'

        self.top_level_layout = QVBoxLayout()

        self.base_name = ''
        self.settings = QSettings('Hiking Food Planner')

        self.menu = self.menuBar().addMenu('&File')
        self.menu.addAction('&Save Project', lambda: None)
        self.menu.addAction('&Save Project as...', lambda: None)
        self.menu.addAction('&Load Project', lambda: None)
        self.menu.addAction('&Save Project and Exit', lambda: None)

        self.database_menu = self.menuBar().addMenu('&Database')
        self.database_menu.addAction('&Save Database', self.save_db_btn_clicked)
        self.database_menu.addAction('&Save Database as...', self.save_db_as_btn_clicked)
        self.database_menu.addAction('&Load Database', self.load_db_btn_clicked)

        self.trip_menu = self.menuBar().addMenu('&Trip')
        self.trip_menu.addAction('&Save Trip', self.save_trip_btn_clicked)
        self.trip_menu.addAction('&Save Trip as...', lambda: None)
        self.trip_menu.addAction('&Load Trip', self.load_trip_btn_clicked)

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

        if os.path.isfile(f'{self.config_dir}config.ini'):
            with open(f'{self.config_dir}config.ini', 'r') as file:
                f_path = file.readline()
                if f_path.strip() != '':
                    self.base_name = os.path.basename(f_path)
                    if os.path.isfile(f'{self.database_dir}{self.base_name}'):
                        self.db.load_from_base_file(f'{self.database_dir}{self.base_name}')
                        self.ingredient_tab.ingredients_list.update_from_db()
                        self.meal_tab.meal_list.update_from_db()
                        self.setWindowTitle(f'Hiking Food Planner: {self.base_name}')
                        self.trip.link_database(db=self.db)

    def closeEvent(self, event):
        if not self.force_quit:
            reply = QMessageBox.question(self, 'Window Close', 'Save before exiting?',
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)

            if reply == QMessageBox.Yes:
                self.save_db_btn_clicked()
                self.save_current_config()
                event.accept()
            elif reply == QMessageBox.No:
                self.save_current_config()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def save_db_btn_clicked(self):
        if self.base_name == '':
            self.base_name = os.path.basename(
                QFileDialog().getSaveFileName(directory=self.database_dir, filter='*.txt')[0])
            self.setWindowTitle(f'Hiking Food Planner: {self.base_name}')
        else:
            self.db.save_base_file(base_name=self.base_name, db_dir=self.database_dir)
            self.db.save(base_name=self.base_name, db_dir=self.database_dir)

    def save_trip_btn_clicked(self):
        save_name = QFileDialog().getSaveFileName(directory=self.trip_dir, filter='*.csv')[0]
        self.trip.save_trip(f_path=f'{self.trip_dir}{os.path.basename(save_name)}')

    def load_trip_btn_clicked(self):
        load_name = QFileDialog().getOpenFileName(directory=self.trip_dir, filter='*.csv')[0]
        if load_name != '':
            self.trip.load_linked_db_code(f_path=load_name)
            if self.trip.verify_linked_database(linked_db=self.db):
                self.trip.load_trip(f_path=load_name)
                self.trip_tab.day_overview.load_trip_data()
                self.trip_tab.lower_part_widget.update_info(new_ind=0)

    def save_and_exit_btn_clicked(self):
        self.save_db_btn_clicked()
        self.force_quit = True
        self.save_current_config()
        self.close()

    def load_db_btn_clicked(self):
        base_name = os.path.basename(QFileDialog().getOpenFileName(directory=self.database_dir, filter='*.txt')[0])
        if base_name != '':
            self.base_name = os.path.basename(base_name)
            self.db.load_from_base_file(f_path=os.path.join(self.database_dir, base_name))
            self.setWindowTitle(f'Hiking Food Planner: {self.base_name}')
            self.ingredient_tab.ingredients_list.update_from_db()
            self.meal_tab.meal_list.update_from_db()
            self.trip.link_database(db=self.db)

    def save_db_as_btn_clicked(self):
        base_name = os.path.basename(QFileDialog().getSaveFileName(directory=self.database_dir, filter='*.txt')[0])
        if base_name != '':
            self.base_name = os.path.basename(base_name)
            self.setWindowTitle(f'Hiking Food Planner: {self.base_name}')
            self.save_db_btn_clicked()

    def save_current_config(self):
        with open(f'{self.config_dir}config.ini', 'w') as file:
            if self.base_name != '':
                file.write(f'{self.database_dir}{self.base_name}')


class Application(QApplication):
    def __init__(self):
        super().__init__(sys.argv)

        stylesheet = '..\\gui\\style.css'
        with open(stylesheet, 'r') as file:
            self.setStyleSheet(file.read())
