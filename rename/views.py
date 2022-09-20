# -*- coding: utf-8 -*-
# rename/views.py

"""This module provides the Renamer main window."""

from collections import deque
from pathlib import Path

from PyQt5.QtWidgets import QFileDialog, QWidget

from .ui.window import Ui_Window

# specify different file filters as a string
FILTERS = ";;".join(
    (
        "PNG Files (*.png)",
        "JPEG Files (*.jpeg)",
        "JPG Files (*.jpg)",
        "GIF Files (*.gif)",
        "Text Files (*.txt)",
        "Python Files (*.py)",
    )
)


class Window(QWidget, Ui_Window):
    def __init__(self):
        super().__init__()  # initialize window
        self._files = deque()  # Stores paths to the files you want to rename.
        self._filesCount = len(self._files)  # Number of files
        self._setupUI()
        self._connectSignalsSlots()

    def _setupUI(self):
        # collects code required for generating and setting up the GUI
        self.setupUi(self)

    def _connectSignalsSlots(self):
        # trigger .loadFiles() every time the user clicks the button.
        self.loadFilesButton.clicked.connect(self.loadFiles)

    def loadFiles(self):
        self.dstFileList.clear()  # clear the dst file list

        # checks if the Last Source Directory line edit is currently displaying any directory path.
        if self.dirEdit.text():
            initDir = self.dirEdit.text()  # if true: set to initDir
        else:
            initDir = str(Path.home())  # if false: set to home

        # allow the user to select one or more files, and returns a list of string-based paths to the selected files
        files, filter = QFileDialog.getOpenFileNames(
            self, "Choose Files to Rename", initDir, filter=FILTERS
        )
        if len(files) > 0:
            # extract file extention
            fileExtension = filter[filter.index("*"): -1]
            self.extensionLabel.setText(fileExtension)  # set file extention
            # path to dir containing selected files
            srcDirName = str(Path(files[0]).parent)
            self.dirEdit.setText(srcDirName)  # set text of dirEdit
            for file in files:  # iterate over the list of selected files
                self._files.append(Path(file))  # add to _files
                self.srcFileList.addItem(file)  # add to GUI
            self._filesCount = len(self._files)  # update file count
