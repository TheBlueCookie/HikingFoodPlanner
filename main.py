import sys

from src.app.connector import LocalDatabase
from src.backend.trip import Trip
from src.gui.main_classes import Application, MainWindow


def run():
    if __name__ == '__main__':
        database = LocalDatabase()
        trip = Trip(CODE=0, name='', meal_types=database.meal_types)
        app = Application()
        window = MainWindow(local_database=database, trip=trip)
        window.show()
        sys.exit(app.exec_())


if __name__ == '__main__':
    run()