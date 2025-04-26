import sys
import time

from PyQt6.QtCore import (QCoreApplication, QObject, QRunnable, QThread,
                          QThreadPool, pyqtSignal)
from PyQt6 import QtWidgets, QtGui

class Color(QtWidgets.QWidget):
    def __init__(self, color):
        super().__init__()

        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(color))
        self.setPalette(palette)
# Subclassing QThread
# http://qt-project.org/doc/latest/qthread.html
class AThread(QThread):

    def run(self):
        count = 0
        while count < 5:
            time.sleep(1)
            print("A Increasing")
            count += 1

# Subclassing QObject and using moveToThread
# http://blog.qt.digia.com/blog/2007/07/05/qthreads-no-longer-abstract
class SomeObject(QObject):

    finished = pyqtSignal()

    def long_running(self):
        count = 0
        while count < 5:
            time.sleep(1)
            print("B Increasing")
            count += 1
        self.finished.emit()

# Using a QRunnable
# http://qt-project.org/doc/latest/qthreadpool.html
# Note that a QRunnable isn't a subclass of QObject and therefore does
# not provide signals and slots.
class Runnable(QRunnable):

    def run(self):
        count = 0
        app = QCoreApplication.instance()
        while count < 5:
            print("C Increasing")
            time.sleep(1)
            count += 1
        app.quit()


def using_q_thread():
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    window.setCentralWidget(Color("red"))
    window.show()
    thread = AThread()
    thread.finished.connect(app.exit)
    thread.start()
    app.exec()
    # sys.exit(app.exec())

def using_move_to_thread():
    app = QCoreApplication([])
    objThread = QThread()
    obj = SomeObject()
    obj.moveToThread(objThread)
    obj.finished.connect(objThread.quit)
    objThread.started.connect(obj.long_running)
    objThread.finished.connect(app.exit)
    objThread.start()
    sys.exit(app.exec())

def using_q_runnable():
    app = QCoreApplication([])
    runnable = Runnable()
    QThreadPool.globalInstance().start(runnable)
    sys.exit(app.exec())

if __name__ == "__main__":
    #using_q_thread()
    #using_move_to_thread()
    using_q_thread()
