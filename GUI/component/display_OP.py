from PyQt5.QtWidgets import (QWidget, QFrame, QFileDialog, QLabel, QPushButton,
                             QVBoxLayout, QHBoxLayout, QSizePolicy,
                             QGridLayout, QFormLayout)

from qframelesswindow import FramelessDialog
from qfluentwidgets import (BodyLabel, PushButton, PrimaryPushButton, 
                            SpinBox, DoubleSpinBox, ColorDialog,
                            FluentStyleSheet, getStyleSheet)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from PyQt5.QtCore import Qt, QSize, QEvent, pyqtSignal
from PyQt5.QtGui import QColor
import numpy as np
import GUI.qss
import GUI.data
from importlib.resources import path

from .utility import setFont, substitute
from .combox_ import ComboBox_ as ComboBox
from ..project import Project as Pro
from .check_box import CheckBox_ as CheckBox
class DisplayOP(QFrame):
    
    ratioEmit=pyqtSignal(float)
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        hBoxLayout=QHBoxLayout(self)
        
        vMainLayout=QVBoxLayout()
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
        
        vMainLayout.addWidget(self.w)
       
        self.operation=Operation(self.canvas, self)
        
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
        
        hBoxLayout.addLayout(vMainLayout); hBoxLayout.addWidget(self.operation)
        
        with path(GUI.qss, "displayB.qss") as qss_path:
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
        self.OPData=Pro.loadOPFile(fileName)
        self.canvas.show_plot()

        data=self.OPData['History_Best']
        self.operation.data=data
        self.canvas.plot_parameters(data)
            
class Operation(QWidget):
    
    color=QColor('#1f77b4')
    data=None
    keys=None
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
        
        
        label=BodyLabel("Title Size:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.barWidth=SpinBox(self)
        self.barWidth.setRange(1, 20)
        self.barWidth.setSingleStep(1)
        self.barWidth.setValue(13)
        self.barWidth.setProperty('name', 'titleSize')
        self.barWidth.setProperty('type', 'int')
        self.controls.append(self.barWidth)
        setFont(self.barWidth)
        
        vMainLayout.addWidget(label, 1, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.barWidth, 1, 1, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("Legend Size:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.legendSize=SpinBox(self)
        self.legendSize.setProperty('name', 'legendSize')
        self.legendSize.setValue(12)
        self.legendSize.setProperty('type', 'int')
        self.controls.append(self.legendSize)
        setFont(self.legendSize)
        
        vMainLayout.addWidget(label, 2, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.legendSize, 2, 1, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("Box Width:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        
        self.boxWidth=SpinBox(self)
        self.boxWidth.setProperty('name', 'boxWidth')
        self.boxWidth.setValue(2)
        self.boxWidth.setProperty('type', 'int')
        self.controls.append(self.boxWidth)
        setFont(self.boxWidth)
        
        vMainLayout.addWidget(label, 3, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.boxWidth, 3, 1, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("Line Color:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.lineColor=ColorButton(self.color, self)
        self.lineColor.clicked.connect(self.showColorDialog)
        setFont(self.lineColor)
        self.controls.append(self.lineColor)
        self.lineColor.setProperty('name', 'lineColor')
        self.lineColor.setProperty('type', 'txt')
        self.lineColor.setStyleSheet(f"background-color: {self.color.name()}; border: 1px solid rbga(0, 0, 0, 0.073); border-radius: 5px; outline: none;")
        
        vMainLayout.addWidget(label, 4, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.lineColor, 4, 1, Qt.AlignmentFlag.AlignVCenter)
        
        
        label=BodyLabel("Line Width:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.lineWidth=SpinBox(self)
        self.lineWidth.setRange(1, 20)
        self.lineWidth.setSingleStep(1)
        self.lineWidth.setProperty('name', 'lineWidth')
        self.lineWidth.setProperty('type', 'int')
        self.lineWidth.setValue(2)
        self.controls.append(self.lineWidth)
        setFont(self.lineWidth)
        
        vMainLayout.addWidget(label, 5, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.lineWidth, 5, 1, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("Mark Size:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.markSize=SpinBox(self)
        self.markSize.setProperty('name', 'markSize')
        self.markSize.setProperty('type', 'int')
        self.markSize.setRange(0, 20)
        self.markSize.setValue(12)
        self.controls.append(self.markSize)
        setFont(self.markSize)
        
        vMainLayout.addWidget(label, 6, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.markSize, 6, 1, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("Mark Type:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.markType=ComboBox(self)
        self.markType.addItems([".", "o", "v", "s", "x"]) #TODO
        self.markType.setCurrentIndex(0)
        self.markType.setProperty('name', 'markType')
        self.markType.setProperty('type', 'txt')
       
        self.controls.append(self.markType)
        setFont(self.markType)
        
        vMainLayout.addWidget(label, 7, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.markType, 7, 1, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("Every Mark:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.everyMark=DoubleSpinBox(self)
        self.everyMark.setRange(0.01, 1.0)
        self.everyMark.setProperty("name", 'everyMark')
        self.everyMark.setProperty("type", 'float')
        self.everyMark.setSingleStep(0.01)
        self.everyMark.setValue(0.01)
        self.controls.append(self.everyMark)
        setFont(self.everyMark)
        
        vMainLayout.addWidget(label, 8, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.everyMark, 8, 1, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("Figure Ratio:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.figWidth=DoubleSpinBox(self)
        self.figWidth.setProperty('name', 'figRatio')
        self.figWidth.setProperty('type', 'float')
        self.figWidth.setValue(1.0)
        self.figWidth.setRange(0.0, 2.0)
        self.figWidth.setSingleStep(0.1)
        self.controls.append(self.figWidth)
        setFont(self.figWidth)
        
        vMainLayout.addWidget(label, 9, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.figWidth, 9, 1, Qt.AlignmentFlag.AlignVCenter)
        
        # label=BodyLabel("Value Text:")
        # label.setAlignment(Qt.AlignmentFlag.AlignRight)
        # setFont(label)
        # self.valueText=ComboBox(self)
        # self.valueText.addItems(['True', 'False'])
        # self.valueText.setCurrentIndex(0)
        # self.valueText.setProperty('name', 'ifText')
        # self.valueText.setProperty('type', 'bool')
        # setFont(self.valueText)
        # self.controls.append(self.valueText)
        
        # vMainLayout.addWidget(label, 9, 0, Qt.AlignmentFlag.AlignVCenter)
        # vMainLayout.addWidget(self.valueText, 9, 1, Qt.AlignmentFlag.AlignVCenter)
        
        # label=BodyLabel("Bar Selection:")
        # label.setAlignment(Qt.AlignmentFlag.AlignRight)
        # setFont(label)
        # self.barBtn=PushButton("Click to select", self)
        # setFont(self.barBtn)
        # self.barBtn.clicked.connect(self.selectBar)
        # self.barBtn.setProperty('name', 'barIndex')
        # self.barBtn.setProperty('type', 'list')
        # self.controls.append(self.barBtn)
        
        # vMainLayout.addWidget(label, 10, 0, Qt.AlignmentFlag.AlignVCenter)
        # vMainLayout.addWidget(self.barBtn, 10, 1, Qt.AlignmentFlag.AlignVCenter)
        
        # label=BodyLabel("Normalization:")
        # setFont(label)
        # label.setAlignment(Qt.AlignmentFlag.AlignRight)
        # self.norm=ComboBox(self)
        # self.norm.addItems(['True', 'False'])
        # setFont(self.norm)
        # self.norm.setProperty('name', 'ifNorm')
        # self.norm.setProperty('type', 'bool')
        # self.norm.setCurrentIndex(1)
        # self.controls.append(self.norm)
        
        # vMainLayout.addWidget(label, 11, 0, Qt.AlignmentFlag.AlignVCenter)
        # vMainLayout.addWidget(self.norm, 11, 1, Qt.AlignmentFlag.AlignVCenter)
        
        self.refreshBtn=PrimaryPushButton("Refresh", self)
        setFont(self.refreshBtn)
        self.refreshBtn.clicked.connect(self.refresh)
        vMainLayout.addWidget(self.refreshBtn, 10, 0, 1, 2)

    def selectBar(self):
        
        dialog=BarSelector(self.data, self.keys)
        res=dialog.exec()
        
        if res:
            self.keys=dialog.keys

    def setRatio(self, value):
        
        self.figWidth.setValue(value)

    def showColorDialog(self):
        
        w=ColorDialog(self.color, "Choose color", self.window())
        w.exec()
        self.color=w.color
        self.lineColor.setColor(self.color)
        
    def refresh(self):
        
        hyper={}
        
        for control in self.controls:
            
            type=control.property('type')
            if type=='int' or type=='float':
                hyper[control.property('name')] = control.value()
            elif type=='txt':
                hyper[control.property('name')] = control.text()
            elif type=='bool':
                hyper[control.property('name')] = control.currentText() == 'True'
            elif type=='list':
                hyper[control.property('name')] = self.keys
            
        self.picture.plot_parameters(self.data, **hyper)
        self.parent().w.update()
        
class MplCanvas(FigureCanvas):
    
    ratioEmit=pyqtSignal(float)
    
    def __init__(self, width=16, height=9, dpi=300):

        self.saveDpi=dpi
        self.fig = Figure(figsize=(width, height), dpi=100)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        self.clear_plot()
        
    def plot_parameters(self, OPData, boxWidth=2, markType='.', titleSize=15, markSize=12,
                        everyMark=0.01, labelName='Data', ifInverse=True, lineWidth=2,
                        labelSize=12, figRatio=1.0, lineColor='#1f77b4', legendSize=12):
        
        self.axes.clear() 
        x_data=[]
        y_data=[]
        
        for i, (_, value) in enumerate(OPData.items()):
            x_data.append(i)
            y_data.append(value['Best Objectives'])
            
        y_data=np.log(y_data)
        
        if ifInverse:
            y_data=y_data*-1
        min_value, max_value=min(y_data), max(y_data)
        
        # 在初始化时绘制折线图
        self.axes.plot(x_data, y_data, marker=markType, markevery=everyMark, markersize=markSize, linewidth=lineWidth,linestyle='-', color=lineColor, label=labelName)
        self.axes.set_xlabel('Iters', fontsize=titleSize, fontweight='bold')  # 横坐标标签
        self.axes.set_ylabel('Obj', fontsize=titleSize, fontweight='bold')  # 纵坐标标签
        self.axes.legend(prop={'weight': 'bold', 'size': legendSize})
        
        self.axes.set_ylim(min_value, max_value)
        self.axes.set_xlim(0, len(x_data))
        self.axes.tick_params(axis='both', direction='in', width=2, 
                              labelsize=labelSize)
        
        
        # self.axes.tick_params(axis='x', which='both', bottom=False, top=False)

        for spine in self.axes.spines.values():
            spine.set_linewidth(boxWidth)
        
        plt.setp(self.axes.get_yticklabels(), fontweight='bold')
        plt.setp(self.axes.get_xticklabels(), fontweight='bold')
        
        delta=(1.3-figRatio)/2
        self.axes.set_position([0.10, delta, 0.85, figRatio-0.2])
        self.axes.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
        self.axes.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))  # 强制使用科学计数法
        self.figure.canvas.draw_idle()
    
    def clear_plot(self):
        
        self.axes.clear()
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        for spine in self.axes.spines.values():
            spine.set_visible(False)
        
        self.figure.canvas.draw_idle()
    
    def show_plot(self):
        
        self.axes.clear()
        for spine in self.axes.spines.values():
            spine.set_visible(True)
        self.figure.canvas.draw_idle()
        
    
    def saveFig(self, path, suffix):
        
        self.fig.savefig(path, format=suffix, dpi=self.saveDpi)
    
    def resizeEvent(self, event):
        
        self.canvas_width, self.canvas_height=self.get_width_height()
        self.ratio=self.canvas_width/self.canvas_height
        super(MplCanvas, self).resizeEvent(event)
        
class ColorButton(PushButton):
    
    def __init__(self, color, parent=None):
        
        super().__init__(parent)
        
        self.setColor(color)
        self.setFixedHeight(30)
        
    def setColor(self, color):
        
        qss=getStyleSheet(FluentStyleSheet.BUTTON)
        qss=substitute(qss, {"PushButton, ToolButton, ToggleButton, ToggleToolButton": {"background" : f" {color.name()}"}})
        self.setStyleSheet(qss)
        self.setText(color.name())
        self.update()

class BarSelector(FramelessDialog):
    keys=[]
    def __init__(self, data, keys, parent=None):
        
        super().__init__(parent)
        
        self.vMainLayout=QVBoxLayout(self)
        
        titleLabel=BodyLabel("Select Bar")
        setFont(titleLabel)
        self.vMainLayout.addWidget(titleLabel)
        self.vMainLayout.addStretch(1)
        
        self.contentWidget=QWidget(self)
        self.contentWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.contentLayout=QGridLayout(self.contentWidget)
        
        self.boxes=[]
        col=4
        for i, (key, value) in enumerate(data.items()):
            box=CheckBox(key+f"_{value: .2f}")
            if keys is not None:
                if key in keys:
                    box.setChecked(True)
            else:
                box.setChecked(True)
            box.setProperty('key', key)
            self.boxes.append(box)
            self.contentLayout.addWidget(box, i//col, i%col, Qt.AlignmentFlag.AlignLeft)

        self.vMainLayout.addWidget(self.contentWidget)
        self.vMainLayout.addStretch(1)
        
        self.yesBtn=PrimaryPushButton("Confirm", self)
        self.yesBtn.clicked.connect(self.confirm)
        setFont(self.yesBtn)
        self.cancelBtn=PushButton("Cancel", self)
        self.cancelBtn.clicked.connect(self.cancel)
        setFont(self.cancelBtn)
        
        h=QHBoxLayout()
        h.addStretch(1); h.addWidget(self.yesBtn); h.addSpacing(20); h.addWidget(self.cancelBtn); h.addStretch(1)
        self.vMainLayout.addLayout(h)
        
        
        self.setFixedWidth(800)
        self.titleBar.hide()
    
    def confirm(self):
        
        for box in self.boxes:
            if box.isChecked():
                self.keys.append(box.property('key'))
        
        self.accept()
        
    def cancel(self):
        
        self.reject()