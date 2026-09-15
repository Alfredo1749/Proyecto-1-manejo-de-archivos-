import json
import os

CONFIG_FILENAME = "config.json"
BACKUP_SUFFIX = ".bak"

# Valores por defecto si no hay archivo o hubo error
DEFAULT_CONFIG = {
    "nombre_usuario": "Usuario",
    "tema_interfaz": "claro",
    "idioma": "es",
    "tamano_fuente": 12,
    "color_barra_menu": "#f0f0f0",
    "color_letra": "#000000",
    "foto_perfil": "",
}


class ConfigLoadResult:
    def __init__(self, datos, estado, mensaje=""):
        self.datos = datos
        self.estado = estado  # "ok" | "no_existe" | "corrupto" | "sin_permisos"
        self.mensaje = mensaje


def _copiar_archivo(ruta_origen, ruta_destino):
    with open(ruta_origen, "rb") as archivo_origen:
        contenido = archivo_origen.read()
    with open(ruta_destino, "wb") as archivo_destino:
        archivo_destino.write(contenido)


def cargar_config(ruta=CONFIG_FILENAME):
    if not os.path.exists(ruta):
        return ConfigLoadResult(
            dict(DEFAULT_CONFIG),
            "no_existe",
            "No se encontro configuracion previa. Se usan valores por defecto.",
        )

    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        return ConfigLoadResult(datos, "ok")

    except json.JSONDecodeError:
        # Archivo corrupto: intentar recuperar desde el respaldo
        respaldo = restaurar_desde_respaldo(ruta)
        if respaldo is not None:
            return ConfigLoadResult(
                respaldo,
                "corrupto",
                "Configuracion corrupta. Se restauro desde el respaldo (.bak).",
            )
        return ConfigLoadResult(
            dict(DEFAULT_CONFIG),
            "corrupto",
            "Configuracion corrupta y sin respaldo valido. Valores por defecto.",
        )

    except PermissionError:
        return ConfigLoadResult(
            dict(DEFAULT_CONFIG),
            "sin_permisos",
            "Sin permisos de lectura. Se usan valores por defecto.",
        )


def guardar_config(datos, ruta=CONFIG_FILENAME):
    ruta_temporal = ruta + ".tmp"
    ruta_respaldo = ruta + BACKUP_SUFFIX

    try:
        with open(ruta_temporal, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=4)
            archivo.flush()
            os.fsync(archivo.fileno())

        if os.path.exists(ruta):
            _copiar_archivo(ruta, ruta_respaldo)

        os.replace(ruta_temporal, ruta)
        return True, "Configuracion guardada correctamente."

    except PermissionError:
        if os.path.exists(ruta_temporal):
            try:
                os.remove(ruta_temporal)
            except OSError:
                pass
        return False, "Sin permisos de escritura. No se guardaron los cambios."


def restaurar_desde_respaldo(ruta=CONFIG_FILENAME):
    ruta_respaldo = ruta + BACKUP_SUFFIX

    if not os.path.exists(ruta_respaldo):
        return None

    try:
        with open(ruta_respaldo, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except (json.JSONDecodeError, OSError):
        return None

    _copiar_archivo(ruta_respaldo, ruta)
    return datos
