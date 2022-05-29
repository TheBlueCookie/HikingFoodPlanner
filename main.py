from gui_main_classes import Application, MainWindow
from connector import LocalDatabase
import sys

if __name__ == '__main__':
    database = LocalDatabase()
    app = Application()
    window = MainWindow(local_database=database)
    window.show()
    sys.exit(app.exec_())