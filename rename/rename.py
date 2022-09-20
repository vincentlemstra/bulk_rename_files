# -*- coding: utf-8 -*-
#   rename/rename.py

"""This module provides the Renamer class to rename multiple files."""

import time
from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal


class Renamer(QObject):
    progressed = pyqtSignal(int)  # returns integer of the current file
    renamedFile = pyqtSignal(Path)  # returns path of renamed file
    finished = pyqtSignal()  # emitted when process is finished


    def __init__(self, files, prefix):
        super().__init__()
        self._files = files  # list of selected files
        self._prefix = prefix  # prefix to rename

    def renameFiles(self):
        # loop selected files
        for fileNumber, file in enumerate(self._files, 1):
            # builds new filename
            newFile = file.parent.joinpath(
                # option 1: use for full new file name
                # f"{self._prefix}{str(fileNumber)}{file.suffix}"

                # option 2: use to keep old file name (with number ID)
                # f"{self._prefix}{str(fileNumber)}{file.stem}{file.suffix}"

                # option 3: use to keep old file name (without ID)
                f"{self._prefix}{file.stem}{file.suffix}"
                
            )
            file.rename(newFile)
            time.sleep(0.1)  # Can be used to slow down application
            self.progressed.emit(fileNumber)  # update GUI
            self.renamedFile.emit(newFile)  # update GUI
        self.progressed.emit(0)  # resets the progress
        self.finished.emit()  # finished signal
