try:
    from PySide6 import QtWidgets
    from PySide6 import QtCore
    from PySide6 import QtGui
except ImportError:
    from PySide2 import QtWidgets
    from PySide2 import QtCore
    from PySide2 import QtGui

import logging

from vex_manager.gui.file_explorer_tree_view import FileExplorerTreeView
import vex_manager.core as core


logger = logging.getLogger(f"vex_manager.{__name__}")


class FileExplorerWidget(QtWidgets.QWidget):
    double_clicked = QtCore.Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.library_path = ""
        self.warn_before_deleting_a_file = True

        self._create_widgets()
        self._create_layouts()
        self._create_connections()

    def _create_widgets(self) -> None:

        self.file_explorer_tree_view = FileExplorerTreeView()
        self.file_system_model = self.file_explorer_tree_view.get_file_system_model()

        self.delete_push_button = QtWidgets.QPushButton("Delete")

        self.new_file_push_button = QtWidgets.QPushButton("New File")

        self.new_folder_push_button = QtWidgets.QPushButton("New Folder")

    def _create_layouts(self) -> None:
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.file_explorer_tree_view)
        main_layout.addWidget(self.delete_push_button)
        main_layout.setContentsMargins(QtCore.QMargins())
        main_layout.setSpacing(3)

        new_h_box_layout = QtWidgets.QHBoxLayout()
        new_h_box_layout.addWidget(self.new_file_push_button)
        new_h_box_layout.addWidget(self.new_folder_push_button)
        main_layout.addLayout(new_h_box_layout)

    def _create_connections(self) -> None:
        self.file_explorer_tree_view.doubleClicked.connect(
            self._file_explorer_double_clicked_tree_view
        )

        self.delete_push_button.clicked.connect(self._delete_clicked_push_button)
        self.new_file_push_button.clicked.connect(self._new_file_clicked_push_button)
        self.new_folder_push_button.clicked.connect(self._new_folder_clicked_push_button)

    def _file_explorer_double_clicked_tree_view(self, index: QtCore.QModelIndex) -> None:
        if not self.file_system_model.isDir(index):
            self.double_clicked.emit(self.file_system_model.filePath(index))

    def _delete_clicked_push_button(self) -> None:
        self.file_explorer_tree_view.delete_selected_item()

    def _new_file_clicked_push_button(self) -> None:
        self.file_explorer_tree_view.create_vex_file()

    def _new_folder_clicked_push_button(self) -> None:
        self.file_explorer_tree_view.create_folder()

    def get_library_path(self) -> str:
        return self.library_path

    def set_library_path(self, library_path: str) -> None:
        self.library_path = library_path

        self.file_explorer_tree_view.set_library_path(library_path)
