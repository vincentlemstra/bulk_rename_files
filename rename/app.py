# -*- coding: utf-8 -*-
# rename/app.py

"""This module provides the Renamer application."""

import sys

from PyQt5.QtWidgets import QApplication

from .views import Window

def main():
    # Creates the application
    app = QApplication(sys.argv)
    # Creates the main window
    win = Window()
    # Shows the main window
    win.show()
    # Run the event loop
    sys.exit(app.exec())