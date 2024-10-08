from PyQt5.QtWidgets import QWidget, QHBoxLayout, QGridLayout, QFormLayout
from PyQt5.QtCore import pyqtSignal, Qt
from qfluentwidgets import BodyLabel, SpinBox, DoubleSpinBox, CheckBox


class hyperWidget(QWidget):
    
    changed=pyqtSignal()
    
    def __init__(self, dicts, parent=None):
        
        super().__init__(parent)
        formLayout1=QFormLayout()
        formLayout1.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        formLayout2=QFormLayout()
        formLayout2.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        hBoxLayout=QHBoxLayout(self)
        self.widgets=[]
        self.relatedWidgets=[]
        
        count=0
        for name, contents in dicts.items():
    
            if 'dec' in contents:
                dec=contents['dec']
            else:
                dec=name
            
            label=BodyLabel(dec+":")
            label.setFixedWidth(200)
            label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
            
            type=contents['type']
            value=contents['default']
            method=contents['method']
            class_=contents['class']
            if type=="int":
                line=SpinBox()
                line.setMaximum(5000)
                line.setValue(int(value))

            elif type=="float":
                line=DoubleSpinBox()
                line.setValue(float(value))
                
            elif type=="bool":
                line=CheckBox()
                line.setChecked(bool(value))

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
            
            if count%2==0:
                formLayout1.addRow(label, line)
            else:
                formLayout2.addRow(label, line)
            count+=1
            
        hBoxLayout.addStretch(1)
        hBoxLayout.addLayout(formLayout1)
        hBoxLayout.addStretch(3)
        hBoxLayout.addLayout(formLayout2)
        hBoxLayout.addStretch(3)
        
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