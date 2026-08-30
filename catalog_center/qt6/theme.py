from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    key: str
    label: str
    stylesheet: str


LIGHT_QSS = """
QMainWindow, QWidget {
    background: #f4f6f8;
    color: #152536;
}
QWidget#Sidebar {
    background: #0f1f2f;
    color: #f8fafc;
    border: 0;
}
QLabel#BrandTitle {
    color: #ffffff;
    font-size: 18px;
    font-weight: 700;
}
QLabel#BrandSubtitle {
    color: #9fb1c2;
}
QListWidget#Navigation {
    background: transparent;
    color: #d7e0e8;
    border: 0;
    outline: 0;
}
QListWidget#Navigation::item {
    min-height: 38px;
    padding: 4px 10px;
    margin: 2px 0;
    border-radius: 8px;
}
QListWidget#Navigation::item:selected {
    background: #1d3b57;
    color: #ffffff;
}
QFrame#Card {
    background: #ffffff;
    border: 1px solid #dde5ec;
    border-radius: 12px;
}
QLabel#MetricValue {
    font-size: 26px;
    font-weight: 700;
}
QLabel#Muted {
    color: #66788a;
}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {
    background: #ffffff;
    border: 1px solid #cfd8e1;
    border-radius: 8px;
    min-height: 32px;
    padding: 3px 8px;
    selection-background-color: #2b6f9f;
}
QPushButton {
    background: #ffffff;
    border: 1px solid #cfd8e1;
    border-radius: 8px;
    min-height: 32px;
    padding: 4px 12px;
}
QPushButton:hover {
    border-color: #7190a8;
}
QPushButton[primary="true"] {
    background: #143a56;
    color: #ffffff;
    border-color: #143a56;
}
QPushButton[success="true"] {
    background: #176b52;
    color: #ffffff;
    border-color: #176b52;
}
QHeaderView::section {
    background: #eef2f5;
    color: #314557;
    border: 0;
    border-bottom: 1px solid #d8e0e7;
    padding: 7px;
    font-weight: 600;
}
QTableView, QTreeView {
    background: #ffffff;
    alternate-background-color: #f8fafb;
    border: 1px solid #d8e0e7;
    border-radius: 8px;
    gridline-color: #e8edf1;
    selection-background-color: #dceaf4;
    selection-color: #102a43;
}
QToolBar {
    background: #ffffff;
    border-bottom: 1px solid #dde5ec;
    spacing: 4px;
}
QStatusBar {
    background: #ffffff;
    border-top: 1px solid #dde5ec;
}
QMenuBar, QMenu {
    background: #ffffff;
}
QSplitter::handle {
    background: #dce3e9;
    width: 2px;
    height: 2px;
}
QProgressBar {
    border: 1px solid #d3dde5;
    border-radius: 6px;
    text-align: center;
    background: #ffffff;
}
QProgressBar::chunk {
    background: #176b52;
    border-radius: 5px;
}
"""

DARK_QSS = """
QMainWindow, QWidget {
    background: #101820;
    color: #e7eef5;
}
QWidget#Sidebar {
    background: #09131d;
    color: #f8fafc;
    border: 0;
}
QLabel#BrandTitle {
    color: #ffffff;
    font-size: 18px;
    font-weight: 700;
}
QLabel#BrandSubtitle, QLabel#Muted {
    color: #91a4b7;
}
QListWidget#Navigation {
    background: transparent;
    color: #c7d2dc;
    border: 0;
    outline: 0;
}
QListWidget#Navigation::item {
    min-height: 38px;
    padding: 4px 10px;
    margin: 2px 0;
    border-radius: 8px;
}
QListWidget#Navigation::item:selected {
    background: #173750;
    color: #ffffff;
}
QFrame#Card {
    background: #17232d;
    border: 1px solid #2a3a48;
    border-radius: 12px;
}
QLabel#MetricValue {
    font-size: 26px;
    font-weight: 700;
}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {
    background: #17232d;
    color: #edf4fa;
    border: 1px solid #344859;
    border-radius: 8px;
    min-height: 32px;
    padding: 3px 8px;
    selection-background-color: #2c6188;
}
QPushButton {
    background: #1a2a36;
    color: #edf4fa;
    border: 1px solid #344859;
    border-radius: 8px;
    min-height: 32px;
    padding: 4px 12px;
}
QPushButton:hover {
    border-color: #63839b;
}
QPushButton[primary="true"] {
    background: #1e5d86;
    color: #ffffff;
    border-color: #1e5d86;
}
QPushButton[success="true"] {
    background: #187156;
    color: #ffffff;
    border-color: #187156;
}
QHeaderView::section {
    background: #1a2935;
    color: #d9e4ed;
    border: 0;
    border-bottom: 1px solid #314351;
    padding: 7px;
    font-weight: 600;
}
QTableView, QTreeView {
    background: #121e27;
    alternate-background-color: #16242e;
    color: #e7eef5;
    border: 1px solid #314351;
    border-radius: 8px;
    gridline-color: #23333f;
    selection-background-color: #244f6d;
}
QToolBar, QStatusBar, QMenuBar, QMenu {
    background: #121e27;
    color: #e7eef5;
}
QToolBar {
    border-bottom: 1px solid #2a3a48;
}
QStatusBar {
    border-top: 1px solid #2a3a48;
}
QSplitter::handle {
    background: #314351;
    width: 2px;
    height: 2px;
}
QProgressBar {
    border: 1px solid #344859;
    border-radius: 6px;
    text-align: center;
    background: #17232d;
}
QProgressBar::chunk {
    background: #1b8263;
    border-radius: 5px;
}
"""


THEMES = {
    "light": Theme("light", "روشن", LIGHT_QSS),
    "dark": Theme("dark", "تیره", DARK_QSS),
}


def apply_theme(app, key: str) -> str:
    key = key if key in THEMES else "light"
    app.setStyleSheet(THEMES[key].stylesheet)
    return key
