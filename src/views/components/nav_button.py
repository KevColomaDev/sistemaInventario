from PyQt6.QtWidgets import QPushButton, QSizePolicy, QStyle
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap

class NavButton(QPushButton):
    def __init__(self, text, icon_path="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(40)
        
        # Estilo base
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #4A4A4A;
                text-align: left;
                padding: 8px 16px 8px 12px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: 500;
                spacing: 8px;
            }
            
            QPushButton:hover {
                background-color: rgba(202, 179, 137, 0.2);
            }
            
            QPushButton:pressed {
                background-color: rgba(202, 179, 137, 0.3);
            }
            
            QPushButton:checked {
                background-color: #DAC0A3;
                color: #4A4A4A;
                font-weight: 600;
            }
            
            QPushButton::icon {
                width: 20px;
                height: 20px;
                margin-right: 8px;
            }
        """)
        
        # Hacer que el botón sea checkeable
        self.setCheckable(True)
        self.setAutoExclusive(True)
