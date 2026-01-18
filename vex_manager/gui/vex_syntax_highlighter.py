try:
    from PySide6 import QtCore
    from PySide6 import QtGui
except ImportError:
    from PySide2 import QtCore
    from PySide2 import QtGui

import logging
import re

from vex_manager.config import VEXSyntaxis


logger = logging.getLogger(f"vex_manager.{__name__}")


class VEXSyntaxHighlighter(QtGui.QSyntaxHighlighter):

    def __init__(self, parent: QtCore.QObject) -> None:
        super().__init__(parent)

        keywords = "|".join(VEXSyntaxis.KEYWORDS)
        data_types = "|".join(VEXSyntaxis.DATA_TYPES)
        vex_functions = "|".join(VEXSyntaxis.VEX_FUNCTIONS)

        self.numbers_reg_exp = re.compile(r"\b\d+(\.\d+)?\b")
        self.functions_reg_exp = re.compile(rf"\b({vex_functions})\b")
        self.keywords_reg_exp = re.compile(rf"\b({keywords})\b")
        self.types_reg_exp = re.compile(rf"\b({data_types})\b")
        self.references_reg_exp = re.compile(r"[\w]*@[\w-]+")
        self.strings_reg_exp = re.compile(r'(["\'])((?:\\.|[^"\\])*)\1')
        self.comments_reg_exp = re.compile(r"//.*")
        self.comment_start_reg_exp = re.compile(r"/\*")
        self.comment_end_reg_exp = re.compile(r"\*/")

        self.plain_text_char_format = QtGui.QTextCharFormat()
        self.numbers_text_char_format = QtGui.QTextCharFormat()
        self.functions_text_char_format = QtGui.QTextCharFormat()
        self.keywords_text_char_format = QtGui.QTextCharFormat()
        self.types_text_char_format = QtGui.QTextCharFormat()
        self.references_text_char_format = QtGui.QTextCharFormat()
        self.strings_text_char_format = QtGui.QTextCharFormat()
        self.comments_text_char_format = QtGui.QTextCharFormat()
        self.multi_line_comment_text_char_format = QtGui.QTextCharFormat()

    def set_vex_systax_highlighter_colors(
        self, color_scheme: dict[str, tuple[float, float, float]]
    ) -> None:
        self.plain_text_char_format.setForeground(QtGui.QColor(*color_scheme["plain"]))

        self.numbers_text_char_format.setForeground(
            QtGui.QColor(*color_scheme["numbers"])
        )

        self.functions_text_char_format.setForeground(
            QtGui.QColor(*color_scheme["functions"])
        )

        self.keywords_text_char_format.setForeground(
            QtGui.QColor(*color_scheme["keywords"])
        )

        self.types_text_char_format.setForeground(QtGui.QColor(*color_scheme["types"]))

        self.references_text_char_format.setForeground(
            QtGui.QColor(*color_scheme["references"])
        )

        self.strings_text_char_format.setForeground(
            QtGui.QColor(*color_scheme["strings"])
        )

        self.comments_text_char_format.setForeground(
            QtGui.QColor(*color_scheme["comments"])
        )

        self.multi_line_comment_text_char_format.setForeground(
            QtGui.QColor(*color_scheme["comments"])
        )

        self.rehighlight()

    def _set_vex_syntax_highlighter(
        self,
        reg_exp: re.Pattern[str],
        text: str,
        text_char_format: QtGui.QTextCharFormat,
    ) -> None:

        for match in reg_exp.finditer(text):
            start = match.start()
            length = match.end() - match.start()
            self.setFormat(start, length, text_char_format)

    def highlightBlock(self, text: str) -> None:
        self.setFormat(0, len(text), self.plain_text_char_format)

        self._set_vex_syntax_highlighter(
            reg_exp=self.numbers_reg_exp,
            text=text,
            text_char_format=self.numbers_text_char_format,
        )

        self._set_vex_syntax_highlighter(
            reg_exp=self.functions_reg_exp,
            text=text,
            text_char_format=self.functions_text_char_format,
        )

        self._set_vex_syntax_highlighter(
            reg_exp=self.keywords_reg_exp,
            text=text,
            text_char_format=self.keywords_text_char_format,
        )

        self._set_vex_syntax_highlighter(
            reg_exp=self.types_reg_exp,
            text=text,
            text_char_format=self.types_text_char_format,
        )

        self._set_vex_syntax_highlighter(
            reg_exp=self.references_reg_exp,
            text=text,
            text_char_format=self.references_text_char_format,
        )

        self._set_vex_syntax_highlighter(
            reg_exp=self.strings_reg_exp,
            text=text,
            text_char_format=self.strings_text_char_format,
        )

        self._set_vex_syntax_highlighter(
            reg_exp=self.comments_reg_exp,
            text=text,
            text_char_format=self.comments_text_char_format,
        )

        self.setCurrentBlockState(0)

        start_index = 0

        if self.previousBlockState() != 1:
            start_index = text.find("/*")

        while start_index >= 0:
            match = self.comment_end_reg_exp.match(text, start_index)
            end_index = match.capturedStart()

            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + match.capturedLength()

            self.setFormat(
                start_index, comment_length, self.multi_line_comment_text_char_format
            )

            start_index = text.find("/*", start_index + comment_length)
