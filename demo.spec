# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

datas = [
    ('GUI/qss/banner_widget.qss', 'GUI/qss'),
    ('GUI/qss/displayA.qss', 'GUI/qss'),
    ('GUI/qss/displayB.qss', 'GUI/qss'),
    ('GUI/qss/get_start.qss', 'GUI/qss'),
    ('GUI/qss/link_card.qss', 'GUI/qss'),
    ('GUI/qss/messagebox.qss', 'GUI/qss'),
    ('GUI/qss/obj_table.qss', 'GUI/qss'),
    ('GUI/qss/op_widget.qss', 'GUI/qss'),
    ('GUI/qss/open_project.qss', 'GUI/qss'),
    ('GUI/qss/optimization.qss', 'GUI/qss'),
    ('GUI/qss/para_setting.qss', 'GUI/qss'),
    ('GUI/qss/problem_define.qss', 'GUI/qss'),
    ('GUI/qss/para_table.qss', 'GUI/qss'),
    ('GUI/qss/sa_widget.qss', 'GUI/qss'),
    ('GUI/qss/sensitivity_analysis.qss', 'GUI/qss'),
    ('GUI/qss/table_widget.qss', 'GUI/qss'),
    ('GUI/qss/tree_list.qss', 'GUI/qss'),
    ('GUI/qss/validation.qss', 'GUI/qss'),
    ('GUI/picture/header.png', 'GUI/picture'),
    ('GUI/picture/header1.png', 'GUI/picture'),
    ('GUI/picture/header2.png', 'GUI/picture'),
    ('GUI/picture/header3.png', 'GUI/picture'),
    ('GUI/picture/header4.png', 'GUI/picture'),
    ('GUI/data/parameter_list.txt', 'GUI/data'),
    ('GUI/picture/icon.png', 'GUI/picture'),
    ('GUI/picture/title_icon.png', 'GUI/picture'),
    ('GUI/data/SWAT_paras_files.csv', 'GUI/data')
]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='demo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='./GUI/picture/icon.png',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='demo'
)
