from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLineEdit, QTextEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.models.categoria import Categoria

class CategoriaDialog(QDialog):
    categoria_guardada = pyqtSignal()
    
    def __init__(self, categoria_id=None, parent=None):
        super().__init__(parent)
        self.categoria_id = categoria_id
        self.setWindowTitle("Nueva Categoría" if categoria_id is None else "Editar Categoría")
        self.setMinimumWidth(500)
        
        self.setup_ui()
        
        if categoria_id is not None:
            self.cargar_categoria()
    
    def setup_ui(self):
        """Configura la interfaz de usuario del diálogo"""
        layout = QVBoxLayout(self)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        # Nombre
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre de la categoría")
        self.nombre_input.returnPressed.connect(self.guardar_categoria)  # Enter key press
        form_layout.addRow("Nombre*:", self.nombre_input)
        
        # Descripción
        self.descripcion_input = QTextEdit()
        self.descripcion_input.setPlaceholderText("Descripción de la categoría")
        self.descripcion_input.setMaximumHeight(100)
        form_layout.addRow("Descripción:", self.descripcion_input)
        
        # Configurar el botón de guardar como predeterminado
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()
        
        layout.addLayout(form_layout)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Configurar botón de guardar como predeterminado
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.clicked.connect(self.guardar_categoria)
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_cancelar)
        button_layout.addWidget(self.btn_guardar)
        
        layout.addLayout(button_layout)
        
        # Configurar el botón de guardar como predeterminado
        self.btn_guardar.setDefault(True)
        
        # Configurar estilos
        self.setup_styles()
    
    def setup_styles(self):
        """Configura los estilos del diálogo"""
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F0E5;
            }
            
            QLineEdit, QTextEdit {
                padding: 6px 8px;
                border: 1px solid #DAC0A3;
                border-radius: 4px;
                background-color: white;
                color: #4A4A4A;
            }
            
            QTextEdit {
                padding: 4px;
            }
            
            QPushButton {
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                font-weight: 500;
                min-width: 80px;
            }
            
            QPushButton#btn_guardar {
                background-color: #A8E6CF;
                color: #1B5E20;
            }
            
            QPushButton#btn_cancelar {
                background-color: #FFD3B6;
                color: #BF360C;
            }
            
            QPushButton:hover {
                opacity: 0.9;
            }
            
            QPushButton:pressed {
                opacity: 0.8;
            }
            
            QLabel {
                color: #4A4A4A;
                font-weight: 500;
            }
        """)
        
        # Aplicar estilos específicos a los botones
        self.btn_guardar.setObjectName("btn_guardar")
        self.btn_cancelar.setObjectName("btn_cancelar")
    
    def cargar_categoria(self):
        """Carga los datos de la categoría en el formulario"""
        if self.categoria_id is None:
            return
            
        categoria = Categoria.obtener_por_id(self.categoria_id)
        if not categoria:
            QMessageBox.critical(self, "Error", "No se pudo cargar la categoría.")
            self.reject()
            return
        
        self.setWindowTitle(f"Editar: {categoria.nombre}")
        self.nombre_input.setText(categoria.nombre)
        self.descripcion_input.setPlainText(categoria.descripcion or "")
    
    def validar_formulario(self):
        """Valida los datos del formulario"""
        errores = []
        
        nombre = self.nombre_input.text().strip()
        
        if not nombre:
            errores.append("El nombre es obligatorio")
        
        # Verificar si el nombre ya existe (solo para nueva categoría)
        if self.categoria_id is None and nombre:
            # Verificar si ya existe una categoría con el mismo nombre
            categorias = Categoria.buscar_por_nombre(nombre)
            if categorias:
                errores.append("Ya existe una categoría con este nombre")
        
        return errores
    
    def guardar_categoria(self):
        """Guarda o actualiza la categoría"""
        errores = self.validar_formulario()
        if errores:
            QMessageBox.warning(
                self,
                "Error de validación",
                "Por favor, corrija los siguientes errores:\n\n• " + "\n• ".join(errores)
            )
            return
        
        # Crear o actualizar la categoría
        categoria = Categoria(
            id=self.categoria_id,
            nombre=self.nombre_input.text().strip(),
            descripcion=self.descripcion_input.toPlainText().strip()
        )
        
        try:
            if self.categoria_id is None:
                # Nueva categoría
                categoria_id = categoria.guardar()
                if categoria_id:
                    QMessageBox.information(
                        self,
                        "Categoría guardada",
                        f"La categoría '{categoria.nombre}' ha sido guardada correctamente."
                    )
                    self.categoria_guardada.emit()
                    self.accept()
            else:
                # Actualizar categoría existente
                if categoria.actualizar() is not None:
                    QMessageBox.information(
                        self,
                        "Categoría actualizada",
                        f"Los datos de '{categoria.nombre}' han sido actualizados correctamente."
                    )
                    self.categoria_guardada.emit()
                    self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo guardar la categoría: {str(e)}"
            )
