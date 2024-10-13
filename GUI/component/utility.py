from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget
import re

Medium=QFont.Medium
MediumSize=18
Normal=QFont.Normal

def setFont(widget: QWidget, fontSize=MediumSize, weight=Medium):
    """ set the font of widget

    Parameters
    ----------
    widget: QWidget
        the widget to set font

    fontSize: int
        font pixel size

    weight: `QFont.Weight`
        font weight
    """
    widget.setFont(getFont(fontSize, weight))


def getFont(fontSize=14, weight=QFont.Normal):
    """ create font

    Parameters
    ----------
    fontSize: int
        font pixel size

    weight: `QFont.Weight`
        font weight
    """
    font = QFont()
    font.setFamilies(['Segoe UI', 'Microsoft YaHei', 'PingFang SC'])
    font.setPixelSize(fontSize)
    font.setWeight(weight)
    return font

def substitute(qss, substitutions):
    
    for css_class, properties in substitutions.items():
        pattern = rf"({css_class}\s*\{{[^}}]*\}})"
    
        def replace_or_add_properties(match):
            content = match.group(1)
            for property_name, new_value in properties.items():
                existing_match = re.search(rf"{property_name}:\s*[^;]+;", content)
                if existing_match:
                    content = re.sub(rf"({property_name}:\s*)([^;]+)(;)", rf"\1{new_value}\3", content)
                else:
            
                    content = content.rstrip('}') + f"    {property_name}: {new_value};\n}}"
            return content
    
        qss = re.sub(pattern, replace_or_add_properties, qss)
    
    return qss
    
# def multi_level_substitute(template_string, substitutions):
#     # 创建模板对象
#     template = string.Template(template_string)
    
#     # 初步替换
#     replaced_content = template.safe_substitute(substitutions)
    
#     # 递归替换
#     while '$' in replaced_content:
#         replaced_content = string.Template(replaced_content).safe_substitute(substitutions)
    
#     return replaced_content