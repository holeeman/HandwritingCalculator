from PyQt5.QtWidgets import QApplication, QAction, QPushButton, QMainWindow, QListView, QLabel, QWidget
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPixmap, QPainter, QImage, QPen, QFont
from PyQt5.QtCore import Qt, QPoint, QBuffer
import sys, io

class CalculatorGUI(QWidget):
    canvasSize = (1000,600)
    canvasPosition = (0, 0)
    toolSpace = (0, 100)
    toolStartX = canvasSize[0] + canvasPosition[0]
    toolStartY = canvasSize[1] + canvasPosition[1]

    buttonSize = (150, 40)
    buttonPosition = (toolStartX-buttonSize[0]-20, toolStartY + 20)

    exprLabelSize = (500, 40)
    exprLabelPosition = (20, toolStartY + 20)

    ansLabelSize = (270, 40)
    ansLabelPosition = (40 + exprLabelSize[0], toolStartY + 20)

    
    def __init__(self):
        super().__init__()
        self.evaluator = None
        self.setWindowTitle("Handwriting Calculator")
        self.setGeometry(100, 100,
            CalculatorGUI.toolStartX + CalculatorGUI.toolSpace[0], CalculatorGUI.toolStartY + CalculatorGUI.toolSpace[1])

        # canvas
        self.image_pos = CalculatorGUI.canvasPosition
        self.image_size = CalculatorGUI.canvasSize
        imw, imh = self.image_size
        self.drawing = False
        self.mouse_pos = QPoint()
        self.image = QImage(imw, imh, QImage.Format_RGB32)
        self.image.fill(Qt.white)

        # clear button
        self.button = QPushButton('clear', self)
        self.button.clicked.connect(self.clear)
        self.button.resize(CalculatorGUI.buttonSize[0], CalculatorGUI.buttonSize[1])
        self.button.move(CalculatorGUI.buttonPosition[0], CalculatorGUI.buttonPosition[1])

        # math expression label
        self.label = QLabel("", self)
        self.label.resize(CalculatorGUI.exprLabelSize[0], CalculatorGUI.exprLabelSize[1])
        self.label.move(CalculatorGUI.exprLabelPosition[0], CalculatorGUI.exprLabelPosition[1])
        self.label.setFont(QFont("Courier", 15))
        self.label.setStyleSheet("background: white;qproperty-alignment: AlignCenter;")
        self.label.alignment()

        # math evaluation label
        self.ansLabel = QLabel("", self)
        self.ansLabel.resize(CalculatorGUI.ansLabelSize[0],CalculatorGUI.ansLabelSize[1])
        self.ansLabel.move(CalculatorGUI.ansLabelPosition[0], CalculatorGUI.ansLabelPosition[1])
        self.ansLabel.setFont(QFont("Courier", 15, 100))
        self.ansLabel.setStyleSheet("background: white;qproperty-alignment: AlignCenter;")
        self.idassign = 0
        
        self.show()
    
    def setExprLabel(self, txt):
        self.label.setText(txt)
    
    def setAnsLabel(self, txt):
        self.ansLabel.setText(txt)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            ix, iy, iw, ih = *self.image_pos, *self.image_size
            mx, my = event.pos().x(), event.pos().y()
            if mx < ix or mx > ix + iw or my < iy or my > iy + ih:
                return
        self.drawing = True
        self.mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.drawing and event.buttons() and Qt.LeftButton:
            painter = QPainter(self.image)
            painter.setPen(QPen(Qt.black, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.mouse_pos, event.pos())
            self.mouse_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
        self.evaluate()

    def paintEvent(self, event):
        x, y = self.image_pos
        canvasPainter = QPainter(self) 
        canvasPainter.drawImage(x, y, self.image)
    
    def setEvaluator(self, evaluator):
        self.evaluator = evaluator
    
    def evaluate(self):
        if self.evaluator:
            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)
            self.image.save(buffer, "PNG")
            result = self.evaluator(io.BytesIO(buffer.data()))
            parsed, evaluated = result
            self.setExprLabel(parsed)
            self.setAnsLabel(str(evaluated))
    
    def clear(self):
        self.image.fill(Qt.white)
        self.label.setText("")
        self.ansLabel.setText("")
        self.update()

def run_gui(app, window):
    app.exec_()
    window.show()
def init_gui():
    app = QApplication(sys.argv)
    window = CalculatorGUI()
    return app, window

if __name__ == "__main__":
    app, window = init_gui()
    run_gui(app, window)