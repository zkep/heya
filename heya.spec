# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import tomllib
from pathlib import Path

block_cipher = None


def get_site_packages_path():
    venv_path = Path(".venv")
    for lib_dir in venv_path.glob("lib/python*"):
        site_packages = lib_dir / "site-packages"
        if site_packages.exists():
            return site_packages
    raise RuntimeError("Cannot find site-packages directory in .venv")


def load_pyinstaller_config():
    config_path = Path("pyinstaller.toml")
    if not config_path.exists():
        return {"venv_path": ".venv", "packages": []}

    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    tool_config = config.get("tool", {}).get("pyinstaller", {})
    return {
        "venv_path": tool_config.get("venv_path", ".venv"),
        "packages": tool_config.get("packages", []),
    }


def scan_packages():
    config = load_pyinstaller_config()
    venv_path = Path(config["venv_path"])
    site_packages = get_site_packages_path()

    datas = []
    for pkg in config["packages"]:
        if ":" in pkg:
            src, dst = pkg.split(":", 1)
            if "/" in src:
                pkg_dir, filename = src.split("/", 1)
                src_path = site_packages / pkg_dir / filename
                if src_path.exists():
                    datas.append((str(src_path), dst))
            else:
                pkg_path = site_packages / src
                if pkg_path.exists():
                    datas.append((str(pkg_path), dst))
        else:
            pkg_path = site_packages / pkg
            if pkg_path.exists():
                datas.append((str(pkg_path), pkg))

    return datas


a = Analysis(
    ['heya/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('heya/app/i18n/locales', 'heya/app/i18n/locales'),
        ('heya/web/i18n/locales', 'heya/web/i18n/locales'),
        ('heya/web/assets', 'heya/web/assets'),
    ] + scan_packages(),
    hiddenimports=[
        'click',
        'playwright',
        'markdown',
        'pypdf',
        'reportlab',
        'gradio',
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'heya.cmd.commands',
        'heya.cmd.commands.html2pdf',
        'heya.cmd.commands.md2pdf',
        'heya.cmd.commands.pdf2word',
        'heya.cmd.commands.wechat2pdf',
        'heya.app',
        'heya.web',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='heya',
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
