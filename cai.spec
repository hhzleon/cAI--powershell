# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# 自动推导当前 Python 的 Conda 根目录
conda_prefix = os.path.abspath(os.path.join(os.path.dirname(sys.executable), ".."))

# SSL 动态库路径（根据实际文件名调整）
libssl_path = r"C:\Users\z\miniconda3\Library\bin\libssl-3-x64.dll"
libcrypto_path = r"C:\Users\z\miniconda3\Library\bin\libcrypto-3-x64.dll"

# 检查是否存在
if not os.path.exists(libssl_path) or not os.path.exists(libcrypto_path):
    print("❌ 未找到 OpenSSL DLL，请检查路径：", os.path.join(conda_prefix, 'Library', 'bin'))
else:
    print("✅ 找到 SSL 库：", libssl_path, libcrypto_path)

binaries = [
    (libssl_path, '.'),
    (libcrypto_path, '.')
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=[],
    hiddenimports=['ssl', '_ssl', 'requests', 'urllib3'],
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
    a.binaries,
    a.datas,
    [],
    name='cai',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
