from PyQt5.QtWidgets import (QWidget, QFrame, QFileDialog,
                             QVBoxLayout, QHBoxLayout, QSizePolicy,
                             QGridLayout)

from qfluentwidgets import BodyLabel, PrimaryPushButton, SpinBox, DoubleSpinBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PyQt5.QtCore import Qt, QSize, QEvent, pyqtSignal

import numpy as np
import GUI.qss
import GUI.data
from importlib.resources import path

from .utility import setFont
from .combox_ import ComboBox_ as ComboBox
from ..project import Project as Pro

class DisplaySA(QFrame):
    
    ratioEmit=pyqtSignal(float)
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        vMainLayout=QVBoxLayout(self)
        vMainLayout.setContentsMargins(0, 20, 0, 20)
        
        h=QHBoxLayout()
        label=BodyLabel("Sensitivity Analysis Result File:")
        setFont(label)
        
        self.resultFile=ComboBox(self)
        self.resultFile._showComboMenu=self.dynamicShowFile
        self.resultFile.setFixedWidth(300)
        setFont(self.resultFile)
        
        self.drawBtn=PrimaryPushButton("Draw", self)
        setFont(self.drawBtn)
        self.drawBtn.clicked.connect(self.drawResult)
        
        h.addSpacing(20);h.addWidget(label); h.addWidget(self.resultFile); h.addSpacing(10); h.addWidget(self.drawBtn);h.addStretch(1)
        
        vMainLayout.addLayout(h)
        
        self.w=QWidget()
        v=QVBoxLayout(self.w)
        self.canvas = MplCanvas(width=16, height=9)
        
        v.addWidget(self.canvas, Qt.AlignmentFlag.AlignCenter)
   
        self.w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        h=QHBoxLayout()
        self.operation=Operation(self.canvas, self)
        h.addWidget(self.w); h.addWidget(self.operation)
        vMainLayout.addLayout(h)
        
        self.canvas.ratioEmit.connect(self.operation.setRatio)
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        h=QHBoxLayout(); h.setContentsMargins(0, 5, 0, 5)
        self.saveFigBtn=PrimaryPushButton("Save Figure", self)
        self.saveFigBtn.setMinimumWidth(150)
        setFont(self.saveFigBtn)
        self.reset=PrimaryPushButton("Reset", self)
        self.reset.setMinimumWidth(150)
        setFont(self.reset)
        h.addStretch(1); h.addWidget(self.saveFigBtn);h.addSpacing(20); h.addWidget(self.reset) ;h.addStretch(1)
        
        self.saveFigBtn.clicked.connect(self.saveFig)
        
        vMainLayout.addLayout(h)
        
        with path(GUI.qss, "display.qss") as qss_path:
            with open(qss_path, 'r') as f:
                self.setStyleSheet(f.read())
        
    def saveFig(self):
        
        fileName, type = QFileDialog.getSaveFileName(self, "Save Figure", "", "PNG (*.png);;PDF (*.pdf);;SVG (*.svg);;EPS (*.eps)")

        suffix = type.split('.')[-1].strip(')')
        self.canvas.saveFig(fileName, suffix)
        
    def dynamicShowFile(self):
        
        self.resultFile.clear()
        self.resultFile.addItems(Pro.findResultFile())
        self.resultFile.setCurrentIndex(0)
        super(ComboBox, self.resultFile)._showComboMenu()
        
    def drawResult(self):
        
        fileName=self.resultFile.currentText()
        self.SAData=Pro.loadSAFile(fileName)
        del self.SAData['S1']['matrix']
        self.operation.data=self.SAData['S1']
        self.canvas.plot_parameters(self.SAData['S1'])

        
class Operation(QWidget):
    
    def __init__(self, picture, parent=None):
        super().__init__(parent)
        
        self.controls=[]
        
        self.picture=picture
    
        self.setSizePolicy(QSizePolicy.Fixed,  QSizePolicy.Expanding)
        
        vMainLayout=QGridLayout(self)
        
        label=BodyLabel("Font Size:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        
        self.labelSize=SpinBox(self)
        self.labelSize.setProperty('name', 'labelSize')
        self.labelSize.setProperty('type', 'int')
        self.labelSize.setValue(12)
        self.controls.append(self.labelSize)
        setFont(self.labelSize)
        
        vMainLayout.addWidget(label, 0, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.labelSize, 0, 1, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("Box Width:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        
        self.boxWidth=SpinBox(self)
        self.boxWidth.setProperty('name', 'boxWidth')
        self.boxWidth.setValue(2)
        self.boxWidth.setProperty('type', 'int')
        self.controls.append(self.boxWidth)
        setFont(self.boxWidth)
        
        vMainLayout.addWidget(label, 1, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.boxWidth, 1, 1, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("Bar Width:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.barWidth=DoubleSpinBox(self)
        self.barWidth.setRange(0.1, 1.0)
        self.barWidth.setSingleStep(0.1)
        self.barWidth.setValue(0.5)
        self.barWidth.setProperty('name', 'barWidth')
        self.barWidth.setProperty('type', 'float')
        self.controls.append(self.barWidth)
        setFont(self.barWidth)
        
        vMainLayout.addWidget(label, 2, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.barWidth, 2, 1, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("Bar Spacing:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.barSpacing=DoubleSpinBox(self)
        self.barSpacing.setRange(0.1, 1.0)
        self.barSpacing.setSingleStep(0.1)
        self.barSpacing.setProperty('name', 'barSpacing')
        self.barSpacing.setProperty('type', 'float')
        self.barSpacing.setValue(1.0)
        self.controls.append(self.barSpacing)
        setFont(self.barSpacing)
        
        vMainLayout.addWidget(label, 3, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.barSpacing, 3, 1, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("Edge Width:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.edgeWidth=SpinBox(self)
        self.edgeWidth.setProperty('name', 'edgeWidth')
        self.edgeWidth.setProperty('type', 'int')
        self.edgeWidth.setValue(1)
        self.controls.append(self.edgeWidth)
        setFont(self.edgeWidth)
        
        vMainLayout.addWidget(label, 4, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.edgeWidth, 4, 1, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("yMaxLimit:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.yMaxLimit=DoubleSpinBox(self)
        self.yMaxLimit.setRange(0.1, 1.0)
        self.yMaxLimit.setSingleStep(0.1)
        self.yMaxLimit.setProperty('name', 'yMaxLimit')
        self.yMaxLimit.setProperty('type', 'float')
        self.yMaxLimit.setValue(1.0)
        self.controls.append(self.yMaxLimit)
        setFont(self.yMaxLimit)
        
        vMainLayout.addWidget(label, 5, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.yMaxLimit, 5, 1, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("Label Rotation:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.xRotation=SpinBox(self)
        self.xRotation.setRange(0, 90)
        self.xRotation.setProperty("name", 'xRotation')
        self.xRotation.setProperty("type", 'int')
        self.xRotation.setValue(0)
        self.controls.append(self.xRotation)
        setFont(self.xRotation)
        
        vMainLayout.addWidget(label, 6, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.xRotation, 6, 1, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("Figure Ratio:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.figWidth=DoubleSpinBox(self)
        self.figWidth.setProperty('name', 'figRatio')
        self.figWidth.setProperty('type', 'float')
        self.figWidth.setValue(1.0)
        self.figWidth.setRange(0.0, 1.0)
        self.figWidth.setSingleStep(0.1)
        self.controls.append(self.figWidth)
        setFont(self.figWidth)
        
        vMainLayout.addWidget(label, 7, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.figWidth, 7, 1, Qt.AlignmentFlag.AlignVCenter)
        
        self.refreshBtn=PrimaryPushButton("Refresh", self)
        setFont(self.refreshBtn)
        self.refreshBtn.clicked.connect(self.refresh)
        vMainLayout.addWidget(self.refreshBtn, 8, 0, 1, 2)
    
    def setRatio(self, value):
        
        self.figWidth.setValue(value)

        
    def refresh(self):
        
        hyper={}
        
        for control in self.controls:
            
            type=control.property('type')
            if type=='int' or type=='float':
                hyper[control.property('name')] = control.value()
                
        self.picture.plot_parameters(self.data, **hyper)
        self.parent().w.update()
        
class MplCanvas(FigureCanvas):
    
    ratioEmit=pyqtSignal(float)
    
    def __init__(self, width=16, height=9, dpi=300):

        self.saveDpi=dpi
        self.fig = Figure(figsize=(width, height), dpi=100)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        
    def plot_parameters(self, SAData, barWidth=0.5, boxWidth=2, yMaxLimit=1.0, barSpacing=1.0,
                        labelSize=12, edgeWidth=1, xRotation=0, figRatio=1.0):
        
        # w, h=self.fig.get_size_inches()
        # h=w/(self.ratio/figRatio)
        # self.fig.set_size_inches(w, h)
        # self.draw()
        self.axes.clear()  # Clear existing plot
        
        name=list(SAData.keys())
        value=list(SAData.values())

        heights= list(map(abs, value))
        labels=name
        
        bar_width = barWidth
        spacing = barSpacing
        indices = np.arange(len(labels)) * (bar_width + spacing)

        self.axes.bar(indices, heights, width=bar_width, tick_label=labels, edgecolor='black', linewidth=edgeWidth)
        self.axes.set_ylim(0, yMaxLimit) 

        self.axes.set_xlim(-bar_width, max(indices) + bar_width)
        
        self.axes.tick_params(axis='both', direction='in', width=2, 
                              labelsize=labelSize)

        for spine in self.axes.spines.values():
            spine.set_linewidth(boxWidth)
        
        self.axes.set_xticklabels(labels, rotation=xRotation, fontweight='bold')
        plt.setp(self.axes.get_yticklabels(), fontweight='bold')
        
        delta=(1.1-figRatio)/2
        self.axes.set_position([0.05, delta, 0.9, figRatio-0.1])
        self.figure.canvas.draw_idle()
        # self.fig.tight_layout()
        # self.draw()
              
    def saveFig(self, path, suffix):
        
        self.fig.savefig(path, format=suffix, dpi=self.saveDpi)
    
    def resizeEvent(self, event):

        self.canvas_width, self.canvas_height=self.get_width_height()
        self.ratio=self.canvas_width/self.canvas_height
        self.ratioEmit.emit(1.0) 
        super(MplCanvas, self).resizeEvent(event)
        
        