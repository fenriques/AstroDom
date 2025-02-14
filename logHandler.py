import logging
from PyQt6.QtWidgets import QTextEdit

class QTextEditLogger(logging.Handler):
    def __init__(self, log_edit: QTextEdit):
        super().__init__()
        self.log_edit = log_edit

    def emit(self, record):
        msg = self.format(record)
        self.log_edit.append(msg)
        self.log_edit.verticalScrollBar().setValue(self.log_edit.verticalScrollBar().maximum()) 
        self.flush()

    def flush(self):
        self.log_edit.ensureCursorVisible()
                
class ColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': 'green',
        'INFO': 'lightblue',
        'WARNING': 'orange',
        'ERROR': 'red',
        'CRITICAL': 'purple'
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, 'black')
        record.msg = f'<span style="color: {color};">{record.msg}</span>'
        return super().format(record)