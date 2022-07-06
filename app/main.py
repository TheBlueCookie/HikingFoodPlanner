from gui.main_classes import Application, MainWindow
from connector import LocalDatabase
import sys

from backend.trip import Trip

if __name__ == '__main__':
    database = LocalDatabase()
    trip = Trip(CODE=0, name='')
    app = Application()
    window = MainWindow(local_database=database, trip=trip)
    window.show()
    sys.exit(app.exec_())