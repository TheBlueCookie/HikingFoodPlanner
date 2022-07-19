import sys
import os

from src.app.connector import LocalDatabase
from src.backend.trip import Trip
from src.gui.main_classes import Application, MainWindow


def run():
    database = LocalDatabase()
    trip = Trip(CODE=0, name='', meal_types=database.meal_types)
    app = Application()
    window = MainWindow(local_database=database, trip=trip)
    window.show()
    sys.exit(app.exec_())

def prepare_dirs():
    for d in ['databases', 'trips', 'shopping_lists']:
        if not os.path.isdir(f'.\\saves\\{d}'):
            os.mkdir(f'.\\saves\\{d}')
    
    if not os.path.isdir(f'.\\config'):
        os.mkdir(f'.\\mkdir')


if __name__ == '__main__':
    print('Application started...\n')
    prepare_dirs()
    run()