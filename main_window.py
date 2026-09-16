from PyQt5.QtWidgets import (
    QMainWindow,
    QLabel,
    QMessageBox,
    QAction,
)
from PyQt5.QtCore import Qt

import config_manager
from settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config_actual = {}

        self.setWindowTitle("Gestion de Configuracion de Usuario")
        self.resize(600, 400)

        self.label_estado = QLabel(
            "Cargando configuracion...", alignment=Qt.AlignCenter
        )
        self.label_estado.setWordWrap(True)
        self.setCentralWidget(self.label_estado)

        self._crear_menu()
        self._cargar_configuracion_inicial()

    def _crear_menu(self):
        barra_menu = self.menuBar()

        menu_archivo = barra_menu.addMenu("Archivo")
        self._agregar_accion_simulada(menu_archivo, "Nuevo")
        self._agregar_accion_simulada(menu_archivo, "Abrir")
        self._agregar_accion_simulada(menu_archivo, "Guardar")
        menu_archivo.addSeparator()
        accion_salir = QAction("Salir", self)
        accion_salir.triggered.connect(self.close)
        menu_archivo.addAction(accion_salir)

        menu_edicion = barra_menu.addMenu("Edicion")
        self._agregar_accion_simulada(menu_edicion, "Copiar")
        self._agregar_accion_simulada(menu_edicion, "Pegar")

        menu_ver = barra_menu.addMenu("Ver")
        self._agregar_accion_simulada(menu_ver, "Zoom")
        self._agregar_accion_simulada(menu_ver, "Pantalla completa")

        menu_settings = barra_menu.addMenu("Settings")
        accion_abrir_settings = QAction("Abrir Settings...", self)
        accion_abrir_settings.triggered.connect(self.abrir_settings)
        menu_settings.addAction(accion_abrir_settings)

    def _agregar_accion_simulada(self, menu, texto):
        """Accion sin funcionalidad real, solo muestra un mensaje."""
        accion = QAction(texto, self)
        accion.triggered.connect(
            lambda: QMessageBox.information(
                self, texto, f"Opcion '{texto}' simulada (sin funcionalidad real)."
            )
        )
        menu.addAction(accion)

    def _cargar_configuracion_inicial(self):
        resultado = config_manager.cargar_config()
        self.config_actual = resultado.datos

        if resultado.estado != "ok":
            QMessageBox.warning(self, "Configuracion", resultado.mensaje)

        self._aplicar_configuracion_a_la_vista()

    def _aplicar_configuracion_a_la_vista(self):
        c = self.config_actual
        self.label_estado.setText(
            f"Usuario: {c.get('nombre_usuario', '')}\n"
            f"Tema: {c.get('tema_interfaz', '')}\n"
            f"Idioma: {c.get('idioma', '')}\n"
            f"Tamano de fuente: {c.get('tamano_fuente', '')}"
        )

        color_barra = c.get("color_barra_menu", "#f0f0f0")
        color_letra = c.get("color_letra", "#000000")
        tamano_fuente = c.get("tamano_fuente", 12)
        tema = c.get("tema_interfaz", "claro")

        color_fondo = "#2b2b2b" if tema == "oscuro" else "#ffffff"

        self.menuBar().setStyleSheet(
            f"QMenuBar {{ background-color: {color_barra}; color: {color_letra}; }}"
        )
        self.label_estado.setStyleSheet(
            f"color: {color_letra}; font-size: {tamano_fuente}px; "
            f"background-color: {color_fondo};"
        )
        self.setStyleSheet(f"QMainWindow {{ background-color: {color_fondo}; }}")

    def abrir_settings(self):
        dialogo = SettingsDialog(self.config_actual, self)

        if dialogo.exec_():  # True si el usuario presiono "Guardar"
            nueva_config = dialogo.obtener_configuracion()
            exito, mensaje = config_manager.guardar_config(nueva_config)

            if exito:
                self.config_actual = nueva_config
                self._aplicar_configuracion_a_la_vista()
                QMessageBox.information(self, "Settings", mensaje)
            else:
                QMessageBox.critical(self, "Error al guardar", mensaje)
