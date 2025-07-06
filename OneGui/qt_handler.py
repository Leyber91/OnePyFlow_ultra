# gui_v2/qt_handler.py

import logging
from PyQt5 import QtCore

class QtHandler(logging.Handler, QtCore.QObject):
    """
    A logging handler that emits log records via a PyQt signal.
    """
    log_signal = QtCore.pyqtSignal(str)

    def __init__(self):
        logging.Handler.__init__(self)
        QtCore.QObject.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        self.log_signal.emit(msg)
