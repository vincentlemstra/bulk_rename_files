# -*- coding: utf-8 -*-
# rename/views.py

"""This module provides the Renamer main window."""

from collections import deque
from pathlib import Path

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QFileDialog, QWidget

from .rename import Renamer
from .ui.window import Ui_Window

# specify different file filters as a string
FILTERS = ";;".join(
    (
        "PNG Files (*.png)",
        "JPEG Files (*.jpeg)",
        "JPG Files (*.jpg)",
        "GIF Files (*.gif)",
        "Text Files (*.txt)",
        "Microsoft Word Files (*.docx)",
        "Microsoft Excel Files (*.xlsx)",
        "Revit Project Files (*.rvt)",
        "Revit Family Files (*.rfa)",
        "CAD Files (*.dwg)",
        "CAD Files (*.dwf)",
        "CAD Files (*.dxf)",
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
        # update GUI state if no files are uploaded
        self._updateStateWhenNoFiles()

    def _updateStateWhenNoFiles(self):
        self._filesCount = len(self._files)
        self.loadFilesButton.setEnabled(True)  # enable load
        self.loadFilesButton.setFocus(True)  # can use space
        self.renameFilesButton.setEnabled(False)  # disable rename
        self.prefixEdit.clear()  # clears filename prefix
        self.prefixEdit.setEnabled(False)  # disable the typing field

    def _connectSignalsSlots(self):
        # trigger .loadFiles() every time the user clicks the button
        self.loadFilesButton.clicked.connect(self.loadFiles)
        # trigger .renameFiles() every time the user clicks the button
        self.renameFilesButton.clicked.connect(self.renameFiles)
        # connect Filename Prefix line edits .textChanged() signal with ._updateStateWhenReady()
        self.prefixEdit.textChanged.connect(self._updateStateWhenReady)

    def _updateStateWhenReady(self):
        if self.prefixEdit.text():
            # content: enable rename button
            self.renameFilesButton.setEnabled(True)
        else:
            # no content: disable rename button
            self.renameFilesButton.setEnabled(False)

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
            self._updateStateWhenFilesLoaded()  # calls GUI state

    def _updateStateWhenFilesLoaded(self):
        self.prefixEdit.setEnabled(True)  # enables typing field
        self.prefixEdit.setFocus(True)  # moves focus to edit field

    def renameFiles(self):
        self._runRenamerThread()
        self._updateStateWhileRenaming()

    def _updateStateWhileRenaming(self):
        # disables buttons while the renaming process is running
        self.loadFilesButton.setEnabled(False)
        self.renameFilesButton.setEnabled(False)

    def _runRenamerThread(self):
        prefix = self.prefixEdit.text()  # receives prefix text
        self._thread = QThread()  # new QThread object to offload the file naming process
        # turns ._files into a tuple to prevent the thread from modifying the underlying deque on the main thread
        self._renamer = Renamer(
            files=tuple(self._files),
            prefix=prefix,
        )
        # moves object to different thread
        self._renamer.moveToThread(self._thread)
        self._thread.started.connect(self._renamer.renameFiles)  # rename
        # connects the thread???s .started() signal with .renameFiles() on the Renamer instance
        self._renamer.renamedFile.connect(
            self._updateStateWhenFileRenamed)  # update state
        # connects the Renamer instance .progressed() signal with ._updateProgressBar().
        self._renamer.progressed.connect(
            self._updateProgressBar)  # update progress bar
        # update when no files are selected
        self._renamer.finished.connect(self._updateStateWhenNoFiles)
        self._renamer.finished.connect(self._thread.quit)  # clean up
        # schedule for later deletion
        self._renamer.finished.connect(self._renamer.deleteLater)
        # makes it possible to delete thread after finishing
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()  # starts the working thread

    # removes the file from the list of files to be renamed and updates GUI
    def _updateStateWhenFileRenamed(self, newFile):
        self._files.popleft()
        self.srcFileList.takeItem(0)
        self.dstFileList.addItem(str(newFile))

    def _updateProgressBar(self, fileNumber):
        # set remaining files in percent
        progressPercent = int(fileNumber / self._filesCount * 100)
        # updates .value property
        self.progressBar.setValue(progressPercent)
