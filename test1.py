import re

css_string = """
QHeaderView::section {
    background-color: transparent;
    color: rgb(96, 96, 96);
    padding-left: 5px;
    padding-right: 5px;
    border: 1px solid rgba(0, 0, 0, 15);
    font: 13px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC';
}

OtherSection {
    font: 12px 'Times New Roman';
}
"""

# 定义要替换的 CSS 类名、属性名称和属性值
css_updates = {
    "QHeaderView::section": {
        "font": " 14px 'Arial', sans-serif",
        "color": "rgb(128, 128, 128)",
        "new-property": "new-value"
    },
    "OtherSection": {
        "font": " 12px 'Times New Roman'",
        "new-property": "new-value"
    }
}

# 遍历字典，进行替换或添加
for css_class, properties in css_updates.items():
    # 构建正则表达式模式
    pattern = rf"({css_class}\s*\{{[^}}]*\}})"
    
    # 使用 lambda 函数进行替换或添加
    def replace_or_add_properties(match):
        content = match.group(1)
        for property_name, new_value in properties.items():
            # 检查属性是否存在
            existing_match = re.search(rf"{property_name}:\s*[^;]+;", content)
            if existing_match:
                # 替换现有属性值
                content = re.sub(rf"({property_name}:\s*)([^;]+)(;)", rf"\1{new_value}\3", content)
            else:
                # 添加新属性
                # if not content.endswith(';'):
                #     content = content.rstrip('}') + ';\n'
                content = content.rstrip('}') + f"    {property_name}: {new_value};\n}}"
        return content
    
    css_string = re.sub(pattern, replace_or_add_properties, css_string)

# 打印最终结果
print("Final CSS string:")
print(css_string)