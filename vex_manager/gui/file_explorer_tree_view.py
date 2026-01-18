try:
    from PySide6 import QtWidgets
    from PySide6 import QtCore
    from PySide6 import QtGui
except ImportError:
    from PySide2 import QtWidgets
    from PySide2 import QtCore
    from PySide2 import QtGui

import hou

import logging
import json
import os

import vex_manager.utils as utils
import vex_manager.core as core


logger = logging.getLogger(f"vex_manager.{__name__}")


class FileExplorerTreeView(QtWidgets.QTreeView):
    PREFERENCES_PATH = utils.get_preferences_path()

    def __init__(self) -> None:
        super().__init__()

        self.library_path = ""

        self.file_system_model = QtWidgets.QFileSystemModel()
        self.file_system_model.setNameFilters(["*.vfl"])
        self.file_system_model.setNameFilterDisables(False)

        self.setHeaderHidden(True)
        self.setModel(self.file_system_model)
        self.hideColumn(1)
        self.hideColumn(2)
        self.hideColumn(3)

    def _load_preferences(self) -> None:
        settings = {}

        if os.path.exists(FileExplorerTreeView.PREFERENCES_PATH):
            with open(FileExplorerTreeView.PREFERENCES_PATH, "r") as file_for_read:
                settings = json.load(file_for_read)

        self.warn_before_deleting_a_file = settings.get(
            "warn_before_deleting_a_file", True
        )

    def create_folder(self) -> None:
        result, folder_name = hou.ui.readInput(
            "Folder name",
            title="New Folder",
            buttons=("OK", "Cancel"),
            default_choice=0, close_choice=1,
        )

        if not result:  # result = 0 means that the user selected "Yes"
            if utils.is_valid_file_name(folder_name):
                current_index = self.currentIndex()

                if current_index.data():
                    self.file_system_model.mkdir(current_index, folder_name)
                else:
                    self.file_system_model.mkdir(self.rootIndex(), folder_name)
            else:
                logger.error(f"Invalid folder name {folder_name!r}")

    def create_vex_file(self) -> str:
        file_path = ""

        result, file_name = hou.ui.readInput(
            "VEX file name",
            title="New VEX File",
            buttons=("OK", "Cancel"),
            default_choice=0, close_choice=1,
        )

        if not result:  # result = 0 means that the user selected "Yes"
            if utils.is_valid_file_name(file_name):
                current_index = self.currentIndex()

                if current_index.data():
                    item_path = self.file_system_model.filePath(current_index)

                    if os.path.isfile(item_path):
                        item_path = os.path.dirname(item_path)

                    file_path = core.create_new_vex_file(item_path, file_name)
                else:
                    file_path = core.create_new_vex_file(self.library_path, file_name)
            else:
                logger.error(f"Invalid file name {file_name!r}")

        return file_path

    def delete_selected_item(self) -> None:
        current_index = self.currentIndex()
        item_path = self.file_system_model.filePath(current_index)

        if item_path == self.library_path:
            return

        item_path = self.file_system_model.filePath(current_index)

        if os.path.isdir(item_path):
            warn = "Delete selected folder?"
        else:
            warn = "Delete selected VEX file?"

        self._load_preferences()

        result = 0  # result = 0 means that the user selected "Yes"

        if self.warn_before_deleting_a_file:
            result = hou.ui.displayCustomConfirmation(
                warn,
                buttons=("Yes", "No"),
                close_choice=1,
                default_choice=0,
                suppress=hou.confirmType.NoConfirmType,
                title="Delete",
            )

        if not result:
            self.file_system_model.remove(current_index)

    def get_file_system_model(self) -> QtWidgets.QFileSystemModel:
        return self.file_system_model

    def set_library_path(self, library_path: str) -> None:
        self.library_path = library_path

        self.setRootIndex(self.file_system_model.index(self.library_path))

        self.file_system_model.setRootPath(self.library_path)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

        item = self.indexAt(event.pos())

        if not item.isValid():
            self.setCurrentIndex(self.rootIndex())
            self.clearSelection()
            self.clearFocus()
