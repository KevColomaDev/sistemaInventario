import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon

# Importar después de configurar el entorno
from src.main_window import MainWindow

def main():
    # Configurar la aplicación
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Configurar el estilo de la aplicación
    app.setStyleSheet("""
        QMainWindow, QDialog {
            background-color: #F8F0E5;
        }
        
        QPushButton {
            background-color: #DAC0A3;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
            color: #4A4A4A;
            font-weight: 500;
        }
        
        QPushButton:hover {
            background-color: #C8AE7D;
        }
        
        QPushButton:disabled {
            background-color: #EADBC8;
            color: #9E9E9E;
        }
        
        QLineEdit, QComboBox, QTextEdit, QSpinBox, QDoubleSpinBox {
            border: 1px solid #DAC0A3;
            border-radius: 4px;
            padding: 6px 8px;
            background-color: white;
            color: #4A4A4A;
            min-height: 28px;
        }
        
        QTextEdit {
            padding: 4px;
        }
        
        QLabel {
            color: #4A4A4A;
        }
        
        QTableWidget, QTableView {
            background-color: white;
            border: 1px solid #DAC0A3;
            border-radius: 4px;
            gridline-color: #EADBC8;
            selection-background-color: #EADBC8;
        }
        
        QHeaderView::section {
            background-color: #EADBC8;
            padding: 8px;
            border: none;
            font-weight: bold;
        }
        
        QMenuBar {
            background-color: #EADBC8;
            padding: 4px;
            border: none;
        }
        
        QMenuBar::item {
            padding: 4px 8px;
            background: transparent;
            border-radius: 4px;
        }
        
        QMenuBar::item:selected {
            background: #DAC0A3;
        }
        
        QMenu {
            background-color: #F8F0E5;
            border: 1px solid #DAC0A3;
        }
        
        QMenu::item:selected {
            background-color: #EADBC8;
        }
        
        QStatusBar {
            background-color: #EADBC8;
            color: #4A4A4A;
            border-top: 1px solid #DAC0A3;
        }
        
        /* Estilos para diálogos */
        QDialog QLabel {
            font-weight: 500;
        }
        
        QDialog QPushButton {
            min-width: 80px;
        }
        
        /* Estilos para pestañas */
        QTabWidget::pane {
            border: 1px solid #DAC0A3;
            border-radius: 4px;
            background: white;
        }
        
        QTabBar::tab {
            background: #EADBC8;
            border: 1px solid #DAC0A3;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 6px 12px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background: #F8F0E5;
            border-bottom: 1px solid #F8F0E5;
            margin-bottom: -1px;
        }
        
        QTabBar::tab:!selected {
            margin-top: 2px;
        }
    """)
    
    # Configurar fuente
    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
    
    # Crear y mostrar la ventana principal
    window = MainWindow()
    window.show()
    
    # Ejecutar la aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
