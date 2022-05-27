from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget,
    QVBoxLayout,
    QMessageBox
)

import os.path
import sys

from connector import LocalDatabase
from gui_tab_classes import IngredientTab, MealTab
from gui_helper_classes import FileLoadDialog, FileSaveDialog


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


class Application(QApplication):
    def __init__(self):
        super().__init__(sys.argv)

        stylesheet = 'style.css'
        with open(stylesheet, 'r') as file:
            self.setStyleSheet(file.read())


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
