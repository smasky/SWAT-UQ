from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPainter, QPen, QColor
from qfluentwidgets import BodyLabel, SpinBox, DoubleSpinBox

from .utility import setFont, MediumSize, Normal, substitute
from .check_box import CheckBox_
class hyperWidget(QWidget):
    
    changed=pyqtSignal()
    
    def __init__(self, dicts, parent=None):
        
        super().__init__(parent)
        self.setObjectName("hyperWidget")
        mainLayout=QGridLayout(self)
        self.widgets=[]
        self.relatedWidgets=[]
        
        mainLayout.setVerticalSpacing(10)
        
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1 ,1)
        mainLayout.setColumnStretch(2, 1)
        mainLayout.setColumnStretch(3, 1)
        mainLayout.setColumnStretch(4 ,1)
        mainLayout.setColumnStretch(5, 1)
        mainLayout.setColumnStretch(6, 1)
        
        count=0
        for name, contents in dicts.items():
    
            if 'dec' in contents:
                dec=contents['dec']
            else:
                dec=name
            
            label=BodyLabel(dec+":")
            setFont(label)
            label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
            
            type=contents['type']
            value=contents['default']
            method=contents['method']
            class_=contents['class']
            
            if type=="int":
                line=SpinBox()
                line.setMaximum(5000)
                line.setValue(int(value))
                line.setMaximumWidth(160)
                setFont(line, MediumSize, Normal)

            elif type=="float":
                line=DoubleSpinBox()
                line.setValue(float(value))
                line.setMaximumWidth(160)
                setFont(line, MediumSize, Normal)
                
            elif type=="bool":
                line=CheckBox_()
                line.setChecked(bool(value))
                
                setFont(line, MediumSize, Normal)
                
            if 'related' in contents:
                if type=="int" or type=="float":
                    line.valueChanged.connect(lambda value: self.changedEvent())
                else:
                    line.stateChanged.connect(lambda value: self.changedEvent())
                line.setProperty('related', 1)
                self.relatedWidgets.append(line)
            else:
                line.setProperty('related', 0)
            
            line.setProperty('name', name)
            line.setProperty('method', method)
            line.setProperty('class', class_)
            line.setProperty('type', type)
            self.widgets.append(line)
            
            row=count//2
            col=2 if count%2==0 else 5
            mainLayout.addWidget(label, row, col-1, Qt.AlignmentFlag.AlignVCenter)
            mainLayout.addWidget(line, row, col, Qt.AlignmentFlag.AlignVCenter)
            count+=1
            
        row=count//2+1
        for col in [1, 2, 4, 5]:
            w = QWidget()
            w.setFixedSize(200, 10)
            mainLayout.addWidget(w, row, col)

        mainLayout.setContentsMargins(0, 15, 0, 15)
        
    def changedEvent(self):
        
        self.changed.emit()
    
    def returnRelated(self):
        R={}
        for w in self.relatedWidgets:
            name=w.property('name')
            type=w.property('type')
            if type=="int":
                R[name]=int(w.value())
            elif type=='float':
                R[name]=float(w.value())
            elif type=='bool':
                R[name]=w.isChecked()
        return R
    
    def returnHyper(self):
        
        hyper={}
        for w in self.widgets:
            name=w.property('name')
            method=w.property('method')
            class_=w.property('class')
            type=w.property('type')
            related=w.property('related')
            hyper.setdefault(class_, [])
            h={}
            h['name']=name
            h['method']=method
            h['related']=related
            if type=="int":
                h['value']=int(w.value())
            elif type=='float':
                h['value']=float(w.value())
            elif type=='bool':
                h['value']=w.isChecked()
            hyper[class_].append(h)
                
        return hyper
    
    def paintEvent(self, event):
        # Create QPainter object
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Create a pen to define the border style
        pen = QPen(QColor(0, 0, 0, 30))
        pen.setWidth(1)
        painter.setPen(pen)
        
        # Calculate the rectangle that covers columns 1 to 5
        margin = 10  # Margin for the rounded rectangle
        left = self.layout().cellRect(0, 1).left() - margin
        top = self.layout().cellRect(0, 1).top() - margin
        right = self.layout().cellRect(self.layout().rowCount() - 1, 5).right() + margin
        bottom = self.layout().cellRect(self.layout().rowCount() - 1, 5).bottom() + margin
        
        # Draw the rounded rectangle
        painter.drawRoundedRect(left-5, top-5, right - left+5, bottom - top+5, 15, 15)