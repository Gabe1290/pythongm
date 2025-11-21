#!/usr/bin/env python3
"""
Python Syntax Highlighter for QTextEdit
Provides syntax highlighting for Python code in the code editor
"""

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Python code"""

    def __init__(self, document):
        super().__init__(document)

        # Define highlighting rules
        self.highlighting_rules = []

        # Keyword format (Python keywords)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000FF"))  # Blue
        keyword_format.setFontWeight(QFont.Weight.Bold)

        keywords = [
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
            'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
            'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
            'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
            'try', 'while', 'with', 'yield', 'self'
        ]

        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, keyword_format))

        # Built-in functions format
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#008080"))  # Teal

        builtins = [
            'print', 'len', 'range', 'str', 'int', 'float', 'bool', 'list',
            'dict', 'set', 'tuple', 'abs', 'max', 'min', 'sum', 'round',
            'isinstance', 'hasattr', 'getattr', 'setattr', 'type'
        ]

        for word in builtins:
            pattern = QRegularExpression(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, builtin_format))

        # String format (single and double quotes)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#008000"))  # Green

        # Double-quoted strings
        self.highlighting_rules.append((
            QRegularExpression('"[^"\\\\]*(\\\\.[^"\\\\]*)*"'),
            string_format
        ))

        # Single-quoted strings
        self.highlighting_rules.append((
            QRegularExpression("'[^'\\\\]*(\\\\.[^'\\\\]*)*'"),
            string_format
        ))

        # Triple-quoted strings (docstrings)
        self.highlighting_rules.append((
            QRegularExpression('"""[^"]*"""'),
            string_format
        ))

        self.highlighting_rules.append((
            QRegularExpression("'''[^']*'''"),
            string_format
        ))

        # Number format
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#FF6600"))  # Orange

        self.highlighting_rules.append((
            QRegularExpression("\\b[0-9]+\\.?[0-9]*\\b"),
            number_format
        ))

        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#808080"))  # Gray
        comment_format.setFontItalic(True)

        self.highlighting_rules.append((
            QRegularExpression("#[^\n]*"),
            comment_format
        ))

        # Class name format
        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#0000FF"))  # Blue
        class_format.setFontWeight(QFont.Weight.Bold)

        self.highlighting_rules.append((
            QRegularExpression("\\bclass\\s+([A-Za-z_][A-Za-z0-9_]*)"),
            class_format
        ))

        # Function name format
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#0000FF"))  # Blue

        self.highlighting_rules.append((
            QRegularExpression("\\bdef\\s+([A-Za-z_][A-Za-z0-9_]*)"),
            function_format
        ))

        # Decorator format
        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor("#808000"))  # Olive

        self.highlighting_rules.append((
            QRegularExpression("@[A-Za-z_][A-Za-z0-9_]*"),
            decorator_format
        ))

    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text"""
        # Apply all rules
        for pattern, format in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)
