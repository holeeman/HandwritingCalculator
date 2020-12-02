from PyQt5.QtWidgets import QApplication, QAction, QPushButton, QMainWindow, QListView, QLabel, QWidget, QCheckBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPixmap, QPainter, QImage, QPen, QFont
from PyQt5.QtCore import Qt, QPoint, QBuffer, QThreadPool
from .worker import OnDrawAsyncWorker
from .latexLabel import LatexLabel
from sympy import sympify
from sympy.printing import latex
import io
import sys
import time

class CalculatorWidget(QWidget):
    canvasSize = (1000,500)
    canvasPosition = (0, 0)
    toolSpace = (0, 150)
    toolStartX = canvasSize[0] + canvasPosition[0]
    toolStartY = canvasSize[1] + canvasPosition[1]
    toolMarginW = 20
    toolMarginH = 20

    exprLabelSize = (580, 80)
    exprLabelPosition = (toolMarginW, toolStartY + toolMarginH)

    ansLabelSize = (200, 80)
    ansLabelPosition = (toolMarginW + exprLabelPosition[0] + exprLabelSize[0], toolStartY + toolMarginH)

    buttonSize = (140, 80)
    buttonPosition = (toolMarginW + ansLabelPosition[0] + ansLabelSize[0], toolStartY + toolMarginH)

    latexTogglePosition = (toolMarginW, toolStartY + toolMarginH + buttonSize[1] + toolMarginH)

    asyncTogglePosition = (toolMarginW + 100, toolStartY + toolMarginH + buttonSize[1] + toolMarginH)

    useAsync = True
    useLatex = True

    
    def __init__(self, useAsync=True, useLatex=True):
        super().__init__()
        self.initGui(useAsync, useLatex)

        # canvas
        self.initCanvas()

        # clear button
        self.initButton()

        # math expression label
        self.initExprLabel()

        # math evaluation label
        self.initAnsLabel()

        # use latex toggle
        self.initLatexToggle()

        # use async toggle
        self.initAsyncToggle()

        # debug
        self.initDebug()
        
        self.show()
    
    def initGui(self, useAsync, useLatex):
        self.setWindowTitle("Handwriting Calculator")
        self.setGeometry(
            100, 
            100,
            self.toolStartX + self.toolSpace[0], 
            self.toolStartY + self.toolSpace[1])
        self.useAsync = useAsync
        self.useLatex = useLatex
    
    def initCanvas(self):
        self.onDraw = None
        self.image_pos = self.canvasPosition
        self.image_size = self.canvasSize
        imw, imh = self.image_size
        self.drawing = False
        self.mouse_pos = QPoint()
        self.image = QImage(imw, imh, QImage.Format_RGB32)
        self.image.fill(Qt.white)

    def initButton(self):
        self.button = QPushButton('clear', self)
        self.button.clicked.connect(self.clear)
        self.button.resize(self.buttonSize[0], self.buttonSize[1])
        self.button.move(self.buttonPosition[0], self.buttonPosition[1])

    def initExprLabel(self):
         # math expression label
        self.label = LatexLabel("", self)
        self.label.resize(self.exprLabelSize[0], self.exprLabelSize[1])
        self.label.move(self.exprLabelPosition[0], self.exprLabelPosition[1])
        self.label.setFont(QFont("Courier", 15))
        self.label.setStyleSheet("background: white;qproperty-alignment: AlignCenter;")
        self.label.alignment()
    
    def initAnsLabel(self):
        # math evaluation label
        self.ansLabel = LatexLabel("", self)
        self.ansLabel.resize(self.ansLabelSize[0],self.ansLabelSize[1])
        self.ansLabel.move(self.ansLabelPosition[0], self.ansLabelPosition[1])
        self.ansLabel.setFont(QFont("Courier", 15, 100))
        self.ansLabel.setStyleSheet("background: white;qproperty-alignment: AlignCenter;")
        self.idassign = 0
    
    def initLatexToggle(self):
        self.latexToggle = QCheckBox("use latex",self)
        self.latexToggle.setChecked(self.useLatex)
        self.latexToggle.stateChanged.connect(self.toggleLatex)
        self.latexToggle.move(self.latexTogglePosition[0], self.latexTogglePosition[1])

    def initAsyncToggle(self):
        self.latexToggle = QCheckBox("use async",self)
        self.latexToggle.setChecked(self.useAsync)
        self.latexToggle.stateChanged.connect(self.toggleAsync)
        self.latexToggle.move(self.asyncTogglePosition[0], self.asyncTogglePosition[1])
    
    def initDebug(self):
        self.startTime = time.time()

    def setDebugStartTime(self):
        self.startTime = time.time()

    def printDebugExecTime(self):
        print(time.time() - self.startTime)
    
    def toggleLatex(self):
        self.useLatex = not self.useLatex
        self.triggerOnDraw()
    
    def toggleAsync(self):
        self.useAsync = not self.useAysnc
    
    def setExprLabel(self, txt):
        if self.useLatex:
            self.label.setLatexText(str(txt))
        else:
            self.label.setText(str(txt))
    
    def setAnsLabel(self, txt):
        if self.useLatex:
            self.ansLabel.setLatexText(str(txt))
        else:
            self.ansLabel.setText(str(txt))

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
        self.triggerOnDraw()

    def paintEvent(self, event):
        x, y = self.image_pos
        canvasPainter = QPainter(self) 
        canvasPainter.drawImage(x, y, self.image)
    
    def setOnDraw(self, func):
        self.onDraw = func

    def runOnDrawAsync(self, img):
        thread_pool = QThreadPool.globalInstance()
        worker = OnDrawAsyncWorker(self.onDraw, img)
        worker.signals.result.connect(self.afterOnDraw)
        thread_pool.start(worker)
    
    def triggerOnDraw(self):
        if self.onDraw:
            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)
            self.image.save(buffer, "PNG")
            self.setDebugStartTime()
            if self.useAsync:
                self.runOnDrawAsync(io.BytesIO(buffer.data()))
            else:
                self.afterOnDraw(self.onDraw(io.BytesIO(buffer.data())))
    
    def afterOnDraw(self, result):
        self.printDebugExecTime()
        expr, ans = result
        try:
            expr = latex(sympify(expr, evaluate=False)) if self.useLatex else expr
        except:
            pass
        try:
            ans = latex(sympify(ans, evaluate=False)) if self.useLatex else ans
        except:
            pass
        self.setExprLabel(expr)
        self.setAnsLabel(ans)
    
    def clear(self):
        self.image.fill(Qt.white)
        if self.useLatex:
            self.label.setLatexText("")
            self.ansLabel.setLatexText("")
        else:
            self.label.setText("")
            self.ansLabel.setText("")
        self.update()


class GUICalculatorApplication(QApplication):
    def __init__(self, useAsync=True, useLatex=True):
        self.app = QApplication(sys.argv)
        self.window = CalculatorWidget(useAsync, useLatex)
    
    def connect(self, method):
        self.window.setOnDraw(method)
    
    def run(self):
        self.app.exec_()
        self.window.show()

if __name__ == "__main__":
    calculator = GUICalculatorApplication()
    calculator.connect(lambda x: ("1/2 + 3 ** 2", "9.5"))
    calculator.run()