
from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QPushButton,
    QLabel,
    QFileDialog,
    QColorDialog,
    QDialogButtonBox,
)
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtCore import Qt


class SettingsDialog(QDialog):
    def __init__(self, config_actual, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(420, 380)

        # Copia de trabajo, no se toca el dict original hasta Guardar
        self._config = dict(config_actual)

        self._construir_formulario()
        self._cargar_valores_actuales()

    def _construir_formulario(self):
        layout_principal = QVBoxLayout(self)
        formulario = QFormLayout()

        self.input_nombre = QLineEdit()
        formulario.addRow("Nombre de usuario:", self.input_nombre)

        self.combo_tema = QComboBox()
        self.combo_tema.addItems(["claro", "oscuro"])
        formulario.addRow("Tema de interfaz:", self.combo_tema)

        self.combo_idioma = QComboBox()
        self.combo_idioma.addItems(["es", "es-ES", "en", "en-US"])
        formulario.addRow("Idioma:", self.combo_idioma)

        self.spin_tamano_fuente = QSpinBox()
        self.spin_tamano_fuente.setRange(8, 72)
        formulario.addRow("Tamano de fuente:", self.spin_tamano_fuente)

        # Color de la barra de menu
        self.boton_color_barra = QPushButton("Elegir color...")
        self.label_preview_barra = QLabel()
        self.label_preview_barra.setFixedSize(24, 24)
        self.boton_color_barra.clicked.connect(self._elegir_color_barra)
        fila_color_barra = QHBoxLayout()
        fila_color_barra.addWidget(self.boton_color_barra)
        fila_color_barra.addWidget(self.label_preview_barra)
        formulario.addRow("Color de la barra de menu:", fila_color_barra)

        # Color de letra
        self.boton_color_letra = QPushButton("Elegir color...")
        self.label_preview_letra = QLabel()
        self.label_preview_letra.setFixedSize(24, 24)
        self.boton_color_letra.clicked.connect(self._elegir_color_letra)
        fila_color_letra = QHBoxLayout()
        fila_color_letra.addWidget(self.boton_color_letra)
        fila_color_letra.addWidget(self.label_preview_letra)
        formulario.addRow("Color de letra:", fila_color_letra)

        # Foto de perfil
        self.boton_foto = QPushButton("Seleccionar imagen...")
        self.boton_foto.clicked.connect(self._elegir_foto_perfil)
        self.label_preview_foto = QLabel("(sin foto)")
        self.label_preview_foto.setFixedSize(64, 64)
        self.label_preview_foto.setAlignment(Qt.AlignCenter)
        self.label_preview_foto.setStyleSheet("border: 1px solid gray;")
        fila_foto = QHBoxLayout()
        fila_foto.addWidget(self.boton_foto)
        fila_foto.addWidget(self.label_preview_foto)
        formulario.addRow("Foto de perfil:", fila_foto)

        layout_principal.addLayout(formulario)

        botones = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        botones.button(QDialogButtonBox.Save).setText("Guardar")
        botones.button(QDialogButtonBox.Cancel).setText("Cancelar")
        botones.accepted.connect(self._al_guardar)
        botones.rejected.connect(self.reject)
        layout_principal.addWidget(botones)

    def _cargar_valores_actuales(self):
        c = self._config
        self.input_nombre.setText(c.get("nombre_usuario", ""))

        idx_tema = self.combo_tema.findText(c.get("tema_interfaz", "claro"))
        self.combo_tema.setCurrentIndex(max(idx_tema, 0))

        idx_idioma = self.combo_idioma.findText(c.get("idioma", "es"))
        self.combo_idioma.setCurrentIndex(max(idx_idioma, 0))

        self.spin_tamano_fuente.setValue(int(c.get("tamano_fuente", 12)))

        self._actualizar_preview_color(
            self.label_preview_barra, c.get("color_barra_menu", "#f0f0f0")
        )
        self._actualizar_preview_color(
            self.label_preview_letra, c.get("color_letra", "#000000")
        )

        ruta_foto = c.get("foto_perfil", "")
        if ruta_foto:
            self._actualizar_preview_foto(ruta_foto)

    # Selectores (color, foto)
  
    def _elegir_color_barra(self):
        color = QColorDialog.getColor(
            QColor(self._config.get("color_barra_menu", "#f0f0f0")), self
        )
        if color.isValid():
            self._config["color_barra_menu"] = color.name()
            self._actualizar_preview_color(self.label_preview_barra, color.name())

    def _elegir_color_letra(self):
        color = QColorDialog.getColor(
            QColor(self._config.get("color_letra", "#000000")), self
        )
        if color.isValid():
            self._config["color_letra"] = color.name()
            self._actualizar_preview_color(self.label_preview_letra, color.name())

    def _elegir_foto_perfil(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar foto de perfil",
            "",
            "Imagenes (*.png *.jpg *.jpeg *.bmp)",
        )
        if ruta:
            self._config["foto_perfil"] = ruta
            self._actualizar_preview_foto(ruta)

    def _actualizar_preview_color(self, label, color_hex):
        label.setStyleSheet(
            f"background-color: {color_hex}; border: 1px solid gray;"
        )

    def _actualizar_preview_foto(self, ruta):
        pixmap = QPixmap(ruta)
        if not pixmap.isNull():
            self.label_preview_foto.setPixmap(
                pixmap.scaled(
                    64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            )
        else:
            self.label_preview_foto.setText("(invalida)")

    def _al_guardar(self):
        self._config["nombre_usuario"] = self.input_nombre.text()
        self._config["tema_interfaz"] = self.combo_tema.currentText()
        self._config["idioma"] = self.combo_idioma.currentText()
        self._config["tamano_fuente"] = self.spin_tamano_fuente.value()
        # colores y foto ya estan en self._config desde que se eligieron
        self.accept()

    def obtener_configuracion(self):
        return self._config
