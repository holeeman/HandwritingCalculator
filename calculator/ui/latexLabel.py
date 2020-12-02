'''
@date: December 2 2020
@description: Latex Label class
'''

from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPixmap, QPainter, QImage, QPen, QFont
from PyQt5.QtCore import Qt, QPoint, QBuffer, QThreadPool
from matplotlib import figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

class LatexLabel(QLabel):
    def __init__(self, text, parent):
        super(LatexLabel, self).__init__(text, parent)
    
    def setLatexText(self, text):
        '''
            I modified the code I got from https://stackoverflow.com/questions/32035251/displaying-latex-in-pyqt-pyside-qtablewidget
            by Jean-Sébastien
        '''
        if text == '':
            self.setPixmap(QPixmap())
            return
        fig = figure.Figure()
        fig.patch.set_facecolor('none')
        fig.set_canvas(FigureCanvasAgg(fig))
        renderer = fig.canvas.get_renderer()

        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')
        ax.patch.set_facecolor('none')
        if text[:14] == '<function sqrt':
            text = "sqrt"
        text = "$" + text + "$"
        t = ax.text(0, 0, text.encode('unicode_escape').decode().replace('\\\\', '\\'), ha='left', va='bottom', fontsize=16)
        
        fw, fh = fig.get_size_inches()
        fig_bbox = fig.get_window_extent(renderer)
        text_bbox = t.get_window_extent(renderer)

        tight_fwidth = text_bbox.width * fw / fig_bbox.width
        tight_fheight = text_bbox.height * fh / fig_bbox.height

        fig.set_size_inches(tight_fwidth, tight_fheight)

        buf, size = fig.canvas.print_to_buffer()
        qimage = QImage.rgbSwapped(QImage(buf, size[0], size[1], QImage.Format_ARGB32))
        qpixmap = QPixmap(qimage)

        self.setPixmap(qpixmap)