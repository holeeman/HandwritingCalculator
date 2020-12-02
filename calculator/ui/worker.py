'''
@author: Hosung Lee
@date: December 2 2020
@description: Worker class for multiprocessing
'''

from PyQt5.QtCore import QRunnable, pyqtSignal, QObject
import sys
import traceback

class OnDrawAsyncWorkerSignal(QObject):
    result = pyqtSignal(tuple)
    error = pyqtSignal(tuple)
    finished = pyqtSignal()


class OnDrawAsyncWorker(QRunnable):
    def __init__(self, fn, img):
        super(OnDrawAsyncWorker, self).__init__()
        self.fn = fn
        self.img = img
        self.signals = OnDrawAsyncWorkerSignal()

    def run(self):
        try:
            result = self.fn(self.img)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            if result is None:
                self.signals.result.emit(("", ""))
            else:
                self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()
