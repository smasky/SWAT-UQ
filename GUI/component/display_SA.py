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

class DisplaySA(QFrame):
    
    ratioEmit=pyqtSignal(float)
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        # hBoxLayout=QHBoxLayout(self)
        
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
        
        vMainLayout.addWidget(self.w)
       
        # self.operation=Operation(self.canvas, self)
        
        # self.canvas.ratioEmit.connect(self.operation.setRatio)
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        h=QHBoxLayout(); h.setContentsMargins(0, 5, 0, 5)
        self.configBtn=PrimaryPushButton("Config", self)
        self.configBtn.clicked.connect(self.showConfigPanel)
        self.configBtn.setMinimumWidth(150)
        setFont(self.configBtn)
        self.saveFigBtn=PrimaryPushButton("Save Figure", self)
        self.saveFigBtn.setMinimumWidth(150)
        setFont(self.saveFigBtn)
        self.reset=PrimaryPushButton("Reset", self)
        self.reset.setMinimumWidth(150)
        setFont(self.reset)
        h.addStretch(1); h.addWidget(self.saveFigBtn)
        h.addSpacing(20); h.addWidget(self.reset)
        h.addSpacing(20); h.addWidget(self.configBtn); h.addStretch(1)
        
        self.saveFigBtn.clicked.connect(self.saveFig)
        
        vMainLayout.addLayout(h)
        
        # hBoxLayout.addLayout(vMainLayout); hBoxLayout.addWidget(self.operation)
        
        with path(GUI.qss, "displayA.qss") as qss_path:
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
    
    def showConfigPanel(self):
        
        configPanel=ConfigPanel(self)
        configPanel.show()
    
    def drawResult(self):
        
        fileName=self.resultFile.currentText()
        self.SAData=Pro.loadSAFile(fileName)
        self.canvas.show_plot()
        try:
            del self.SAData['S1(First Order)']['matrix']
            data=self.SAData['S1(First Order)']
            self.operation.data=data
            self.canvas.plot_parameters(self.SAData['S1(First Order)'])
            
        except Exception as e:
            
            del self.SAData['S1']['matrix']
            data=self.SAData['S1']
            self.operation.data=data
            self.canvas.plot_parameters(self.SAData['S1'])

class ConfigPanel(FramelessDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setFixedSize(400, 500)
        self.setWindowTitle("Config Panel")
        
    
  
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
        
        label=BodyLabel("Bar Color:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.barColor=ColorButton(self.color, self)
        self.barColor.clicked.connect(self.showColorDialog)
        setFont(self.barColor)
        self.controls.append(self.barColor)
        self.barColor.setProperty('name', 'barColor')
        self.barColor.setProperty('type', 'txt')
        self.barColor.setStyleSheet(f"background-color: {self.color.name()}; border: 1px solid rbga(0, 0, 0, 0.073); border-radius: 5px; outline: none;")
        
        
        vMainLayout.addWidget(label, 2, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.barColor, 2, 1, Qt.AlignmentFlag.AlignVCenter)
        
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
        
        vMainLayout.addWidget(label, 3, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.barWidth, 3, 1, Qt.AlignmentFlag.AlignVCenter)
        
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
        
        vMainLayout.addWidget(label, 4, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.barSpacing, 4, 1, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("Edge Width:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.edgeWidth=SpinBox(self)
        self.edgeWidth.setProperty('name', 'edgeWidth')
        self.edgeWidth.setProperty('type', 'int')
        self.edgeWidth.setValue(1)
        self.controls.append(self.edgeWidth)
        setFont(self.edgeWidth)
        
        vMainLayout.addWidget(label, 5, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.edgeWidth, 5, 1, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("yMaxLimit:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.yMaxLimit=DoubleSpinBox(self)
        self.yMaxLimit.setRange(0.1, 1.3)
        self.yMaxLimit.setSingleStep(0.1)
        self.yMaxLimit.setProperty('name', 'yMaxLimit')
        self.yMaxLimit.setProperty('type', 'float')
        self.yMaxLimit.setValue(1.0)
        self.controls.append(self.yMaxLimit)
        setFont(self.yMaxLimit)
        
        vMainLayout.addWidget(label, 6, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.yMaxLimit, 6, 1, Qt.AlignmentFlag.AlignVCenter)
        
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
        
        vMainLayout.addWidget(label, 7, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.xRotation, 7, 1, Qt.AlignmentFlag.AlignVCenter)
        
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
        
        vMainLayout.addWidget(label, 8, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.figWidth, 8, 1, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("Value Text:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.valueText=ComboBox(self)
        self.valueText.addItems(['True', 'False'])
        self.valueText.setCurrentIndex(0)
        self.valueText.setProperty('name', 'ifText')
        self.valueText.setProperty('type', 'bool')
        setFont(self.valueText)
        self.controls.append(self.valueText)
        
        vMainLayout.addWidget(label, 9, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.valueText, 9, 1, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("Bar Selection:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.barBtn=PushButton("Click to select", self)
        setFont(self.barBtn)
        self.barBtn.clicked.connect(self.selectBar)
        self.barBtn.setProperty('name', 'barIndex')
        self.barBtn.setProperty('type', 'list')
        self.controls.append(self.barBtn)
        
        vMainLayout.addWidget(label, 10, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.barBtn, 10, 1, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("Normalization:")
        setFont(label)
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.norm=ComboBox(self)
        self.norm.addItems(['True', 'False'])
        setFont(self.norm)
        self.norm.setProperty('name', 'ifNorm')
        self.norm.setProperty('type', 'bool')
        self.norm.setCurrentIndex(1)
        self.controls.append(self.norm)
        
        vMainLayout.addWidget(label, 11, 0, Qt.AlignmentFlag.AlignVCenter)
        vMainLayout.addWidget(self.norm, 11, 1, Qt.AlignmentFlag.AlignVCenter)
        
        
        self.refreshBtn=PrimaryPushButton("Refresh", self)
        setFont(self.refreshBtn)
        self.refreshBtn.clicked.connect(self.refresh)
        vMainLayout.addWidget(self.refreshBtn, 12, 0, 1, 2)
    
    def selectBar(self):
        
        dialog = BarSelector(self.data, self.keys, self.window())
        dialog.ACCEPTED.connect(lambda: setattr(self, 'keys', dialog.keys))  # 直接使用 setattr 修改 self.keys
        dialog.show()

    def setRatio(self, value):
        
        self.figWidth.setValue(value)

    def showColorDialog(self):
        
        w=ColorDialog(self.color, "Choose color", self.window())
        w.exec()
        self.color=w.color
        self.barColor.setColor(self.color)
        
        w.deleteLater()
        
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
        
    def plot_parameters(self, SAData, barWidth=0.5, boxWidth=2, yMaxLimit=1.0, barSpacing=1.0, ifNorm=False,
                        labelSize=12, edgeWidth=1, xRotation=0, figRatio=1.0, barColor='#1f77b4', ifText=True, barIndex=None):
        
        self.axes.clear() 
        
        if barIndex is None:
            name=list(SAData.keys())
            value=list(SAData.values())
        else:
            name=barIndex
            value=[SAData[key] for key in barIndex]
        
        if ifNorm:
            value=(np.array(value)/np.sum(value)).tolist()

        heights= list(map(abs, value))
        labels=name
        
        bar_width = barWidth
        spacing = barSpacing
        indices = np.arange(len(labels)) * (bar_width + spacing)

        bars=self.axes.bar(indices, heights, color=barColor, width=bar_width, tick_label=labels, edgecolor='black', linewidth=edgeWidth)
        self.axes.set_ylim(0, yMaxLimit) 

        self.axes.set_xlim(-bar_width, max(indices) + bar_width)
        
        self.axes.tick_params(axis='both', direction='in', width=2, 
                              labelsize=labelSize)
        
        self.axes.tick_params(axis='x', which='both', bottom=False, top=False)

        for spine in self.axes.spines.values():
            spine.set_linewidth(boxWidth)
        
        self.axes.set_xticklabels(labels, rotation=xRotation, fontweight='bold')
        plt.setp(self.axes.get_yticklabels(), fontweight='bold')
        
        if ifText:
            for bar, height in zip(bars, heights):
                self.axes.text(
                    bar.get_x() + bar.get_width() / 2,
                    height,  
                    f'{height:.2f}',  
                    ha='center',  
                    va='bottom',  
                    fontsize=int(labelSize/1.2),  
                    fontweight='bold' 
                )
        
        delta=(1.3-figRatio)/2
        self.axes.set_position([0.05, delta, 0.90, figRatio-0.2])
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
        
        self.save_figure_with_size(path, format=suffix, scale=2, dpi=300)
    
    def resizeEvent(self, event):
        
        self.canvas_width, self.canvas_height=self.get_width_height()
        self.ratio=self.canvas_width/self.canvas_height
        super(MplCanvas, self).resizeEvent(event)
    
    def save_figure_with_size(self, filename, format='png', scale=None, dpi=None):
        
        original_size = self.get_width_height()
        original_dpi = self.fig.dpi
        
        print(f"Original size: {original_size}, original dpi: {original_dpi}")
        
        if scale is not None:
            width=original_size[0]/original_dpi*scale*2
            height=original_size[1]/original_dpi*scale*2
        
        if dpi is None:
            dpi=self.saveDpi

        # 调试输出：确保输入的宽高和 DPI 是正确的
        print(f"Setting figure size to width={width} inches, height={height} inches at {dpi} dpi")
            
        # 尝试检查除法是否正确
        self.fig.set_size_inches(width, height)
        
        try:
            # 检查图像大小和 dpi
            print(f"Saving figure with size {self.fig.get_size_inches()} inches at {dpi} dpi")
            self.fig.savefig(filename, format=format, dpi=dpi, bbox_inches='tight')
        
        finally:
            # 恢复原来的尺寸
            restored_width = original_size[0] / original_dpi *2
            restored_height = original_size[1] / original_dpi *2
           # 恢复图像尺寸和 DPI
            self.fig.set_size_inches(restored_width, restored_height)
            self.fig.dpi = original_dpi  # 恢复原始 DPI
            
            # 手动刷新渲染器以确保图像显示正确
            self.fig.canvas.draw()
            # self.fig.dpi = original_dpi

        
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
    ACCEPTED=pyqtSignal(list)
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
        
        self.ACCEPTED.emit(self.keys)
        self.close()
    
    def cancel(self):
        self.close()
        