import sys

from PyHikingPlanner.app.connector import LocalDatabase
from PyHikingPlanner.backend.trip import Trip
from PyHikingPlanner.gui.main_classes import Application, MainWindow

if __name__ == '__main__':
    database = LocalDatabase()
    trip = Trip(CODE=0, name='', meal_types=database.meal_types)
    app = Application()
    window = MainWindow(local_database=database, trip=trip)
    window.show()
    sys.exit(app.exec_())