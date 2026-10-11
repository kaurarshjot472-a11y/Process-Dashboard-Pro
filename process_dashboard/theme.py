"""Centralized visual language for the desktop UI (no external assets)."""
STYLESHEET = """
QMainWindow, QWidget { background: #0b1020; color: #e9eefc; font-family: 'Segoe UI'; font-size: 13px; }
QMenuBar, QMenu { background: #10192b; color: #e9eefc; padding: 6px; }
QMenuBar::item:selected, QMenu::item:selected { background: #263854; border-radius: 5px; }
QLabel#title { font-size: 29px; font-weight: 750; color: #f7faff; }
QLabel#subtitle, QLabel#muted { color: #8b9bb7; }
QLabel#liveStatus { background: #102b30; color: #55e0c0; border: 1px solid #1c514d; border-radius: 11px; padding: 9px 14px; font-weight: 700; }
QFrame#metricCard, QFrame#graphCard { background: #141e32; border: 1px solid #253450; border-radius: 15px; }
QLabel#metricLabel { color: #94a9c9; font-size: 11px; font-weight: 700; }
QLabel#metricValue { color: #f7faff; font-size: 28px; font-weight: 750; }
QLabel#graphTitle { color: #d9e5ff; font-size: 14px; font-weight: 700; }
QLabel#graphCurrent { color: #74c7ff; font-size: 15px; font-weight: 700; }
QLineEdit, QTextEdit, QComboBox { background: #111b2e; border: 1px solid #30415e; border-radius: 9px; padding: 9px 12px; selection-background-color: #3c75c5; }
QLineEdit:focus, QComboBox:focus { border: 1px solid #61b0ff; }
QPushButton { background: #213555; border: 1px solid #36547c; border-radius: 9px; padding: 9px 13px; color: #f0f5ff; font-weight: 600; }
QPushButton:hover { background: #2d4870; border-color: #5d92cf; }
QPushButton:pressed { background: #1a2b45; }
QPushButton:disabled { background: #152036; border-color: #22314b; color: #60718d; }
QPushButton#danger { background: #502737; border-color: #8a4259; color: #ffe1e9; }
QPushButton#danger:hover { background: #763348; }
QTableView { background: #101a2b; alternate-background-color: #142037; border: 1px solid #293a55; border-radius: 11px; gridline-color: transparent; selection-background-color: #285487; selection-color: white; }
QHeaderView::section { background: #1b2b45; color: #b6c8e7; border: none; border-bottom: 1px solid #314665; padding: 11px 8px; font-weight: 700; }
QTableView::item { padding: 5px; border: none; }
QListWidget#sidebar { background: #10192b; border: none; border-right: 1px solid #24334b; padding: 24px 10px; outline: none; }
QListWidget#sidebar::item { color: #a1b1cc; padding: 16px 14px; border-radius: 10px; margin: 5px 0; }
QListWidget#sidebar::item:hover { background: #1b2b45; color: white; }
QListWidget#sidebar::item:selected { background: #254b7b; color: #f8fbff; font-weight: 700; }
QStatusBar { background: #10192b; color: #92a8c7; border-top: 1px solid #23344e; }
QLabel#note { color: #c2ac78; padding-top: 7px; }
QScrollBar:vertical { background: #10192b; width: 9px; border: none; }
QScrollBar::handle:vertical { background: #385072; border-radius: 4px; min-height: 24px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #10192b; height: 9px; border: none; }
QScrollBar::handle:horizontal { background: #385072; border-radius: 4px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
"""
