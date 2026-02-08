# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Arknights Auto Separate/Cut Pause Tool
# Platform: Windows
#
# Build instructions:
# 1. Run setup.bat to create venv and download FFmpeg to bin/
# 2. Activate venv: venv\Scripts\activate.bat
# 3. Build: pyinstaller cut_tool.spec
#
# Note: Dependencies (numpy, pydub) are now installed via pip, not bundled

block_cipher = None

a = Analysis(
    ['cut_tool.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include FFmpeg binaries from bin/ folder
        # Note: bin/ is created by setup.bat which downloads FFmpeg
        ('bin/ffmpeg.exe', 'bin'),
        ('bin/ffprobe.exe', 'bin'),
        # Include sample images for manual coordinate setting (optional)
        # Uncomment if these files exist in your repository:
        # ('sample1.jpg', '.'),
        # ('sample2.jpg', '.'),
    ],
    hiddenimports=[
        # OpenCV (cv2) hidden imports
        'cv2',
        'cv2.cv2',
        # NumPy hidden imports
        'numpy',
        'numpy.core._multiarray_umath',
        'numpy.core.multiarray',
        'numpy.core._dtype_ctypes',
        'numpy.core._internal',
        'numpy.random._common',
        'numpy.random._bounded_integers',
        'numpy.random._mt19937',
        'numpy.random.mtrand',
        # Pydub hidden imports
        'pydub',
        'pydub.audio_segment',
        'pydub.utils',
        'pydub.effects',
        'pydub.scipy_effects',
        # CustomTkinter
        'customtkinter',
        # Darkdetect for theme detection
        'darkdetect',
        # Tkinter (standard library, but explicit doesn't hurt)
        'tkinter',
        'tkinter.ttk',
        'tkinter.font',
        # Internationalization modules
        'i18n',
        'ui',
        # ffmpegcv for H.264 encoding
        'ffmpegcv',
        'ffmpegcv.ffmpeg_writer',
        'ffmpegcv.video_info',
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
    [],
    exclude_binaries=True,
    name='cut_tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Windows GUI application - no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add path to .ico file if available: 'icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='cut_tool',
)
