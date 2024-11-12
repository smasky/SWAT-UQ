from PyQt5.QtWidgets import (QWidget, QFrame, QFileDialog, QApplication,
                             QVBoxLayout, QHBoxLayout, QSizePolicy,
                             QGridLayout)

from qframelesswindow import FramelessDialog
from qfluentwidgets import (BodyLabel, PushButton, PrimaryPushButton, LineEdit,
                            SpinBox, DoubleSpinBox, ColorDialog,
                            FluentStyleSheet, getStyleSheet)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from PyQt5.QtCore import Qt, QSize, QEvent, pyqtSignal
from PyQt5.QtGui import QColor
import numpy as np
import math
import GUI.qss
import GUI.data
from importlib.resources import path

from .utility import setFont, substitute, MediumSize
from .combox_ import ComboBox_ as ComboBox
from ..project import Project as Pro
from .check_box import CheckBox_ as CheckBox

BasicDicts={ 'Figure Title' : { 'name' : 'figureTitle', 'type' : 'text', 'default' : 'Optimization Result'},
                'Title Size' : { 'name' : 'titleSize', 'type' : 'int', 'default' : 16, 'range' : (8, 32), 'step' : 1},
                'X Label Size' : { 'name' : 'xLabelSize', 'type' : 'int', 'default' : 12, 'range' : (8, 32), 'step' : 1},
                'X Label' : { 'name' : 'xLabel', 'type' : 'text', 'default' : 'Iter'},
                'Y Label Size' : { 'name' : 'yLabelSize', 'type' : 'int', 'default' : 12, 'range' : (8, 32), 'step' : 1},
                'Y Label' : { 'name' : 'yLabel', 'type' : 'text', 'default' : 'Value'},
                'Y Maximum' : { 'name' : 'yMax', 'type' : 'float', 'default' : 1.0, 'range' : (-1e6, 1e6), 'step' : 1},
                'Y Minimum' : {'name' : 'yMin', 'type' : 'float', 'default' : 0.0, 'range' : (-1e6, 1e6), 'step' : 1},
                'X Maximum' : { 'name' : 'xMax', 'type' : 'float', 'default' : 1.0, 'range' : (-1e6, 1e6), 'step' : 1},
                'X Tick Size' : {'name' : 'xTickSize', 'type' : 'int', 'default' : 12, 'range' : (8, 32), 'step' : 1},
                'X Tick Width' : {'name' : 'xTickWidth', 'type' : 'int', 'default' : 1, 'range' : (1, 8), 'step' : 1},
                'Y Tick Size' : {'name' : 'yTickSize', 'type' : 'int', 'default' : 12, 'range' : (8, 32), 'step' : 1},
                'Y Tick Width' : {'name' : 'yTickWidth', 'type' : 'int', 'default' : 1, 'range' : (1, 8), 'step' : 1},
                'Y Tick Length' : {'name' : 'yTickLength', 'type' : 'int', 'default' : 4, 'range' : (1, 20), 'step' : 1},
                'Y Tick Interval' : {'name' : 'yTickInterval', 'type' : 'float', 'default' : 10, 'range' : (0.01, 1e6), 'step' : 1},
                'X Tick Interval' : {'name' : 'xTickInterval', 'type' : 'float', 'default' : 10, 'range' : (0.01, 1e6), 'step' : 1},
                'Legend Size' : { 'name' : 'legendSize', 'type' : 'int', 'default' : 12, 'range' : (8, 32), 'step' : 1},
                'Box Width' : { 'name' : 'boxWidth', 'type' : 'int', 'default' : 2, 'range' : (1, 10), 'step' : 1},
                'Width Ratio' : { 'name' : 'widthRatio', 'type' : 'float', 'default' : 1.0, 'range' : (0.1, 1), 'step' : 0.01},
                'Height Ratio' : { 'name' : 'heightRatio', 'type' : 'float', 'default' : 1.0, 'range' : (0.1, 1), 'step' : 0.01},
        }

lineDict={
                'Marker Type' : { 'name' : 'markType', 'type' : 'combox', 'items': ['.', 'o', 's', '^'], 'default' : 'o' },
                'Marker Frequency' : { 'name' : 'everyMark', 'type' : 'float', 'default' : 0.01, 'range' : (0.00, 1.00), 'step' : 0.01},
                'Marker Size' : { 'name' : 'markSize', 'type' : 'int', 'default' : 12, 'range' : (1, 32), 'step' : 1},
                'Face Color' : { 'name' : 'markColor', 'type' : 'color', 'default' : '#ff1f77b4', 'tooltip': 'click to select color'},
                'Edge Color' : { 'name' : 'edgeColor', 'type' : 'color', 'default' : '#ff1f77b4', 'tooltip': 'click to select color'},
                'Edge Width' : { 'name' : 'edgeWidth', 'type' : 'int', 'default' : 2, 'range' : (1, 10), 'step' : 1},
                'Line Width' : { 'name' : 'lineWidth', 'type' : 'int', 'default' : 2, 'range' : (1, 10), 'step' : 1},
                'Line Style' : { 'name' : 'lineStyle', 'type' : 'combox', 'items': ['-', '--', '-.', ':'], 'default' : '-' },
                'Line Color' : { 'name' : 'lineColor', 'type' : 'color', 'default' : '#ff1f77b4', 'tooltip': 'click to select color'},
                'Label Name' : { 'name' : 'labelName', 'type' : 'text', 'default' : 'MethodName'},
                'Grid' : { 'name' : 'ifGrid', 'type' : 'bool', 'default' : 'True'},
                'Grid Width' : {'name' : 'gridWidth', 'type' : 'int', 'default' : 1, 'range' : (1, 10), 'step' : 1},
                'Y Inverse' : {'name' : 'ifInverse', 'type' : 'bool', 'default' : 'False'}
        } 

class DisplayOP(QFrame):
    
    ratioEmit=pyqtSignal(float)
    configPanel=None
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        vMainLayout=QVBoxLayout(self)
        vMainLayout.setContentsMargins(0, 20, 0, 20)
        
        h=QHBoxLayout()
        label=BodyLabel("Optimization Result File:")
        setFont(label)
        
        self.resultFile=ComboBox(self)
        self.resultFile._showComboMenu=self.dynamicShowFile
        self.resultFile.setFixedWidth(450)
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
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        h=QHBoxLayout(); h.setContentsMargins(0, 5, 0, 5)
        self.saveFigBtn=PrimaryPushButton("Save Figure", self)
        self.saveFigBtn.setMinimumWidth(150)
        self.saveFigBtn.setEnabled(False)
        setFont(self.saveFigBtn)
        self.resetBtn=PrimaryPushButton("Reset", self)
        self.resetBtn.setMinimumWidth(150)
        self.resetBtn.setEnabled(False)
        setFont(self.resetBtn)
        self.configBtn=PrimaryPushButton("Config", self)
        self.configBtn.setMinimumWidth(150)
        self.configBtn.setEnabled(False)
        setFont(self.configBtn)
        
        h.addStretch(1)
        h.addWidget(self.saveFigBtn); h.addSpacing(20)
        h.addWidget(self.resetBtn); h.addSpacing(20)
        h.addWidget(self.configBtn); h.addStretch(1)
        
        self.saveFigBtn.clicked.connect(self.saveFig)
        self.configBtn.clicked.connect(self.showConfigPanel)
        
        vMainLayout.addLayout(h)
        
        with path(GUI.qss, "displayB.qss") as qss_path:
            with open(qss_path, 'r') as f:
                self.setStyleSheet(f.read())
        
    def reset(self):
        
        self.resultFile.setCurrentIndex(-1)
        self.canvas.reset()
        if self.configPanel is not None:
            self.configPanel.close()
        
        self.saveFigBtn.setEnabled(False)
        self.resetBtn.setEnabled(False)
        self.configBtn.setEnabled(False)
        
    def saveFig(self):
              
        fileName, type = QFileDialog.getSaveFileName(self, "Save Figure", "", "PNG (*.png);;PDF (*.pdf);;SVG (*.svg);;EPS (*.eps)")
        if fileName:
            suffix = type.split('.')[-1].strip(')')
            self.canvas.saveFig(fileName, suffix)
        
    def dynamicShowFile(self):
        
        self.resultFile.clear()
        self.resultFile.addItems(Pro.findSOPResultFile())
        self.resultFile.setCurrentIndex(0)
        super(ComboBox, self.resultFile)._showComboMenu()
    
    def showConfigPanel(self):
        
        self.configPanel.show()
        
    def drawResult(self):
        
        fileName=self.resultFile.currentText()
        self.OPData=Pro.loadOPFile(fileName)
        self.canvas.show_plot()
            
        #Read Data
        data=self.OPData['History_Best'] #TODO
        xData=[]
        yData=[]
        for i, (_, value) in enumerate(data.items()):
            xData.append(i)
            yData.append(value['Best Objectives'])
        
        #calculate interval
        def calInterval(value):
            if value==0:
                return 1
            num_digits = round(math.log10(abs(value)))+1
            base = 10 ** (num_digits-2)
            return base
                
        yInterval=calInterval(np.max(yData)-np.min(yData))
        BasicDicts['Y Tick Interval']['default']=yInterval
        BasicDicts['Y Tick Interval']['step']=yInterval
        BasicDicts['Y Maximum']['default']=np.max(yData)
        BasicDicts['Y Minimum']['default']=np.min(yData)
        
        xInterval=calInterval(np.max(xData)-np.min(xData))
        BasicDicts['X Tick Interval']['default']=xInterval
        BasicDicts['X Tick Interval']['step']=xInterval
        BasicDicts['X Maximum']['default']=len(xData)
        
        data=(xData, yData)
        
        if self.configPanel:
            self.configPanel.close()
            self.configPanel=None
        self.configPanel=ConfigPanel(self.canvas, self)
        self.configPanel.configEmit.connect(self.canvas.setHyper)
        self.configPanel.configEmit.connect(self.canvas.refresh)
        self.canvas.saveEmit.connect(self.configPanel.cancel)
        
        self.configPanel.data=data
        self.canvas.data=data
        self.configPanel.confirm()
        self.canvas.plotPic()
        
        #update Btn
        self.saveFigBtn.setEnabled(True)
        self.resetBtn.setEnabled(True)
        self.configBtn.setEnabled(True)

class MplCanvas(FigureCanvas):
    
    hyper=None
    data=None
    multiply=1
    saveEmit=pyqtSignal()
    def __init__(self, width=16, height=9, dpi=300):
        
        self.saveDpi=dpi
        self.originDpi=100
        self.fig = Figure(figsize=(width, height), dpi=self.originDpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        self.clear_plot()
        
    def setHyper(self, hyper):
        
        self.hyper=hyper
    
    def refresh(self):
        
        self.plotPic()        
    
    def plotPic(self, mul=False):
        
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Arial']
        
        self.axes.clear() 
        
        xData, yData=self.data
        
        ifInverse=self.hyper['ifInverse'] #TODO
        if ifInverse:
            yData=-1*np.array(yData)

        def calRGBA(color):
            return "#"+color[3:]+color[1:3]
            
        markType=self.hyper['markType']
        everyMark=self.hyper['everyMark']
        markSize=self.hyper['markSize'] if not mul else self.hyper['markSize']*self.multiply
        edgeWidth=self.hyper['edgeWidth'] if not mul else self.hyper['edgeWidth']*self.multiply
        lineWidth=self.hyper['lineWidth'] if not mul else self.hyper['lineWidth']*self.multiply
        lineStyle=self.hyper['lineStyle']
        lineColor=calRGBA(self.hyper['lineColor'])
        markFaceColor=calRGBA(self.hyper['markColor'])
        markEdgeColor=calRGBA(self.hyper['edgeColor'])
        labelName=self.hyper['labelName']
        self.axes.plot(xData, yData, marker=markType, markevery=everyMark, markeredgecolor=markEdgeColor, markerfacecolor=markFaceColor,
                       markeredgewidth=edgeWidth, markersize=markSize, linewidth=lineWidth, linestyle=lineStyle,
                       color=lineColor, label=labelName)
        
        xLabel=self.hyper['xLabel']
        xLabelSize=self.hyper['xLabelSize'] if not mul else self.hyper['xLabelSize']*self.multiply
        self.axes.set_xlabel(xLabel, fontsize=xLabelSize, fontweight='bold')
        
        yLabel=self.hyper['yLabel']
        yLabelSize=self.hyper['yLabelSize'] if not mul else self.hyper['yLabelSize']*self.multiply
        self.axes.set_ylabel(yLabel, fontsize=yLabelSize, fontweight='bold')
        
        figureTitle=self.hyper['figureTitle']
        figureTitleSize=self.hyper['titleSize'] if not mul else self.hyper['titleSize']*self.multiply
        self.axes.set_title(figureTitle, fontsize=figureTitleSize, fontweight='bold')
        
        legendSize=self.hyper['legendSize'] if not mul else self.hyper['legendSize']*self.multiply
        self.axes.legend(prop={'weight':'bold', 'size':legendSize}, loc='upper right')
        
        if self.hyper['ifGrid']:
            gridWith=self.hyper['gridWidth'] if not mul else self.hyper['gridWidth']*self.multiply
            self.axes.grid(True, which='major', axis='both', linewidth=gridWith)
        
        plt.rcParams['axes.labelweight'] = 'bold'  # 
        
        yMaximum=self.hyper['yMax']
        yMinimum=self.hyper['yMin']
        xMaximum=self.hyper['xMax']
        self.axes.set_xlim(0, xMaximum)
        self.axes.set_ylim(yMinimum, yMaximum)
         
        xTickWidth=self.hyper['xTickWidth'] if not mul else self.hyper['xTickWidth']*self.multiply
        xTickSize=self.hyper['xTickSize'] if not mul else self.hyper['xTickSize']*self.multiply
        
        self.axes.tick_params(axis='x', direction='in', width=xTickWidth, which='both', 
                              bottom=True, top=False, labelsize=xTickSize)
        
        yTickWidth=self.hyper['yTickWidth'] if not mul else self.hyper['yTickWidth']*self.multiply
        yTickSize=self.hyper['yTickSize'] if not mul else self.hyper['yTickSize']*self.multiply
        self.axes.tick_params(axis='y', direction='in', width=yTickWidth, which='both', 
                              left=True, right=False, labelsize=yTickSize)
        
        yTickInterval=self.hyper['yTickInterval']
        self.axes.yaxis.set_major_locator(MultipleLocator(yTickInterval))
        
        xTickInterval=self.hyper['xTickInterval']
        self.axes.xaxis.set_major_locator(MultipleLocator(xTickInterval))
        
        boxWidth=self.hyper['boxWidth'] if not mul else self.hyper['boxWidth']*self.multiply
        for spine in self.axes.spines.values():
            spine.set_linewidth(boxWidth)
        
        #adjust size
        heightRatio=self.hyper['heightRatio']
        widthRatio=self.hyper['widthRatio']
        heightDelta=(1.3-heightRatio)/2
        widthDelta=(1.1-widthRatio)/2
        self.axes.set_position([widthDelta, heightDelta, widthRatio-0.1, heightRatio-0.2])
        
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
        
        self.save_figure_with_size(path, format=suffix, scale=1, dpi=300)
    
    def resizeEvent(self, event):
        
        super(MplCanvas, self).resizeEvent(event)
        
        try:
            
            self.canvas_width, self.canvas_height=self.get_width_height()
            self.ratio=self.canvas_width/self.canvas_height

        except ZeroDivisionError:
            pass
        
        except Exception as e:
            
            size=self.parent().size()
            width, height=size.width(), size.height()
            self.canvas_width=width-18
            self.canvas_height=height-18
            self.ratio=self.canvas_width/self.canvas_height
    
    def save_figure_with_size(self, filename, format='png', scale=None, dpi=None):
    
        original_size = self.get_width_height()
        original_dpi = self.fig.dpi
        scaling=original_dpi/self.originDpi
        self.multiply = scale / (dpi/original_dpi)**2
        
        if scale is not None:
            width=original_size[0]/original_dpi*scale
            height=original_size[1]/original_dpi*scale
        
        if dpi is None:
            dpi=self.saveDpi
     
        self.fig.set_size_inches(width, height)
        
        try:
            self.plotPic(mul=True)
            self.fig.savefig(filename, format=format, dpi=dpi, bbox_inches='tight')
        
        except Exception as e:
            
            from PyQt5.QtWidgets import QMessageBox
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setText(f"An error occurred: {str(e)}")
            error_dialog.setWindowTitle("Error")
            error_dialog.exec_()
        
        finally:
            
            restored_width = original_size[0] / original_dpi *scaling
            restored_height = original_size[1] / original_dpi *scaling
    
            self.fig.set_size_inches(restored_width, restored_height)
            self.fig.dpi = original_dpi
            self.plotPic()
            self.fig.canvas.draw()
            
            self.saveEmit.emit()
    
    def reset(self):
        
        self.fig.clf()
        self.axes = self.fig.add_subplot(111)  # 添加一个新的子图
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        for spine in self.axes.spines.values():
            spine.set_visible(False)
        self.figure.canvas.draw_idle()

class ConfigPanel(FramelessDialog):
    
    data=None
    configEmit=pyqtSignal(dict)
    panels=[]
    def __init__(self, canvas, parent=None):
        
        self.canvas=canvas
        
        super().__init__(parent)
        
        width = 650
        height = parent.window().height()
        
        self.setFixedSize(width, height)
        self.titleBar.setFixedWidth(width)
        
        parent_window = parent.window()
        parent_geometry = parent_window.geometry()
        
        new_x = parent_geometry.x() + parent_geometry.width()
        new_y = parent_geometry.y()
        
        screen_geometry = QApplication.desktop().availableGeometry(parent_window)
        
        if new_x + width > screen_geometry.width():
            new_x = parent_geometry.x() + parent_geometry.width() - width
        
        self.move(new_x, new_y)
        
        self.initUI()
    
    def initUI(self):
        
        vMainLayout=QVBoxLayout(self)
        
        vMainLayout.setContentsMargins(0, 32, 0, 0)
        
        title=BodyLabel("Config Panel")
        
        setFont(title)
        self.titleBar.hBoxLayout.insertWidget(0, title)
        self.titleBar.hBoxLayout.setContentsMargins(20, 0, 0, 0)
       
        vMainLayout.addSpacing(5)
        basicPanel=SubPanel('Basic Setting', BasicDicts, self)
        self.panels.append(basicPanel)
        vMainLayout.addWidget(basicPanel)
         
        barPanel=SubPanel('Bar Setting', lineDict, self)
        self.panels.append(barPanel)
        vMainLayout.addWidget(barPanel)
        vMainLayout.addStretch(1)
        
        self.yesBtn=PrimaryPushButton("Confirm", self)
        self.cancelBtn=PrimaryPushButton("Cancel", self)
        self.yesBtn.clicked.connect(self.confirm)
        self.cancelBtn.clicked.connect(self.cancel)
        setFont(self.yesBtn, MediumSize-5)
        setFont(self.cancelBtn, MediumSize-5)
        
        h=QHBoxLayout()
        h.addStretch(1); h.addWidget(self.yesBtn); h.addSpacing(20); h.addWidget(self.cancelBtn); h.addStretch(1)
        vMainLayout.addLayout(h)
        vMainLayout.addSpacing(20)
        
    def confirm(self):
        
        hyper={}
        for panel in self.panels:
            
            h=panel.getValue() 
            hyper.update(h)
        
        self.configEmit.emit(hyper)
    
    def cancel(self):
        
        self.close()
    
class ColorDialog_(ColorDialog):
    
    colorEmit=pyqtSignal(str)
    
    def __init__(self, color, title: str, parent=None, enableAlpha=True):
        super().__init__(color, title, parent, enableAlpha)
        self.yesButton.clicked.connect(lambda: self.colorEmit.emit(self.color.name()))

class SubPanel(QFrame):
    
    def __init__(self, titleText, dicts, parent = None):
        super().__init__(parent)
        
        self.widgets=[]
        self.setObjectName("SubPanel")
        self.vBoxLayout = QVBoxLayout(self)
        title=BodyLabel(titleText)
        title.setFixedHeight(30)
        setFont(title)
        title.setAlignment(Qt.AlignHCenter)
        self.vBoxLayout.addWidget(title, Qt.AlignmentFlag.AlignHCenter)
        
        mainGridLayout=QGridLayout()
        self.vBoxLayout.addLayout(mainGridLayout)
        self.vBoxLayout.addStretch(1)
        count=0
        for key, dict in dicts.items():
            
            label=BodyLabel(key+":")
            setFont(label, MediumSize-5)
            
            type=dict['type']
            name=dict['name']
            default=dict['default']
            
            if type=="int":
                
                widget=SpinBox(self)
                widget.setRange(dict['range'][0], dict['range'][1])
                widget.setValue(default)
                widget.setSingleStep(dict['step'])
                
                widget.get=widget.value
                
            elif type=="float":
                
                widget=DoubleSpinBox(self)
                widget.setRange(dict['range'][0], dict['range'][1])
                widget.setValue(default)
                widget.setSingleStep(dict['step'])
                
                widget.get=widget.value
                
            elif type=="bool":
                
                widget=ComboBox(self)
                widget.menuFontsize=MediumSize-5
                widget.addItems(["True", "False"])
                widget.setCurrentText(dict['default'])
                
                widget.get = (lambda w=widget: w.currentText() == "True")
            
            elif type=="text":
                
                widget=LineEdit(self)
                widget.setText(default)
                
                widget.get=widget.text
                
            elif type=="color":
                
                tooltip=dict['tooltip']
                value=dict['default']
                widget=ColorPushButton(tooltip, value, self)
                widget.clicked.connect(self.showColorDialog)
                
                widget.get=widget.text
            
            elif type=="combox":
                
                items=dict['items']
                value=dict['default']
                widget=ComboBox(self)
                widget.addItems(items)
                widget.setCurrentText(value)
                widget.menuFontsize=MediumSize-5
                
                widget.get=widget.currentText
                     
            setFont(widget, MediumSize-5)
            widget.setProperty('name', name)
            widget.setProperty('type', type)
            widget.setFixedWidth(200)
        
            row=count//2
            col=1 if count%2==0 else 3
            count+=1
            mainGridLayout.addWidget(label, row, col-1, Qt.AlignmentFlag.AlignRight)
            mainGridLayout.addWidget(widget, row, col, Qt.AlignmentFlag.AlignLeft)
            self.widgets.append(widget)
        
        self.setStyleSheet( "#SubPanel {border-top: 1px solid rgba(0, 0, 0, 0.15);} " )      
    
    def showColorDialog(self):
        
        widget=self.sender()
        w=ColorDialog_(widget.color, "Choose color", self.window())
        res=w.exec()
        if res:
            color=w.color
            red_hex = format(color.red(), '02X')
            green_hex = format(color.green(), '02X')
            blue_hex = format(color.blue(), '02X')
            alpha_hex = format(color.alpha(), '02X')
            full_hex_color = f"#{alpha_hex}{red_hex}{green_hex}{blue_hex}"
            widget.color=full_hex_color
            widget.setColor(widget.color)
          
    def getValue(self):
        
        hyper={}
        
        for widget in self.widgets:
            name=widget.property('name')
            value=widget.get()
            hyper[name]=value 

        return hyper
class ColorPushButton(PushButton):
    
    def __init__(self, text, color, parent=None):
        
        super().__init__(parent)
        self.setText(text)
        self.setFixedHeight(30)
        self.setColor(color)
        
    def setColor(self, color):
        self.color=color
        qss=getStyleSheet(FluentStyleSheet.BUTTON)
        qss=substitute(qss, {"PushButton, ToolButton, ToggleButton, ToggleToolButton": {"background" : f" {color}"}})
        self.setStyleSheet(qss)
        self.setText(color)
        self.update()