
from typing import List
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem, QFrame, QWidget,QFormLayout, QGridLayout, QVBoxLayout, QHBoxLayout, QSizePolicy, QTreeWidgetItem
from PyQt5.QtWidgets import QApplication

from qfluentwidgets import TextEdit, TableWidget, BodyLabel, PrimaryPushButton, FluentStyleSheet, getStyleSheet, TreeWidget
from qframelesswindow import FramelessDialog

from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import os
import numpy as np
from .utility import setFont, getFont, Medium, substitute, MediumSize, Normal
from .combox_ import ComboBox
from .message_box import MessageBox
# from .tree_widget import TreeWidget_ as TreeWidget
from ..project import Project as Pro
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QFontMetrics
import matplotlib.dates as mdates
class ValidationWidget(QFrame):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)

        vMainLayout=QVBoxLayout(self)
        
        topHLayout=QHBoxLayout()
        leftLayout=QVBoxLayout()
        formLayout=QFormLayout()
        formLayout.setContentsMargins(10, 10, 0, 0)
        formLayout.setSpacing(20)
        formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        label=BodyLabel("Result File:", self)
        setFont(label)
        self.resultFileBox=ComboBox(self)
        setFont(self.resultFileBox)
        self.resultFileBox.setFixedWidth(300)
        self.resultFileBox._showComboMenu=self.dynamicShowResultFile
        
        formLayout.addRow(label, self.resultFileBox)
        
        label=BodyLabel("Parameter File:")
        setFont(label)
        self.paraFileBox=ComboBox(self)
        setFont(self.paraFileBox)
        self.paraFileBox.setFixedWidth(300)
        self.paraFileBox._showComboMenu=self.dynamicShowParFile
        
        formLayout.addRow(label, self.paraFileBox)
        
        label=BodyLabel("Objective File:")
        setFont(label)
        self.objFileBox=ComboBox(self)
        setFont(self.objFileBox)
        self.objFileBox.setFixedWidth(300)
        self.objFileBox._showComboMenu=self.dynamicShowObjFile
        
        formLayout.addRow(label, self.objFileBox)
        
        label=BodyLabel("SWAT Execution:")
        setFont(label)
        self.swatBox=ComboBox(self)
        setFont(self.swatBox)
        self.swatBox.setFixedWidth(300)
        self.swatBox._showComboMenu=self.dynamicShowSwat
        
        formLayout.addRow(label, self.swatBox)
        
        w=QWidget()
        h=QHBoxLayout(w); h.setContentsMargins(0, 0, 0, 0)
        self.loadBtn=PrimaryPushButton("Load", self)
        self.loadBtn.setFixedWidth(100)
        self.loadBtn.clicked.connect(self.loadFile)
        setFont(self.loadBtn)
        
        self.resetBtn=PrimaryPushButton("Reset", self)
        self.resetBtn.setFixedWidth(100)
        setFont(self.resetBtn)
        self.resetBtn.setEnabled(False)
        self.resetBtn.clicked.connect(self.reset)
        
        h.addWidget(self.loadBtn); h.addSpacing(10); h.addWidget(self.resetBtn)
        
        formLayout.addRow("", w)
        
        formLayout.setAlignment(w, Qt.AlignRight)
        
        leftLayout.addLayout(formLayout)
        
        topHLayout.addLayout(leftLayout)
        topHLayout.addSpacing(20)
        
        w=QWidget(self)
        w.setObjectName("Container")
        h=QHBoxLayout(w)
        self.leftTreeWidget=TreeWidgetVal(self)
        h.addWidget(self.leftTreeWidget)
        h.setContentsMargins(0 ,0 ,0 ,0 )
        w.setStyleSheet(""" #Container { border: 1px solid rgba(0, 0, 0, 0.15); border-radius:15px; } """)
      
        topHLayout.addWidget(w)
        
        vMainLayout.addLayout(topHLayout)
        
        vMainLayout.addSpacing(10)
        
        self.table=TableWidgetVal(self)
        
        vMainLayout.addWidget(self.table)
        
        self.verbose=TextEdit(self);self.verbose.setReadOnly(True)
        font = QFont("Consolas", pointSize=12)
        font.setStyleHint(QFont.Monospace) 
        self.verbose.setFont(font)
        self.verbose.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        vMainLayout.addWidget(self.verbose)
        
        self.applyBtn=PrimaryPushButton("Apply", self)
        self.applyBtn.setFixedWidth(100)
        self.applyBtn.setEnabled(False)
        setFont(self.applyBtn)
        self.simBtn=PrimaryPushButton("Simulate", self)
        self.simBtn.setFixedWidth(100)
        self.simBtn.setEnabled(False)
        setFont(self.simBtn)
        self.visualBtn=PrimaryPushButton("Visualize", self)
        self.visualBtn.setFixedWidth(100)
        self.visualBtn.setEnabled(False)
        setFont(self.visualBtn)
        
        h=QHBoxLayout()
        h.addStretch(1)
        h.addWidget(self.applyBtn); h.addSpacing(20)
        h.addWidget(self.simBtn); h.addSpacing(20)
        h.addWidget(self.visualBtn); h.addSpacing(20)
        h.addStretch(1)
        
        vMainLayout.addLayout(h)
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setStyleSheet("""ValidationWidget {
                                    border: 1px solid rgba(0, 0, 0, 0.15);
                                    border-radius:15px;
                                    background-color: rgba(249, 249, 249, 0.75);
                                }
                           """)
        #connect
        self.leftTreeWidget.itemIndex.connect(self.setDecsToTable)
        self.applyBtn.clicked.connect(self.apply)
        self.simBtn.clicked.connect(self.simulate)
        self.visualBtn.clicked.connect(self.visualize)
    
    def dynamicShowSwat(self):
        
        self.swatBox.clear()
        self.swatBox.addItems(Pro.findSwatExe())
        self.swatBox.setCurrentIndex(0)
        super(ComboBox, self.swatBox)._showComboMenu()
    
    def dynamicShowResultFile(self):
        
        self.resultFileBox.clear()
        self.resultFileBox.addItems(Pro.findSOPResultFile())
        self.resultFileBox.setCurrentIndex(0)
        super(ComboBox, self.resultFileBox)._showComboMenu()
    
    def dynamicShowObjFile(self):
        
        self.objFileBox.clear()
        self.objFileBox.addItems(Pro.findObjFile())
        self.objFileBox.setCurrentIndex(0)
        super(ComboBox, self.objFileBox)._showComboMenu()
        
    def dynamicShowParFile(self):
        
        self.paraFileBox.clear()
        self.paraFileBox.addItems(Pro.findParaFile())
        self.paraFileBox.setCurrentIndex(0)
        super(ComboBox, self.paraFileBox)._showComboMenu()
    
    def loadFile(self):
        
        try:
            fileName=self.resultFileBox.currentText()
            self.OPData=Pro.loadOPFile(fileName)
            data=self.OPData['History_Best']
            
            self.data=[]
            
            self.leftTreeWidget.clear()
            
            for key, items in data.items():
                
                bestObj, bestDecs=items['Best Objectives'].tolist(), items['Best Decisions'].tolist()
                
                self.data.append(bestDecs)
                
                text_decs = ",".join([f"{num:.2f}" for num in bestDecs])
                text_objs = ",".join([f"{num:.2f}" for num in bestObj])
                
                description=f"Objs: {text_objs} | Decs: {text_decs}"
                self.leftTreeWidget.addItem_(key, description)
                
            self.leftTreeWidget.scrollToBottom()
            
            paraFile=self.paraFileBox.currentText()
            path=os.path.join(Pro.projectInfos['projectPath'], paraFile)
            infos, _=Pro.importParaFromFile(path)
            
            self.table.setRowCount(0)
            for info in infos:
                self.table.addRows_(info)
                
            Pro.Val_paraInfos=infos #TODO
            Pro.Val_runInfos['paraPath']=path
            
            objFile=self.objFileBox.currentText()
            path=os.path.join(Pro.projectInfos['projectPath'], objFile)
            infos, _=Pro.importObjFromFile(path)
        
            Pro.Val_objInfos=infos #TODO
            Pro.Val_runInfos['objPath']=path
            
            Pro.Val_runInfos['numParallel']=1
            Pro.Val_runInfos['tempPath']=os.path.join(Pro.projectInfos['projectPath'], 'validation') #TODO
            Pro.Val_runInfos['swatExe']=self.swatBox.currentText()

            self.resetBtn.setEnabled(True)
            self.loadBtn.setEnabled(False)
            
        except Exception as e:
            
            self.reset()
            box=MessageBox(title="Error", content=f"The error is {e}\n If you cannot solve this problem, please contact us!", parent=self.window())
            box.show()
        
    def reset(self):
        
        self.table.setRowCount(0)
        self.leftTreeWidget.clear()
        
        self.resetBtn.setEnabled(False)
        self.loadBtn.setEnabled(True)
        
        self.applyBtn.setEnabled(False)
        self.simBtn.setEnabled(False)
        self.visualBtn.setEnabled(False)
        
        self.verbose.clear()
        
        self.resultFileBox.clear()
        self.paraFileBox.clear()
        self.objFileBox.clear()
        self.swatBox.clear()
        
        Pro.Val_objInfos={}
        Pro.Val_paraInfos={}
        Pro.Val_problemInfos={}
        Pro.Val_result={}
        Pro.Val_runInfos={}
        
    def setDecsToTable(self, index):
        
        decs=self.data[index]
        self.table.setColValue(decs)
        
        if self.applyBtn.isEnabled()==False:
            self.applyBtn.setEnabled(True)
        
    def apply(self):
        
        #
        textWidth = self.verbose.viewport().width()
        fontMetrics = QFontMetrics(self.verbose.font())
        averWidth = fontMetrics.averageCharWidth()
        nChars=textWidth // averWidth
        self.verbose.setProperty('totalWidth', nChars)
        Pro.Val_runInfos['verboseWidth']=nChars
        #
        self.verbose.clear()
        
        Pro.initVal(self.verbose, self.simBtn)
        
        self.applyBtn.setEnabled(False)
        
    def simulate(self):
        
        def finish():
            
            self.verbose.append("The objective values are: ")
            
            objs, simData=Pro.Val_result
            
            self.data=simData
            
            for i, (ID, _) in enumerate(Pro.Val_objInfos.items()):
                
                self.verbose.append(f"obj {ID}: {objs[i]:.4f} ")

            self.verbose.append(f"The validation scheme has been saved to: {Pro.projectInfos['tempPath']}")
            self.verbose.append("For detail, please click the 'Visualize' button.")

            self.visualBtn.setEnabled(True)
        
        self.verbose.append("Simulating. Please wait....")
        
        decs=self.table.getValues()
        Pro.singleSim(decs, finish)
        self.applyBtn.setEnabled(False)
        self.simBtn.setEnabled(False)

    def visualize(self):
        
        dialog=VisualizeWidget(self)
        
        dialog.show()
    
class TreeWidgetVal(TreeWidget):
    
    itemIndex=pyqtSignal(int)
    
    def __init__(self, parent=None):
            
        super().__init__(parent)
        
        self.initUI()
        self.lastCheckedItem=None
        
    def initUI(self):
        
        self.setHeaderLabels(["Optimization Iters", "Best Obj Value"])
        qss=getStyleSheet(FluentStyleSheet.TREE_VIEW)
        qss=substitute(qss, {'QHeaderView::section':{'font': " 18px 'Segoe UI', 'Microsoft YaHei'", 'font-weight': '500'}})
        self.setStyleSheet(qss)
        self.header().setStyleSheet("QHeaderView::section { color: black; }")
        self.header().setSectionResizeMode(0, QHeaderView.Fixed)
        self.setColumnWidth(0, 200) 
        self.header().setSectionResizeMode(1, QHeaderView.ResizeToContents) 
        self.itemClicked.connect(self.handleItemClicked)
    
    def clear(self):
        
        self.lastCheckedItem=None
        
        return super().clear()
    
    def addItem_(self, key, description):
        
        iterItems= QTreeWidgetItem(self, [key, description])
        iterItems.setFont(0, getFont(18, Medium))
        iterItems.setFont(1, getFont(18, Medium))
        iterItems.setToolTip(1, description)
        iterItems.setFlags(iterItems.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
        iterItems.setCheckState(0, Qt.Unchecked)
    
    def handleItemClicked(self, item, column):
        
        if self.lastCheckedItem and self.lastCheckedItem is not item:
            self.lastCheckedItem.setCheckState(0, Qt.Unchecked) 
        
        item.setCheckState(0, Qt.Checked)
        self.lastCheckedItem = item 
        
        index=self.indexOfTopLevelItem(item)
        
        self.itemIndex.emit(index)

class TreeWidgetObj(TreeWidget):
    
    selected=pyqtSignal(tuple)
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        self.initUI()
        self.setFixedWidth(200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.itemClicked.connect(self.onItemClicked)
        self.lastCheckedItem=None
        
    def initUI(self):
        
        self.setHeaderLabels(["Objective"])
        qss=getStyleSheet(FluentStyleSheet.TREE_VIEW)
        qss=substitute(qss, {'QHeaderView::section':{'font': " 18px 'Segoe UI', 'Microsoft YaHei'", 'font-weight': '500'}})
        self.setStyleSheet(qss)
        self.header().setStyleSheet("QHeaderView::section { color: black; }")

    def addItems_(self, infos):
        
        for ID, series in infos.items():
            iterItems = QTreeWidgetItem(self, [f"Obj {ID}"])
            iterItems.setFont(0, getFont(16, Medium))
            
            for i, ser in enumerate(series):
                serID=ser['serID']
                iterItems = QTreeWidgetItem(iterItems, [f"Series {serID}"])
                iterItems.setFont(0, getFont(16, Medium))
                iterItems.setFlags(iterItems.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
                iterItems.setCheckState(0, Qt.Unchecked)
                iterItems.setData(0, Qt.UserRole, (ID, i))

        self.expandAll()
    
    def onItemClicked(self, item, col):
        
        index=item.data(col, Qt.UserRole)
        self.selected.emit(index)
        
        if self.lastCheckedItem and self.lastCheckedItem is not item:
            self.lastCheckedItem.setCheckState(0, Qt.Unchecked) 
        
        item.setCheckState(0, Qt.Checked)
        self.lastCheckedItem = item 
        
    
class TableWidgetVal(TableWidget):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        qss=getStyleSheet(FluentStyleSheet.TABLE_VIEW)
        qss=substitute(qss, {'QTableView': { 'font': " 16px 'Segoe UI', 'Microsoft YaHei'"}, 'QHeaderView::section':{'font': " 18px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'", 'font-weight': ' 500'}})
        self.setStyleSheet(qss)

        self.initUI()
        
    def initUI(self):
        
        self.setBorderRadius(8)
        self.setBorderVisible(True)
        self.horizontalHeader().setVisible(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setColumnCount(7)
        
        self.setHorizontalHeaderLabels([
            str('Parameter Name'), str('File Extension'), str('Tuning Mode'),
            str('Lower Bound'), str('Upper Bound'), str('Position'), str('Value')])
        self.setFixedHeight(200)
        self.horizontalHeader().setStyleSheet(f"QHeaderView::section {{ color: black; font: {MediumSize}px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'; }}")
        self.verticalHeader().setVisible(False)
        
    def addRows_(self, data):
        
        row=self.rowCount()
        col=0
        
        self.insertRow(row)
        self.setRowHeight(row, 35) 
        
        for i, value in enumerate(data):
            if i==2:
                value=Pro.INT_MODE[value]
            
            item=QTableWidgetItem(value); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            setFont(item, weight=Normal)
            self.setItem(row, col, item)
            col+=1
    
    def setColValue(self, decs):
        
        for i, v in enumerate(decs):
            
            item=QTableWidgetItem(f"{float(v):.4f}");item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            setFont(item)

            self.setItem(i, 6, item)
    
    def getValues(self):
        
         return np.array([float(self.item(i, 6).text()) for i in range(self.rowCount())]).ravel()

class VisualizeWidget(FramelessDialog):    
        
    def __init__(self, parent=None):
        super().__init__(parent)
        
        vMainLayout=QVBoxLayout(self)
        vMainLayout.setContentsMargins(0, 32, 0, 0)
        
        title=BodyLabel("Visual Validation", self)
        
        setFont(title)
        
        self.titleBar.hBoxLayout.insertWidget(0, title)
        self.titleBar.hBoxLayout.insertSpacing(0, 20)
        
        h=QHBoxLayout()
        self.treeWidget=TreeWidgetObj(self)
        self.treeWidget.addItems_(Pro.Val_objInfos)
        
        self.canvas=MplCanvas(width=16, height=9, dpi=300)

        h.setContentsMargins(10, 0, 0, 0)
        h.addWidget(self.treeWidget)
        h.addWidget(self.canvas)
        
        vMainLayout.addLayout(h)
        vMainLayout.addStretch(1)
        
        self.setFixedSize(1200, 700)
        
        #connect
        self.treeWidget.selected.connect(self.plotPic)
    
    def plotPic(self, index):
        
        objID, serInd=index
        self.canvas.plotPic(objID, serInd, self.parent().data)
        

    def show(self):
        
        super().show()
        
        
class MplCanvas(FigureCanvas):
    
    def __init__(self, width=16, height=9, dpi=300):
        
        self.saveDpi=dpi
        self.originDpi=100
        self.fig = Figure(figsize=(width, height), dpi=self.originDpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        self.clear_plot()
        
    def plotPic(self, objID, serID, simData):
        
        self.show_plot()
        objInfos=Pro.Val_objInfos
        
        timeLists=objInfos[objID][serID]['timeList']
        dataList=objInfos[objID][serID]['dataList']
        s=simData[objID][serID]
        dates = [datetime(year, month, day).date() for year, month, day in timeLists]
        
                # 绘制数据
        
        if dates[0].month not in [4, 8, 12]:
            xticks=[dates[0]]
        else:
            xticks=[]
        xticks+=self.generate_xticks(dates)
        
        if dates[-1].month not in [4, 8, 12]:
            xticks.append(dates[-1])
        
        
        self.axes.set_ylim(np.min(dataList), np.max(dataList))
        self.axes.plot(dates, dataList, marker='o', linestyle='-', markersize=2, label="observe")
        self.axes.plot(dates, s, marker='o', linestyle='--', markersize=2, label="simulation") 
        self.axes.set_title('Detailed Flow Data')
        self.axes.set_xlabel('Date')
        self.axes.set_ylabel('Flow (units)')
        
        self.axes.xaxis.set_major_locator(mdates.DayLocator())
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        self.axes.legend()
        self.axes.set_xticks(xticks)
        self.fig.autofmt_xdate()
        self.fig.tight_layout()
        self.draw()
    
    def generate_xticks(self, dates):
        
        xticks = []
        for date in dates:
            if date.month in [4, 8, 12] and date.day == 1:
                xticks.append(date)
        return xticks 
    
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