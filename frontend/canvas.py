########### PyQT5 imports ###########
import asyncio
import os
from enum import Enum

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPoint, QEventLoop, QTimer
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QWidget, QLabel, QMessageBox, QScrollArea, QGridLayout, QVBoxLayout, QSizePolicy, QDialog

# import backend.main as imageProcessor

class Utensil:
    def __init__(self, color : QColor, radius : int,
                 brush_style : Qt.PenStyle = Qt.SolidLine,
                 cap_style : Qt.PenCapStyle = Qt.RoundCap,
                 join_style : Qt.PenJoinStyle = Qt.RoundJoin):
        self.maxWidth = 50
        self.color = color
        self.radius = radius
        self.brush_style = brush_style
        self.cap_style = cap_style
        self.join_style = join_style

    def incrementWidth(self):
        result = self.radius + 1
        self.radius = result if result < self.maxWidth else self.maxWidth

    def decrementWidth(self):
        result = self.radius - 1
        self.radius = result if result >= 1 else 1

    def pen(self):
        pen = QtGui.QPen()
        pen.setStyle(self.brush_style)
        pen.setWidth(self.radius)
        pen.setColor(self.color)
        pen.setCapStyle(self.cap_style)
        pen.setJoinStyle(self.join_style)
        return pen

class Utensils(Utensil, Enum):
    PEN = (Qt.black, 4)
    ERASER = (Qt.white, 4)

class Canvas(QLabel):
    stopped_writing = pyqtSignal()
    scrolled = pyqtSignal(QtGui.QWheelEvent)
    mouse_grab = pyqtSignal(QPoint)
    def __init__(self):
        super(Canvas, self).__init__()
        self.setStyleSheet("background-color: black")
        master_canvas_layer = QtGui.QPixmap(self.size())
        master_canvas_layer.fill(Qt.white)
        self.activeLayers = []
        self.activeLayers.append(master_canvas_layer)
        self.inactiveLayers = []
        self.last_save = None
        self.startSize = None
        self.setPixmap(self.activeLayers[0])
        ########### Writing parameters ###########
        # General utensil parameters
        self.utensil_press = False
        self.current_utensil = Utensils.PEN
        # Scrolling Parameters
        self.mouse_button_scrolling = False
        # Pen default parameters
        self.pen_lastPoint = QtCore.QPoint()
        # Eraser default parameters
        self.eraser_lastPoint = QtCore.QPoint()
        self.cursor = QtGui.QCursor()
        self.cursor.setShape(Qt.CrossCursor)
        self.setCursor(self.cursor)
        # Painters
        self.painter = QPainter()
        self.layer_painter = QPainter()

    def resizeLayer(self, i, size, active=True):
        temp = self.activeLayers[i] if active else self.inactiveLayers[i]
        if temp.size() == size:
            return
        if active:
            self.activeLayers[i] = QtGui.QPixmap(size)
            self.activeLayers[i].fill(Qt.transparent if i != 0 else Qt.white)
            self.layer_painter.begin(self.activeLayers[i])
        else:
            temp = self.inactiveLayers[i]
            self.inactiveLayers[i] = QtGui.QPixmap(size)
            self.inactiveLayers[i].fill(Qt.transparent)
            self.layer_painter.begin(self.inactiveLayers[i])
        self.layer_painter.drawPixmap(temp.rect(), temp, temp.rect())
        self.layer_painter.end()

    def resizeCanvas(self, size):
        temp = self.activeLayers[0]
        self.activeLayers[0] = QtGui.QPixmap(size)
        self.activeLayers[0].fill(Qt.white)
        self.painter = QtGui.QPainter(self.activeLayers[0])
        self.painter.drawPixmap(self.activeLayers[0].rect(), temp, temp.rect())
        self.painter.end()
        self.setPixmap(self.activeLayers[0])

        for i in range (0, len(self.activeLayers)):
            self.resizeLayer(i, self.size())

        if self.last_save is None:
            self.startSize = self.size()
            self.last_save = self.activeLayers[0].toImage()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        if self.activeLayers[0].size() != self.size():
            self.resizeCanvas(event.size())

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.utensil_press = True
            new_canvas_layer = QtGui.QPixmap(self.size())
            new_canvas_layer.fill(Qt.transparent)

            self.painter.begin(new_canvas_layer)
            self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            self.painter.setPen(self.current_utensil.pen())
            self.painter.drawPoint(event.pos())

            self.activeLayers.append(new_canvas_layer)
            self.last_point_draw = event.pos()
            self.update()
            self.painter.end()
        elif event.button() == Qt.MiddleButton:
            self.setCursor(Qt.ClosedHandCursor)
            self.last_point_scroll = event.globalPos()
            self.mouse_button_scrolling = True
        else:
            super(Canvas, self).mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.buttons() and Qt.LeftButton and self.utensil_press:
            x = self.width() - event.pos().x()
            y = self.height() - event.pos().y()
            if x < 200:
                if y < 200:
                    self.resizeLayer(-1, QSize(self.width() + 100, self.height() + 100))
                    self.resizeCanvas(QSize(self.width() + 100, self.height()))
                else:
                    self.resizeLayer(-1, QSize(self.width() + 100, self.height()))
                    self.resizeCanvas(QSize(self.width() + 100, self.height()))
            elif y < 200:
                self.resizeLayer(-1, QSize(self.width(), self.height() + 100))
                self.resizeCanvas(QSize(self.width(), self.height() + 100))
            self.painter.begin(self.activeLayers[len(self.activeLayers) - 1])
            self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            self.painter.setPen(self.current_utensil.pen())
            self.painter.drawLine(self.last_point_draw, event.pos())
            self.last_point_draw = event.pos()
            self.update()
            self.painter.end()
        elif event.buttons() and Qt.MiddleButton and self.mouse_button_scrolling:
            offset = self.last_point_scroll - event.globalPos()
            self.last_point_scroll = event.globalPos()
            self.mouse_grab.emit(offset)
        else:
            super(Canvas, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.utensil_press = False
            self.stopped_writing.emit()
        elif event.button() == Qt.MiddleButton:
            self.setCursor(self.cursor)
            self.mouse_button_scrolling = False

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        self.scrolled.emit(event)

    def paintEvent(self, event):
        self.activeLayers[0].fill(Qt.white)
        self.layer_painter.begin(self.activeLayers[0])
        for i in range(1, len(self.activeLayers)):
            self.layer_painter.drawPixmap(self.activeLayers[0].rect(), self.activeLayers[i])
        self.layer_painter.end()
        self.setPixmap(self.activeLayers[0])
        super(Canvas, self).paintEvent(event)

    def hasChanged(self):
        self.update()
        if self.last_save is None:
            return False
        return not self.activeLayers[0].toImage() == self.last_save

    def save(self, file_path):
        self.update()
        self.activeLayers[0].save(file_path)
        self.last_save = self.activeLayers[0].toImage()

    def setUtensil(self, utensil : Utensil):
        self.current_utensil = utensil

    # Button click handling
    def clear(self):
        # Reset canvas
        clear_canvas_layer = QtGui.QPixmap(self.size())
        clear_canvas_layer.fill(Qt.white)
        self.activeLayers.append(clear_canvas_layer)
        self.update()
        self.resizeCanvas(self.startSize)
        # Reset back to pen tool
        self.setUtensil(Utensils.PEN)

    def undo(self):
        if len(self.activeLayers) > 1:
            self.inactiveLayers.append(self.activeLayers.pop())
        self.update()

    def redo(self):
        if len(self.inactiveLayers) > 0:
            self.activeLayers.append(self.inactiveLayers.pop())
        self.update()

    def loadImage(self, file_path):
        image_pixmap = QtGui.QPixmap(file_path)
        canvas = QtGui.QPixmap(self.minimumSize().expandedTo(image_pixmap.size()))
        blank = QtGui.QPixmap(canvas.size())
        blank.fill(Qt.white)
        self.activeLayers = [blank, canvas]
        self.inactiveLayers.clear()
        self.painter.begin(canvas)
        self.painter.drawPixmap(canvas.rect(), image_pixmap, image_pixmap.rect())
        self.painter.end()
        self.resizeCanvas(self.activeLayers[0].size())
        self.update()
        self.last_save = self.activeLayers[0].toImage()

class CanvasWindow(QScrollArea):
    def __init__(self):
        super(CanvasWindow, self).__init__()
        self.setWidgetResizable(True)
        self.layout = QVBoxLayout()
        self.label = Canvas()
        self.label.scrolled.connect(self.scrollForLabel)
        self.label.mouse_grab.connect(self.mouseGrabScroll)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.addWidget(self.label, Qt.AlignTop | Qt.AlignLeft)

        self.setWidget(self.label)
        self.setLayout(self.layout)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    def mouseGrabScroll(self, offset):
        x = self.horizontalScrollBar().value() + offset.x()
        y = self.verticalScrollBar().value() + offset.y()
        self.horizontalScrollBar().setValue(x)
        self.verticalScrollBar().setValue(y)

    def scrollForLabel(self, event: QtGui.QWheelEvent):
        hval = self.horizontalScrollBar().value()
        vval = self.verticalScrollBar().value()
        newx = hval - (event.angleDelta().x() / (8 * 15)) * self.horizontalScrollBar().singleStep()
        newy = vval - (event.angleDelta().y() / (8 * 15)) * self.verticalScrollBar().singleStep()
        hmin = self.horizontalScrollBar().minimum()
        hmax = self.horizontalScrollBar().maximum()
        if hmin < newx < hmax:
            self.horizontalScrollBar().setValue(newx)
        elif hmin >= newx:
            self.horizontalScrollBar().setValue(hmin)
        elif hmax <= newx:
            self.horizontalScrollBar().setValue(hmax)
        ymin = self.verticalScrollBar().minimum()
        ymax = self.verticalScrollBar().maximum()
        if ymin < newy < ymax:
            self.verticalScrollBar().setValue(newy)
        elif ymin >= newy:
            self.verticalScrollBar().setValue(ymin)
        elif ymax <= newy:
            self.verticalScrollBar().setValue(ymax)

class UIMainCanvasWindow(QWidget):
    def __init__(self):
        super(UIMainCanvasWindow, self).__init__()
        self.hasSaved = False
        ########### Menu Bar ###########
        self.menu_bar = QtWidgets.QMenuBar(self)
        self.file_menu = self.menu_bar.addMenu("File")
        # Open
        self.open_option = QtWidgets.QAction("Open", self)
        self.open_option.setShortcut("Ctrl+O")
        self.open_option.triggered.connect(self.open)
        self.file_menu.addAction(self.open_option)
        # Save
        self.save_option = QtWidgets.QAction("Save", self)
        self.save_option.setShortcut("Ctrl+S")
        self.save_option.triggered.connect(self.save)
        self.file_menu.addAction(self.save_option)
        # Save As
        self.save_as_option = QtWidgets.QAction("Save As")
        self.save_as_option.setShortcut("Ctrl+Shift+S")
        self.save_as_option.triggered.connect(self.save_as)
        self.file_menu.addAction(self.save_as_option)

        ########### Layout ############
        # Main Window
        self.setMinimumSize(1200, 600)
        self.canvas_window = CanvasWindow()
        self.canvas_window.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.canvas_window.label.stopped_writing.connect(self.run_ai)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.addWidget(self.canvas_window, Qt.AlignTop)
        # Buttons
        self.button_layout = QGridLayout()
        self.button_layout.setContentsMargins(10,10,10,10)
        # Pen Button
        self.pen_button = QtWidgets.QPushButton("Pen", self)
        self.pen_button.setDisabled(False)
        self.pen_button.clicked.connect(self.pen)
        self.button_layout.addWidget(self.pen_button, 0, 0)
        # Eraser Button
        self.eraser_button = QtWidgets.QPushButton("Eraser", self)
        self.eraser_button.clicked.connect(self.erase)
        self.button_layout.addWidget(self.eraser_button, 0, 1)
        # Clear Button
        self.clear_button = QtWidgets.QPushButton("Clear All", self)
        self.clear_button.setToolTip("Clear any writing")
        self.clear_button.clicked.connect(self.canvas_window.label.clear)
        self.button_layout.addWidget(self.clear_button, 0, 2)

        self.layout.addLayout(self.button_layout, Qt.AlignBottom)
        self.setLayout(self.layout)
        self.layout.setMenuBar(self.menu_bar)

    ########### Button Handling ###########
    def erase(self):
        self.canvas_window.label.setUtensil(Utensils.ERASER)
        self.eraser_button.setDisabled(True)
        self.pen_button.setEnabled(True)

    def pen(self):
        self.canvas_window.label.setUtensil(Utensils.PEN)
        self.pen_button.setDisabled(True)
        self.eraser_button.setEnabled(True)

    ########### Keyboard Handling #########
    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key_BracketLeft:
            for u in Utensils:
                u.decrementWidth()
        elif event.key() == Qt.Key_BracketRight:
            for u in Utensils:
                u.incrementWidth()
        elif event.key() == Qt.Key_Z and event.modifiers() == Qt.ControlModifier:
            self.canvas_window.label.undo()
        elif event.key() == Qt.Key_Y and event.modifiers() == Qt.ControlModifier:
            self.canvas_window.label.redo()

    ########### Closing ###########
    def closeEvent(self, event):
        if self.canvas_window.label.hasChanged():
            self.save_popup()

    ########### Saving ###########
    def save(self):
        if self.hasSaved and self.file_path is not None:
            self.canvas_window.label.save(self.file_path)
        else:
            self.save_as()

    def save_as(self):
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Equation", "equation.jpg", "JPG (*.jpg);;PNG (*.png)")
        if file_path == "":
            return
        self.file_path = file_path
        # Saving canvas
        self.canvas_window.label.save(self.file_path)
        self.setWindowTitle(self.file_path)

    def save_popup(self):
        result = SavePrompt().exec_()
        if result:
            self.save()
            self.hasSaved = True

    # Opening
    def open(self):
        if self.canvas_window.label.hasChanged():
            self.save_popup()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "/home", "JPG (*.jpg);;PNG (*.png)")
        if file_path == "":
            return
        if not os.path.isfile(file_path):
            error = QMessageBox()
            error.setText("Error: File does not exist.")
            error.exec_()
        else:
            self.file_path = file_path
            self.canvas_window.label.loadImage(file_path)
            self.setWindowTitle(file_path)

    def run_ai(self):
        # Seems dumb but im going to do an async wait here later
        self.ai()

    def ai(self):
        # if not self.hasSaved:
        #     self.save()
        # imageProcessor.load_img(self.file_path)
        pass

class SavePrompt(QDialog):
    def __init__(self):
        super(SavePrompt, self).__init__()
        self.setWindowTitle("Save for later?")
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(super(SavePrompt, self).accept)
        buttonBox.rejected.connect(super(SavePrompt, self).reject)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(buttonBox)
        self.setLayout(layout)
        self.setFixedSize(layout.minimumSize())