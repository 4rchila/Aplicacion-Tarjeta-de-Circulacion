# ============================================================
#  client.py  –  Cliente PyQt6  (ejecutar después del servidor)
#  Uso: python client.py
# ============================================================

import sys
import socket
import json
import struct
from datetime import date
from config import SERVER_HOST, SERVER_PORT

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QFrame,
    QGroupBox, QScrollArea, QMessageBox, QStackedWidget,
    QSpinBox, QDoubleSpinBox, QDateEdit, QSizePolicy,
    QSplitter, QListWidget, QListWidgetItem, QRadioButton,
    QButtonGroup, QTextEdit, QStatusBar,
)
from PyQt6.QtCore import Qt, QDate, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QColor, QPalette


# ════════════════════════════════════════════════════════════
#  Comunicación con el servidor
# ════════════════════════════════════════════════════════════

class ServerError(Exception):
    pass

class Server:
    """Singleton de conexión al servidor TCP."""

    def __init__(self):
        self._sock: socket.socket | None = None

    def connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(10)
        self._sock.connect((SERVER_HOST, SERVER_PORT))

    def disconnect(self):
        if self._sock:
            self._sock.close()
            self._sock = None

    def call(self, action: str, params: dict = None) -> dict | list:
        if params is None:
            params = {}
        payload = json.dumps({"action": action, "params": params},
                             ensure_ascii=False).encode("utf-8")
        self._sock.sendall(struct.pack(">I", len(payload)) + payload)

        raw = self._recvall(4)
        length = struct.unpack(">I", raw)[0]
        data = json.loads(self._recvall(length).decode("utf-8"))

        if not data.get("success"):
            raise ServerError(data.get("error", "Error desconocido"))
        return data["data"]

    def _recvall(self, n: int) -> bytes:
        buf = b""
        while len(buf) < n:
            chunk = self._sock.recv(n - len(buf))
            if not chunk:
                raise ServerError("Conexión cerrada por el servidor")
            buf += chunk
        return buf


server = Server()


# ════════════════════════════════════════════════════════════
#  Tema oscuro moderno — Design System
# ════════════════════════════════════════════════════════════

# Paleta principal
BG_DARK    = "#0f1923"
BG_CARD    = "#162032"
BG_CARD2   = "#1b2a3f"
BG_INPUT   = "#0d1520"
ACCENT     = "#00d2ff"
ACCENT2    = "#7a5af5"
ACCENT_G   = "qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #00d2ff, stop:1 #7a5af5)"
VERDE      = "#00e676"
VERDE_D    = "#00c853"
ROJO       = "#ff5252"
ROJO_D     = "#d32f2f"
NARANJA    = "#ffab40"
TEXTO      = "#e8eaf6"
TEXTO_SEC  = "#8892b0"
BORDE      = "#2a3a52"
BORDE_L    = "#3d5278"
GRIS_BG    = BG_DARK      # fondo general de la ventana
BLANCO     = BG_CARD      # fondo de paneles/tarjetas
GRIS_B     = BORDE        # color de bordes en listas
GRIS_T     = TEXTO_SEC    # texto secundario / gris claro
AZUL       = ACCENT       # color de acento azul principal

ESTILO_BTN_PRIMARIO = f"""
    QPushButton {{
        background: {ACCENT_G};
        color: #0f1923;
        border: none;
        border-radius: 8px;
        padding: 10px 22px;
        font-weight: bold;
        font-size: 13px;
    }}
    QPushButton:hover {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #33dbff, stop:1 #9a7ff7); }}
    QPushButton:disabled {{ background: #2a3a52; color: #5a6a7a; }}
"""
ESTILO_BTN_VERDE = f"""
    QPushButton {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #00e676, stop:1 #00c853);
        color: #0f1923;
        border: none;
        border-radius: 8px;
        padding: 10px 22px;
        font-weight: bold;
        font-size: 13px;
    }}
    QPushButton:hover {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #33eb91, stop:1 #2ecc71); }}
"""
ESTILO_BTN_ROJO = f"""
    QPushButton {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ff5252, stop:1 #d32f2f);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 22px;
        font-weight: bold;
        font-size: 13px;
    }}
    QPushButton:hover {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ff7575, stop:1 #e53935); }}
"""
ESTILO_BTN_GRIS = f"""
    QPushButton {{
        background: {BG_CARD2};
        color: {TEXTO_SEC};
        border: 1px solid {BORDE};
        border-radius: 8px;
        padding: 10px 22px;
        font-size: 13px;
    }}
    QPushButton:hover {{ background: #243550; border-color: {ACCENT}; color: {TEXTO}; }}
"""

# ── Estilos globales para widgets de entrada ────────────────
_INPUT_BASE = f"""
    border: 1px solid {BORDE};
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 13px;
    background: {BG_INPUT};
    color: {TEXTO};
    selection-background-color: {ACCENT};
"""
_INPUT_FOCUS = f"border-color: {ACCENT};"

_COMBO_STYLE = f"""
    QComboBox {{
        {_INPUT_BASE}
        min-height: 28px;
    }}
    QComboBox:focus {{ {_INPUT_FOCUS} }}
    QComboBox::drop-down {{
        border: none; width: 28px;
    }}
    QComboBox::down-arrow {{
        image: none; border-left: 4px solid transparent; border-right: 4px solid transparent;
        border-top: 6px solid {TEXTO_SEC}; margin-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background: {BG_CARD}; color: {TEXTO}; border: 1px solid {BORDE};
        selection-background-color: #243550;
    }}
"""

_GROUPBOX_STYLE = f"""
    QGroupBox {{
        font-weight: bold; font-size: 13px; color: {ACCENT};
        border: 1px solid {BORDE}; border-radius: 10px;
        margin-top: 12px; padding: 14px 10px 10px 10px;
        background: {BG_CARD};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin; left: 14px; padding: 0 6px;
        color: {ACCENT};
    }}
    QGroupBox QLabel {{
        color: {TEXTO};
        font-size: 13px;
        background: transparent;
    }}
"""

_SCROLL_STYLE = f"""
    QScrollArea {{ border: none; background: transparent; }}
    QScrollBar:vertical {{
        background: {BG_DARK}; width: 8px; border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDE_L}; border-radius: 4px; min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{ background: {ACCENT}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
"""


def separador():
    l = QFrame()
    l.setFrameShape(QFrame.Shape.HLine)
    l.setFixedHeight(1)
    l.setStyleSheet(f"background: {BORDE}; border: none;")
    return l

def titulo(texto, tamaño=15, negrita=True):
    lbl = QLabel(texto)
    f = lbl.font()
    f.setPointSize(tamaño)
    f.setBold(negrita)
    lbl.setFont(f)
    lbl.setStyleSheet(f"color: {TEXTO};")
    return lbl

def etiqueta_info(clave, valor, color_val=None):
    """Devuelve un QLabel con formato 'Clave: valor'."""
    c = color_val or ACCENT
    lbl = QLabel(f"<b style='color:{TEXTO_SEC}'>{clave}:</b>  <span style='color:{c}'>{valor}</span>")
    lbl.setTextFormat(Qt.TextFormat.RichText)
    return lbl

def grupo(titulo_str, widget_hijo=None):
    gb = QGroupBox(titulo_str)
    gb.setStyleSheet(_GROUPBOX_STYLE)
    if widget_hijo:
        ly = QVBoxLayout()
        ly.addWidget(widget_hijo)
        gb.setLayout(ly)
    return gb

def combo_de_lista(datos, id_campo, desc_campo):
    """Crea QComboBox a partir de lista de dicts."""
    cb = QComboBox()
    cb.setStyleSheet(_COMBO_STYLE)
    cb.addItem("-- Seleccionar --", None)
    for d in datos:
        cb.addItem(str(d[desc_campo]), d[id_campo])
    return cb

def input_line(placeholder="", max_w=None):
    le = QLineEdit()
    le.setPlaceholderText(placeholder)
    le.setMinimumHeight(34)
    if max_w:
        le.setMaximumWidth(max_w)
    le.setStyleSheet(f"""
        QLineEdit {{ {_INPUT_BASE} }}
        QLineEdit:focus {{ {_INPUT_FOCUS} }}
    """)
    return le

def spin(minv=0, maxv=9999, val=0):
    s = QSpinBox()
    s.setRange(minv, maxv)
    s.setValue(val)
    s.setMinimumHeight(34)
    s.setStyleSheet(f"QSpinBox {{ {_INPUT_BASE} }} QSpinBox:focus {{ {_INPUT_FOCUS} }}")
    return s

def dspin(minv=0.0, maxv=99999.0, val=0.0, dec=2):
    s = QDoubleSpinBox()
    s.setRange(minv, maxv)
    s.setValue(val)
    s.setDecimals(dec)
    s.setMinimumHeight(34)
    s.setStyleSheet(f"QDoubleSpinBox {{ {_INPUT_BASE} }} QDoubleSpinBox:focus {{ {_INPUT_FOCUS} }}")
    return s

def date_edit(valor: QDate = None):
    de = QDateEdit(valor or QDate.currentDate())
    de.setCalendarPopup(True)
    de.setMinimumHeight(34)
    de.setDisplayFormat("yyyy-MM-dd")
    de.setStyleSheet(f"QDateEdit {{ {_INPUT_BASE} }} QDateEdit:focus {{ {_INPUT_FOCUS} }}")
    return de

def btn(texto, estilo=ESTILO_BTN_PRIMARIO, ancho=None):
    b = QPushButton(texto)
    b.setStyleSheet(estilo)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    if ancho:
        b.setFixedWidth(ancho)
    return b

def scroll_widget(widget):
    sc = QScrollArea()
    sc.setWidget(widget)
    sc.setWidgetResizable(True)
    sc.setFrameShape(QFrame.Shape.NoFrame)
    sc.setStyleSheet(_SCROLL_STYLE)
    return sc


# ════════════════════════════════════════════════════════════
#  Widget reutilizable: tarjeta de resultados
# ════════════════════════════════════════════════════════════

class TarjetaInfoWidget(QWidget):
    """Muestra todos los datos de una tarjeta de circulación."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(10)
        self.setStyleSheet(f"background:{BG_DARK};")

    def limpiar(self):
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def mostrar(self, t: dict):
        self.limpiar()

        def estado_color(e):
            e = (e or "").upper()
            if "ACTIVA" in e and "IN" not in e:
                return VERDE
            return ROJO

        # ── Encabezado ──────────────────────────────
        encabezado = QFrame()
        encabezado.setStyleSheet(f"""
            background: {ACCENT_G};
            border-radius: 10px;
            padding: 12px;
        """)
        h_ly = QHBoxLayout(encabezado)
        lbl_num = QLabel(f"Tarjeta: {t.get('numero_tarjeta','—')}")
        lbl_num.setStyleSheet("color:#0f1923; font-size:16px; font-weight:bold;")
        lbl_est = QLabel(t.get("tarjeta_estado","—"))
        lbl_est.setStyleSheet(
            f"color:white; background:{estado_color(t.get('tarjeta_estado',''))};"
            f"border-radius:6px; padding:5px 14px; font-weight:bold; font-size:12px;"
        )
        h_ly.addWidget(lbl_num)
        h_ly.addStretch()
        h_ly.addWidget(lbl_est)
        self._layout.addWidget(encabezado)

        # ── Grid de secciones ────────────────────────
        grid = QWidget()
        grid.setStyleSheet(f"background: {BG_DARK};")
        gl = QGridLayout(grid)
        gl.setSpacing(10)

        def seccion(titulo_s, campos):
            gb = QGroupBox(titulo_s)
            gb.setStyleSheet(_GROUPBOX_STYLE)
            fl = QFormLayout()
            fl.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
            fl.setHorizontalSpacing(12)
            fl.setVerticalSpacing(6)
            for llave, val, *extra in campos:
                color = extra[0] if extra else ACCENT
                val_lbl = QLabel(str(val) if val else "—")
                val_lbl.setStyleSheet(f"color:{color}; font-size:12px; background:transparent;")
                key_lbl = QLabel(f"<b>{llave}</b>")
                key_lbl.setStyleSheet(f"color:{TEXTO_SEC}; font-size:12px; background:transparent;")
                fl.addRow(key_lbl, val_lbl)
            gb.setLayout(fl)
            return gb

        nombre_completo = " ".join(filter(None, [
            t.get("primer_nombre"), t.get("segundo_nombre"),
            t.get("primer_apellido"), t.get("segundo_apellido")
        ]))

        sec_tarjeta = seccion("📋 Tarjeta de Circulación", [
            ("Código SAT",        t.get("codigo_sat")),
            ("Fecha de Emisión",  t.get("fecha_emision")),
            ("Fecha Vencimiento", t.get("fecha_vencimiento")),
            ("NIT Propietario",   t.get("nit_propietario")),
        ])

        sec_propietario = seccion("👤 Propietario", [
            ("Nombre Completo", nombre_completo),
            ("NIT",             t.get("nit_propietario")),
            ("CUI",             t.get("cui")),
        ])

        sec_vehiculo = seccion("🚗 Vehículo", [
            ("Chasis",       t.get("chasis")),
            ("VIN",          t.get("vin")),
            ("Serie",        t.get("serie")),
            ("N.° Motor",    t.get("numero_motor")),
            ("Año Modelo",   t.get("anio_modelo")),
            ("Tipo",         t.get("tipo_vehiculo")),
            ("Marca",        t.get("marca")),
            ("Línea",        t.get("linea")),
            ("Color",        t.get("color")),
            ("Uso",          t.get("uso")),
            ("Asientos",     t.get("asientos")),
            ("Ejes",         t.get("ejes")),
            ("Cilindros",    t.get("cilindros")),
            ("Cilindraje cc",t.get("cilindraje_cc")),
            ("Tonelaje",     t.get("tonelaje")),
        ])

        sec_placa = seccion("🪪 Placa", [
            ("Número de Placa",    t.get("numero_placa")),
            ("Fecha Asignación",   t.get("placa_fecha")),
            ("Estado Placa",       t.get("placa_estado"),
             estado_color(t.get("placa_estado",""))),
        ])

        sec_cui = seccion("🔐 Código Único Identificador", [
            ("N.° CUI",           t.get("numero_cui")),
            ("Código QR",         t.get("codigo_qr")),
            ("Fecha Generación",  t.get("cui_fecha")),
        ])

        gl.addWidget(sec_tarjeta,     0, 0)
        gl.addWidget(sec_propietario, 0, 1)
        gl.addWidget(sec_vehiculo,    1, 0)
        gl.addWidget(sec_placa,       1, 1)
        gl.addWidget(sec_cui,         2, 0, 1, 2)

        self._layout.addWidget(grid)
        self._layout.addStretch()


# ════════════════════════════════════════════════════════════
#  TAB 1 – Consultar
# ════════════════════════════════════════════════════════════

class TabConsultar(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background:{GRIS_BG};")
        main = QVBoxLayout(self)
        main.setSpacing(12)
        main.setContentsMargins(16, 16, 16, 16)

        # ── Barra de búsqueda ──────────────────────────────
        barra = QFrame()
        barra.setStyleSheet(f"background:{BLANCO}; border-radius:8px; padding:6px;")
        b_ly = QHBoxLayout(barra)

        b_ly.addWidget(QLabel("Buscar por:"))
        self.combo_campo = QComboBox()
        self.combo_campo.addItems([
            "Número de Tarjeta", "Número de Placa", "Chasis", "NIT Propietario"
        ])
        self.combo_campo.setMinimumWidth(180)
        b_ly.addWidget(self.combo_campo)

        self.inp_buscar = input_line("Ingrese el valor...")
        b_ly.addWidget(self.inp_buscar, 1)

        self.btn_buscar = btn("🔍  Buscar")
        self.btn_buscar.clicked.connect(self._buscar)
        b_ly.addWidget(self.btn_buscar)

        main.addWidget(barra)

        # ── Splitter: lista | detalle ──────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Lista de resultados
        panel_lista = QWidget()
        panel_lista.setStyleSheet(f"background:{BLANCO}; border-radius:8px;")
        pl_ly = QVBoxLayout(panel_lista)
        pl_ly.addWidget(titulo("Resultados", 13))
        self.lista = QListWidget()
        self.lista.setStyleSheet(f"""
            QListWidget {{ border:none; font-size:13px; }}
            QListWidget::item {{ padding:8px; border-bottom:1px solid {GRIS_B}; }}
            QListWidget::item:selected {{ background:{AZUL}; color:white; border-radius:4px; }}
        """)
        self.lista.currentRowChanged.connect(self._mostrar_detalle)
        pl_ly.addWidget(self.lista)
        panel_lista.setMinimumWidth(220)
        panel_lista.setMaximumWidth(300)

        # Área de detalle
        self._tarjetas: list[dict] = []
        self.detalle_widget = TarjetaInfoWidget()
        self.detalle_scroll = scroll_widget(self.detalle_widget)

        splitter.addWidget(panel_lista)
        splitter.addWidget(self.detalle_scroll)
        splitter.setSizes([240, 700])

        main.addWidget(splitter, 1)

        # Enter para buscar
        self.inp_buscar.returnPressed.connect(self._buscar)

    _CAMPOS = {
        "Número de Tarjeta":  "numero_tarjeta",
        "Número de Placa":    "numero_placa",
        "Chasis":             "chasis",
        "NIT Propietario":    "nit",
    }

    def _buscar(self):
        valor = self.inp_buscar.text().strip()
        if not valor:
            QMessageBox.warning(self, "Aviso", "Ingrese un valor para buscar.")
            return
        campo = self._CAMPOS[self.combo_campo.currentText()]
        try:
            datos = server.call("consultar_tarjeta", {"campo": campo, "valor": valor})
            self._tarjetas = datos
            self.lista.clear()
            if not datos:
                QMessageBox.information(self, "Sin resultados", "No se encontraron tarjetas.")
                self.detalle_widget.limpiar()
                return
            for t in datos:
                item = QListWidgetItem(
                    f"🪪 {t.get('numero_tarjeta','')}\n"
                    f"   {t.get('primer_nombre','')} {t.get('primer_apellido','')}"
                )
                self.lista.addItem(item)
            self.lista.setCurrentRow(0)
        except ServerError as e:
            QMessageBox.critical(self, "Error del servidor", str(e))

    def _mostrar_detalle(self, row):
        if 0 <= row < len(self._tarjetas):
            self.detalle_widget.mostrar(self._tarjetas[row])


# ════════════════════════════════════════════════════════════
#  TAB 2 – Nueva Tarjeta (wizard de 4 pasos)
# ════════════════════════════════════════════════════════════

class TabNuevaTarjeta(QWidget):

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background:{GRIS_BG};")
        self._prop  = None   # dict propietario seleccionado
        self._veh   = None   # dict vehículo seleccionado
        self._marcas  = []
        self._lineas  = []
        self._colores = []
        self._tipos   = []
        self._usos    = []

        main = QVBoxLayout(self)
        main.setContentsMargins(16, 16, 16, 16)
        main.setSpacing(10)

        # Barra de pasos
        self._indicador = QLabel()
        self._indicador.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._indicador.setStyleSheet(f"font-size:13px; color:{GRIS_T};")
        main.addWidget(self._indicador)
        main.addWidget(separador())

        self._stack = QStackedWidget()
        main.addWidget(self._stack, 1)

        nav = QHBoxLayout()
        self.btn_atras  = btn("◀  Atrás",   ESTILO_BTN_GRIS)
        self.btn_sig    = btn("Siguiente  ▶")
        self.btn_crear  = btn("✅  Crear Tarjeta", ESTILO_BTN_VERDE)
        self.btn_crear.hide()
        nav.addWidget(self.btn_atras)
        nav.addStretch()
        nav.addWidget(self.btn_sig)
        nav.addWidget(self.btn_crear)
        main.addLayout(nav)

        self._construir_paso1()
        self._construir_paso2()
        self._construir_paso3()
        self._construir_paso4()

        self.btn_atras.clicked.connect(self._atras)
        self.btn_sig.clicked.connect(self._siguiente)
        self.btn_crear.clicked.connect(self._crear_todo)

        self._ir_a(0)

    # ─── Paso 1: Propietario ─────────────────────────────

    def _construir_paso1(self):
        w = QWidget()
        ly = QVBoxLayout(w)
        ly.setSpacing(8)
        ly.addWidget(titulo("Paso 1 – Propietario", 14))
        ly.addWidget(separador())

        # Búsqueda
        b = QHBoxLayout()
        self.inp_nit = input_line("NIT del propietario")
        self.btn_buscar_prop = btn("Buscar", ancho=90)
        self.btn_buscar_prop.clicked.connect(self._buscar_propietario)
        b.addWidget(QLabel("NIT:"))
        b.addWidget(self.inp_nit, 1)
        b.addWidget(self.btn_buscar_prop)
        ly.addLayout(b)
        ly.addWidget(separador())

        # Formulario
        gb = QGroupBox("Datos del Propietario (rellenar si es nuevo)")
        fl = QFormLayout()
        self.p_cui  = input_line("CUI (DPI)")
        self.p_pn   = input_line("Primer nombre")
        self.p_sn   = input_line("Segundo nombre (opcional)")
        self.p_pa   = input_line("Primer apellido")
        self.p_sa   = input_line("Segundo apellido (opcional)")
        fl.addRow("NIT *",            self.inp_nit)
        fl.addRow("CUI *",            self.p_cui)
        fl.addRow("Primer nombre *",  self.p_pn)
        fl.addRow("Segundo nombre",   self.p_sn)
        fl.addRow("Primer apellido *",self.p_pa)
        fl.addRow("Segundo apellido", self.p_sa)
        gb.setLayout(fl)
        ly.addWidget(gb)
        ly.addStretch()

        self._stack.addWidget(scroll_widget(w))

    def _buscar_propietario(self):
        nit = self.inp_nit.text().strip()
        if not nit:
            return
        try:
            p = server.call("buscar_propietario", {"nit": nit})
            if p:
                self._prop = p
                self.p_cui.setText(p.get("cui",""))
                self.p_pn.setText(p.get("primer_nombre",""))
                self.p_sn.setText(p.get("segundo_nombre",""))
                self.p_pa.setText(p.get("primer_apellido",""))
                self.p_sa.setText(p.get("segundo_apellido",""))
                QMessageBox.information(self, "Propietario encontrado",
                    f"✔ {p['primer_nombre']} {p['primer_apellido']} (NIT: {p['nit']})")
            else:
                self._prop = None
                QMessageBox.information(self, "No encontrado",
                    "NIT no registrado. Complete los datos para crear el propietario.")
        except ServerError as e:
            QMessageBox.critical(self, "Error", str(e))

    # ─── Paso 2: Vehículo ────────────────────────────────

    def _construir_paso2(self):
        w = QWidget()
        ly = QVBoxLayout(w)
        ly.setSpacing(8)
        ly.addWidget(titulo("Paso 2 – Vehículo", 14))
        ly.addWidget(separador())

        b = QHBoxLayout()
        self.inp_chasis = input_line("Número de chasis")
        btn_bv = btn("Buscar", ancho=90)
        btn_bv.clicked.connect(self._buscar_vehiculo)
        b.addWidget(QLabel("Chasis:"))
        b.addWidget(self.inp_chasis, 1)
        b.addWidget(btn_bv)
        ly.addLayout(b)
        ly.addWidget(separador())

        gb = QGroupBox("Datos del Vehículo (rellenar si es nuevo)")
        fl = QFormLayout()
        self.v_vin   = input_line("VIN")
        self.v_serie = input_line("Serie")
        self.v_motor = input_line("Número de motor")
        self.v_anio  = spin(1900, 2100, date.today().year)
        self.v_asientos  = spin(1, 100, 5)
        self.v_ejes      = spin(1, 20, 2)
        self.v_cilindros = spin(1, 20, 4)
        self.v_cc        = spin(0, 32767, 1600)
        self.v_tonelaje  = dspin(0, 999, 1, 2)

        # Catálogos (se cargan al activar la pestaña)
        self.v_tipo   = QComboBox(); self.v_tipo.addItem("-- cargando --")
        self.v_marca  = QComboBox(); self.v_marca.addItem("-- cargando --")
        self.v_linea  = QComboBox(); self.v_linea.addItem("-- cargando --")
        self.v_color  = QComboBox(); self.v_color.addItem("-- cargando --")
        self.v_uso    = QComboBox(); self.v_uso.addItem("-- cargando --")

        self.v_marca.currentIndexChanged.connect(self._actualizar_lineas)

        fl.addRow("Chasis *",      self.inp_chasis)
        fl.addRow("VIN",           self.v_vin)
        fl.addRow("Serie",         self.v_serie)
        fl.addRow("N.° Motor *",   self.v_motor)
        fl.addRow("Año modelo *",  self.v_anio)
        fl.addRow("Tipo *",        self.v_tipo)
        fl.addRow("Marca *",       self.v_marca)
        fl.addRow("Línea *",       self.v_linea)
        fl.addRow("Color *",       self.v_color)
        fl.addRow("Uso *",         self.v_uso)
        fl.addRow("Asientos",      self.v_asientos)
        fl.addRow("Ejes",          self.v_ejes)
        fl.addRow("Cilindros",     self.v_cilindros)
        fl.addRow("Cilindraje cc", self.v_cc)
        fl.addRow("Tonelaje",      self.v_tonelaje)
        gb.setLayout(fl)
        ly.addWidget(gb)
        ly.addStretch()
        self._stack.addWidget(scroll_widget(w))

    def _cargar_catalogos(self):
        try:
            self._marcas  = server.call("listar_marcas")
            self._colores = server.call("listar_colores")
            self._tipos   = server.call("listar_tipos")
            self._usos    = server.call("listar_usos")

            def fill(cb, lista, id_f, desc_f):
                cb.blockSignals(True)
                cb.clear()
                cb.addItem("-- Seleccionar --", None)
                for d in lista:
                    cb.addItem(str(d[desc_f]), d[id_f])
                cb.blockSignals(False)

            fill(self.v_tipo,  self._tipos,   "id_tipo",  "descripcion")
            fill(self.v_marca, self._marcas,  "id_marca", "nombre")
            fill(self.v_color, self._colores, "id_color", "descripcion")
            fill(self.v_uso,   self._usos,    "id_uso",   "descripcion")
            self._actualizar_lineas()

            # También para mantenimiento color
            if hasattr(self, "m_color"):
                self.m_color.clear()
                self.m_color.addItem("-- Seleccionar --", None)
                for d in self._colores:
                    self.m_color.addItem(d["descripcion"], d["id_color"])
        except ServerError as e:
            QMessageBox.warning(self, "Error al cargar catálogos", str(e))

    def _actualizar_lineas(self):
        id_marca = self.v_marca.currentData()
        try:
            lineas = server.call("listar_lineas", {"id_marca": id_marca} if id_marca else {})
            self.v_linea.blockSignals(True)
            self.v_linea.clear()
            self.v_linea.addItem("-- Seleccionar --", None)
            for d in lineas:
                self.v_linea.addItem(d["nombre"], d["id_linea"])
            self.v_linea.blockSignals(False)
        except ServerError:
            pass

    def _buscar_vehiculo(self):
        chasis = self.inp_chasis.text().strip()
        if not chasis:
            return
        try:
            v = server.call("buscar_vehiculo", {"chasis": chasis})
            if v:
                self._veh = v
                self.v_vin.setText(v.get("vin",""))
                self.v_serie.setText(v.get("serie",""))
                self.v_motor.setText(v.get("numero_motor",""))
                self.v_anio.setValue(int(v.get("anio_modelo", date.today().year) or date.today().year))
                self.v_asientos.setValue(int(v.get("asientos",5) or 5))
                self.v_ejes.setValue(int(v.get("ejes",2) or 2))
                self.v_cilindros.setValue(int(v.get("cilindros",4) or 4))
                self.v_cc.setValue(float(v.get("cilindraje_cc",0) or 0))
                self.v_tonelaje.setValue(float(v.get("tonelaje",0) or 0))
                # Seleccionar en combos
                for cb, clave in [
                    (self.v_tipo, "id_tipo"), (self.v_marca, "id_marca"),
                    (self.v_color, "id_color"), (self.v_uso, "id_uso"),
                ]:
                    for i in range(cb.count()):
                        if cb.itemData(i) == v.get(clave):
                            cb.setCurrentIndex(i)
                            break
                QMessageBox.information(self, "Vehículo encontrado",
                    f"✔ Chasis {chasis} ya registrado.\n"
                    f"Marca: {v.get('marca_nombre','')}  Línea: {v.get('linea_nombre','')}")
            else:
                self._veh = None
                QMessageBox.information(self, "No encontrado",
                    "Chasis no registrado. Complete los datos para crearlo.")
        except ServerError as e:
            QMessageBox.critical(self, "Error", str(e))

    # ─── Paso 3: Placa ───────────────────────────────────

    def _construir_paso3(self):
        w = QWidget()
        ly = QVBoxLayout(w)
        ly.setSpacing(8)
        ly.addWidget(titulo("Paso 3 – Placa", 14))
        ly.addWidget(separador())

        gb = QGroupBox("Datos de la Placa")
        fl = QFormLayout()
        self.pl_numero = input_line("Ej. P-123ABC")
        self.pl_fecha  = date_edit()
        fl.addRow("Número de Placa *",   self.pl_numero)
        fl.addRow("Fecha de asignación", self.pl_fecha)
        gb.setLayout(fl)
        ly.addWidget(gb)
        ly.addStretch()
        self._stack.addWidget(scroll_widget(w))

    # ─── Paso 4: Tarjeta ─────────────────────────────────

    def _construir_paso4(self):
        w = QWidget()
        ly = QVBoxLayout(w)
        ly.setSpacing(8)
        ly.addWidget(titulo("Paso 4 – Datos de la Tarjeta", 14))
        ly.addWidget(separador())

        gb = QGroupBox("Información de la Tarjeta de Circulación")
        fl = QFormLayout()
        self.t_numero = input_line("Número de tarjeta (único)")
        self.t_sat    = input_line("Código SAT")
        self.t_emision    = date_edit()
        venc = QDate.currentDate().addYears(1)
        self.t_vencimiento = date_edit(venc)
        fl.addRow("N.° Tarjeta *",       self.t_numero)
        fl.addRow("Código SAT *",        self.t_sat)
        fl.addRow("Fecha de Emisión",    self.t_emision)
        fl.addRow("Fecha Vencimiento",   self.t_vencimiento)
        gb.setLayout(fl)
        ly.addWidget(gb)

        self.lbl_resultado = QLabel("")
        self.lbl_resultado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_resultado.setStyleSheet("font-size:14px; font-weight:bold; color:#1B5E20;")
        ly.addWidget(self.lbl_resultado)
        ly.addStretch()
        self._stack.addWidget(scroll_widget(w))

    # ─── Navegación ──────────────────────────────────────

    def _ir_a(self, paso):
        self._paso = paso
        self._stack.setCurrentIndex(paso)
        pasos = ["Propietario", "Vehículo", "Placa", "Tarjeta"]
        self._indicador.setText("   ›   ".join(
            f"<b>{p}</b>" if i == paso else p for i, p in enumerate(pasos)
        ))
        self.btn_atras.setEnabled(paso > 0)
        self.btn_sig.setVisible(paso < 3)
        self.btn_crear.setVisible(paso == 3)
        if paso == 1 and not self._marcas:
            self._cargar_catalogos()

    def _atras(self):
        self._ir_a(self._paso - 1)

    def _siguiente(self):
        if not self._validar_paso(self._paso):
            return
        self._ir_a(self._paso + 1)

    def _validar_paso(self, paso):
        if paso == 0:
            if not self.inp_nit.text().strip():
                QMessageBox.warning(self, "Validación", "Ingrese el NIT del propietario.")
                return False
            if not self.p_pn.text().strip() or not self.p_pa.text().strip():
                QMessageBox.warning(self, "Validación",
                    "Complete al menos primer nombre y primer apellido.")
                return False
            if not self._prop and not self.p_cui.text().strip():
                QMessageBox.warning(self, "Validación",
                    "Ingrese el CUI (DPI) del propietario.")
                return False
        elif paso == 1:
            if not self.inp_chasis.text().strip():
                QMessageBox.warning(self, "Validación", "Ingrese el chasis.")
                return False
            if not self.v_motor.text().strip():
                QMessageBox.warning(self, "Validación", "Ingrese el número de motor.")
                return False
            if self.v_tipo.currentData() is None:
                QMessageBox.warning(self, "Validación", "Seleccione el tipo de vehículo.")
                return False
            if self.v_marca.currentData() is None:
                QMessageBox.warning(self, "Validación", "Seleccione la marca del vehículo.")
                return False
            if self.v_linea.currentData() is None:
                QMessageBox.warning(self, "Validación", "Seleccione la línea del vehículo.")
                return False
            if self.v_color.currentData() is None:
                QMessageBox.warning(self, "Validación", "Seleccione el color del vehículo.")
                return False
            if self.v_uso.currentData() is None:
                QMessageBox.warning(self, "Validación", "Seleccione el uso del vehículo.")
                return False
        elif paso == 2:
            if not self.pl_numero.text().strip():
                QMessageBox.warning(self, "Validación", "Ingrese el número de placa.")
                return False
        return True

    # ─── Crear Todo ──────────────────────────────────────

    def _crear_todo(self):
        if not self._validar_paso(2):
            return
        if not self.t_numero.text().strip() or not self.t_sat.text().strip():
            QMessageBox.warning(self, "Validación",
                "Complete el número de tarjeta y el código SAT.")
            return
        try:
            nit = self.inp_nit.text().strip()
            # Crear propietario si no existe
            if not self._prop:
                server.call("crear_propietario", {
                    "nit":              nit,
                    "cui":              self.p_cui.text().strip(),
                    "primer_nombre":    self.p_pn.text().strip(),
                    "segundo_nombre":   self.p_sn.text().strip(),
                    "primer_apellido":  self.p_pa.text().strip(),
                    "segundo_apellido": self.p_sa.text().strip(),
                })

            chasis = self.inp_chasis.text().strip()
            # Crear vehículo si no existe
            if not self._veh:
                server.call("crear_vehiculo", {
                    "chasis":       chasis,
                    "vin":          self.v_vin.text().strip(),
                    "serie":        self.v_serie.text().strip(),
                    "numero_motor": self.v_motor.text().strip(),
                    "anio_modelo":  self.v_anio.value(),
                    "asientos":     self.v_asientos.value(),
                    "ejes":         self.v_ejes.value(),
                    "cilindros":    self.v_cilindros.value(),
                    "cilindraje_cc":self.v_cc.value(),
                    "tonelaje":     self.v_tonelaje.value(),
                    "id_tipo":      self.v_tipo.currentData(),
                    "id_marca":     self.v_marca.currentData(),
                    "id_linea":     self.v_linea.currentData(),
                    "id_color":     self.v_color.currentData(),
                    "id_uso":       self.v_uso.currentData(),
                })

            numero_placa = self.pl_numero.text().strip()
            # Crear placa
            placa_existente = server.call("buscar_placa", {"numero_placa": numero_placa})
            if not placa_existente:
                server.call("crear_placa", {
                    "numero_placa":    numero_placa,
                    "chasis":          chasis,
                    "fecha_asignacion":self.pl_fecha.date().toString("yyyy-MM-dd"),
                })

            # Crear tarjeta
            resultado = server.call("crear_tarjeta", {
                "numero_tarjeta":   self.t_numero.text().strip(),
                "codigo_sat":       self.t_sat.text().strip(),
                "fecha_emision":    self.t_emision.date().toString("yyyy-MM-dd"),
                "fecha_vencimiento":self.t_vencimiento.date().toString("yyyy-MM-dd"),
                "nit_propietario":  nit,
                "chasis":           chasis,
                "numero_placa":     numero_placa,
            })

            cui = resultado.get("numero_cui","—")
            self.lbl_resultado.setText(
                f"✅ Tarjeta creada exitosamente\n"
                f"Código Único Identificador (CUI): {cui}"
            )
            QMessageBox.information(self, "¡Éxito!",
                f"Tarjeta de circulación creada.\nCUI generado: {cui}")

            self._resetear()

        except ServerError as e:
            QMessageBox.critical(self, "Error al crear tarjeta", str(e))

    def _resetear(self):
        """Limpia todos los campos del wizard y regresa al paso 1."""
        self._prop = None
        self._veh  = None

        # Paso 1 – Propietario
        self.inp_nit.clear()
        self.p_cui.clear()
        self.p_pn.clear()
        self.p_sn.clear()
        self.p_pa.clear()
        self.p_sa.clear()

        # Paso 2 – Vehículo
        self.inp_chasis.clear()
        self.v_vin.clear()
        self.v_serie.clear()
        self.v_motor.clear()
        self.v_anio.setValue(QDate.currentDate().year())
        self.v_tipo.setCurrentIndex(0)
        self.v_marca.setCurrentIndex(0)
        self.v_linea.setCurrentIndex(0)
        self.v_color.setCurrentIndex(0)
        self.v_uso.setCurrentIndex(0)
        self.v_asientos.setValue(0)
        self.v_ejes.setValue(0)
        self.v_cilindros.setValue(0)
        self.v_cc.setValue(0)
        self.v_tonelaje.setValue(0.0)

        # Paso 3 – Placa
        self.pl_numero.clear()
        self.pl_fecha.setDate(QDate.currentDate())

        # Paso 4 – Tarjeta
        self.t_numero.clear()
        self.t_sat.clear()
        self.t_emision.setDate(QDate.currentDate())
        self.t_vencimiento.setDate(QDate.currentDate().addYears(1))
        self.lbl_resultado.setText("")

        self._ir_a(0)


# ════════════════════════════════════════════════════════════
#  TAB 3 – Mantenimiento
# ════════════════════════════════════════════════════════════

class TabMantenimiento(QWidget):

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background:{GRIS_BG};")
        self._tarjeta = None
        self._colores = []

        main = QVBoxLayout(self)
        main.setContentsMargins(16, 16, 16, 16)
        main.setSpacing(10)

        # ── Búsqueda ──────────────────────────────────────
        barra = QFrame()
        barra.setStyleSheet(f"background:{BLANCO}; border-radius:8px; padding:6px;")
        b_ly = QHBoxLayout(barra)
        b_ly.addWidget(QLabel("Número de Tarjeta:"))
        self.inp_tarjeta = input_line("Ej. TC-2024-001")
        btn_b = btn("Buscar")
        btn_b.clicked.connect(self._buscar)
        b_ly.addWidget(self.inp_tarjeta, 1)
        b_ly.addWidget(btn_b)
        main.addWidget(barra)

        # ── Info de tarjeta actual ────────────────────────
        self.lbl_info = QLabel("Busca una tarjeta para comenzar el mantenimiento.")
        self.lbl_info.setStyleSheet(
            f"background:{BLANCO}; border-radius:8px; padding:12px;"
            f"color:{GRIS_T}; font-size:13px;"
        )
        main.addWidget(self.lbl_info)

        # ── Operaciones ───────────────────────────────────
        self.panel_ops = QWidget()
        self.panel_ops.setVisible(False)
        ops_ly = QVBoxLayout(self.panel_ops)
        ops_ly.setSpacing(8)

        ops_ly.addWidget(titulo("Selecciona la operación:", 13))

        # Cambio de dueño
        gb_dueno = QGroupBox("👤 Cambio de Dueño")
        d_ly = QFormLayout()
        self.inp_nuevo_nit = input_line("NIT del nuevo propietario")
        btn_d = btn("Verificar y Aplicar", ancho=180)
        btn_d.clicked.connect(self._cambio_dueno)
        d_ly.addRow("Nuevo NIT *", self.inp_nuevo_nit)
        d_ly.addRow("", btn_d)
        gb_dueno.setLayout(d_ly)
        ops_ly.addWidget(gb_dueno)

        # Cambio de motor
        gb_motor = QGroupBox("🔧 Cambio de Motor")
        m_ly = QFormLayout()
        self.inp_nuevo_motor = input_line("Nuevo número de motor")
        btn_m = btn("Aplicar Cambio de Motor", ancho=200)
        btn_m.clicked.connect(self._cambio_motor)
        m_ly.addRow("Nuevo N.° Motor *", self.inp_nuevo_motor)
        m_ly.addRow("", btn_m)
        gb_motor.setLayout(m_ly)
        ops_ly.addWidget(gb_motor)

        # Cambio de color
        gb_color = QGroupBox("🎨 Trámite de Cambio de Color")
        c_ly = QFormLayout()
        self.m_color = QComboBox()
        self.m_color.addItem("-- cargando --")
        btn_c = btn("Aplicar Cambio de Color", ancho=200)
        btn_c.clicked.connect(self._cambio_color)
        c_ly.addRow("Nuevo Color *", self.m_color)
        c_ly.addRow("", btn_c)
        gb_color.setLayout(c_ly)
        ops_ly.addWidget(gb_color)
        ops_ly.addStretch()

        main.addWidget(self.panel_ops, 1)
        self.inp_tarjeta.returnPressed.connect(self._buscar)

    def _buscar(self):
        num = self.inp_tarjeta.text().strip()
        if not num:
            return
        try:
            datos = server.call("consultar_tarjeta", {"campo": "numero_tarjeta", "valor": num})
            if not datos:
                QMessageBox.information(self, "No encontrada", "Tarjeta no encontrada.")
                self.panel_ops.setVisible(False)
                return
            t = datos[0]
            self._tarjeta = t
            nombre = " ".join(filter(None, [t.get("primer_nombre"), t.get("primer_apellido")]))
            self.lbl_info.setText(
                f"<b>Tarjeta:</b> {t.get('numero_tarjeta')}  "
                f"<b>Estado:</b> {t.get('tarjeta_estado')}  |  "
                f"<b>Propietario:</b> {nombre} ({t.get('nit_propietario')})  |  "
                f"<b>Placa:</b> {t.get('numero_placa')}  |  "
                f"<b>Chasis:</b> {t.get('chasis')}"
            )
            self.panel_ops.setVisible(True)
            # Cargar colores si es necesario
            if not self._colores:
                self._colores = server.call("listar_colores")
                self.m_color.clear()
                self.m_color.addItem("-- Seleccionar --", None)
                for c in self._colores:
                    self.m_color.addItem(c["descripcion"], c["id_color"])
        except ServerError as e:
            QMessageBox.critical(self, "Error", str(e))

    def _cambio_dueno(self):
        if not self._tarjeta:
            return
        nuevo_nit = self.inp_nuevo_nit.text().strip()
        if not nuevo_nit:
            QMessageBox.warning(self, "Validación", "Ingrese el NIT del nuevo propietario.")
            return
        try:
            prop = server.call("buscar_propietario", {"nit": nuevo_nit})
            if not prop:
                QMessageBox.warning(self, "NIT no registrado",
                    f"El NIT {nuevo_nit} no está registrado.\n"
                    "Registre el propietario en 'Nueva Tarjeta' primero.")
                return
            nombre = f"{prop.get('primer_nombre','')} {prop.get('primer_apellido','')}"
            resp = QMessageBox.question(self, "Confirmar",
                f"¿Cambiar propietario a:\n{nombre}  (NIT: {nuevo_nit})?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if resp == QMessageBox.StandardButton.Yes:
                server.call("cambio_dueno", {
                    "numero_tarjeta": self._tarjeta["numero_tarjeta"],
                    "nuevo_nit":      nuevo_nit,
                })
                QMessageBox.information(self, "¡Listo!", "Cambio de dueño aplicado.")
                self._buscar()
        except ServerError as e:
            QMessageBox.critical(self, "Error", str(e))

    def _cambio_motor(self):
        if not self._tarjeta:
            return
        nuevo_motor = self.inp_nuevo_motor.text().strip()
        if not nuevo_motor:
            QMessageBox.warning(self, "Validación", "Ingrese el nuevo número de motor.")
            return
        try:
            server.call("actualizar_motor", {
                "chasis":       self._tarjeta["chasis"],
                "nuevo_motor":  nuevo_motor,
            })
            QMessageBox.information(self, "¡Listo!", "Número de motor actualizado.")
        except ServerError as e:
            QMessageBox.critical(self, "Error", str(e))

    def _cambio_color(self):
        if not self._tarjeta:
            return
        id_color = self.m_color.currentData()
        if id_color is None:
            QMessageBox.warning(self, "Validación", "Seleccione un color.")
            return
        try:
            server.call("actualizar_color", {
                "chasis":   self._tarjeta["chasis"],
                "id_color": id_color,
            })
            QMessageBox.information(self, "¡Listo!", "Color actualizado en el vehículo.")
        except ServerError as e:
            QMessageBox.critical(self, "Error", str(e))


# ════════════════════════════════════════════════════════════
#  TAB 4 – Desactivar
# ════════════════════════════════════════════════════════════

class TabDesactivar(QWidget):

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background:{GRIS_BG};")
        self._tarjeta = None

        main = QVBoxLayout(self)
        main.setContentsMargins(16, 16, 16, 16)
        main.setSpacing(12)

        # Búsqueda
        barra = QFrame()
        barra.setStyleSheet(f"background:{BLANCO}; border-radius:8px; padding:6px;")
        b_ly = QHBoxLayout(barra)
        b_ly.addWidget(QLabel("Número de Tarjeta:"))
        self.inp_tarjeta = input_line("Buscar tarjeta a desactivar")
        btn_b = btn("Buscar")
        btn_b.clicked.connect(self._buscar)
        b_ly.addWidget(self.inp_tarjeta, 1)
        b_ly.addWidget(btn_b)
        main.addWidget(barra)

        # Info
        self.detalle = TarjetaInfoWidget()
        self.detalle_scroll = scroll_widget(self.detalle)
        self.detalle_scroll.setMaximumHeight(360)
        main.addWidget(self.detalle_scroll)

        # Panel confirmación
        self.panel_confirm = QWidget()
        self.panel_confirm.setVisible(False)
        c_ly = QVBoxLayout(self.panel_confirm)
        c_ly.setSpacing(8)

        aviso = QLabel("⚠️  Esta acción desactivará la tarjeta y su placa asociada. No es reversible desde la aplicación.")
        aviso.setWordWrap(True)
        aviso.setStyleSheet(f"color:{NARANJA}; font-weight:bold; font-size:13px;")
        c_ly.addWidget(aviso)

        c_ly.addWidget(QLabel("Motivo de desactivación:"))
        self.rb_impago     = QRadioButton("Impago / falta de pago")
        self.rb_vencimiento= QRadioButton("Vencimiento de vigencia")
        self.rb_impago.setChecked(True)
        self.bg = QButtonGroup()
        self.bg.addButton(self.rb_impago)
        self.bg.addButton(self.rb_vencimiento)
        c_ly.addWidget(self.rb_impago)
        c_ly.addWidget(self.rb_vencimiento)

        btn_desact = btn("🚫  Desactivar Tarjeta", ESTILO_BTN_ROJO)
        btn_desact.clicked.connect(self._desactivar)
        c_ly.addWidget(btn_desact, alignment=Qt.AlignmentFlag.AlignLeft)

        main.addWidget(self.panel_confirm)
        main.addStretch()
        self.inp_tarjeta.returnPressed.connect(self._buscar)

    def _buscar(self):
        num = self.inp_tarjeta.text().strip()
        if not num:
            return
        try:
            datos = server.call("consultar_tarjeta", {"campo": "numero_tarjeta", "valor": num})
            if not datos:
                QMessageBox.information(self, "No encontrada", "Tarjeta no encontrada.")
                self.panel_confirm.setVisible(False)
                self.detalle.limpiar()
                return
            self._tarjeta = datos[0]
            self.detalle.mostrar(self._tarjeta)
            estado = (self._tarjeta.get("tarjeta_estado") or "").upper()
            if "INACTIVA" in estado:
                QMessageBox.information(self, "Tarjeta ya inactiva",
                    f"Esta tarjeta ya está en estado: {estado}")
                self.panel_confirm.setVisible(False)
            else:
                self.panel_confirm.setVisible(True)
        except ServerError as e:
            QMessageBox.critical(self, "Error", str(e))

    def _desactivar(self):
        if not self._tarjeta:
            return
        razon = "impago" if self.rb_impago.isChecked() else "vencimiento"
        resp = QMessageBox.warning(self, "¿Confirmar desactivación?",
            f"¿Deseas desactivar la tarjeta\n"
            f"{self._tarjeta.get('numero_tarjeta')}  por  {razon.upper()}?\n\n"
            "Se marcará como INACTIVA junto con su placa.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if resp != QMessageBox.StandardButton.Yes:
            return
        try:
            server.call("desactivar_tarjeta", {
                "numero_tarjeta": self._tarjeta["numero_tarjeta"],
                "razon": razon,
            })
            QMessageBox.information(self, "Desactivada",
                "La tarjeta ha sido desactivada exitosamente.")
            self.panel_confirm.setVisible(False)
            self._buscar()   # refrescar vista
        except ServerError as e:
            QMessageBox.critical(self, "Error", str(e))


# ════════════════════════════════════════════════════════════
#  Ventana principal
# ════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Tarjetas de Circulación — Guatemala")
        self.setMinimumSize(1000, 680)
        self.setStyleSheet(f"QMainWindow {{ background:{GRIS_BG}; }}")

        # ── Header ────────────────────────────────────────
        header = QWidget()
        header.setStyleSheet(f"background:{AZUL};")
        header.setFixedHeight(56)
        h_ly = QHBoxLayout(header)
        h_ly.setContentsMargins(20, 0, 20, 0)
        titulo_app = QLabel("🇬🇹  Sistema de Tarjetas de Circulación Vehicular")
        titulo_app.setStyleSheet("color:white; font-size:16px; font-weight:bold;")
        self.lbl_conexion = QLabel("⚪ Sin conexión")
        self.lbl_conexion.setStyleSheet("color:#B3E5FC; font-size:12px;")
        h_ly.addWidget(titulo_app)
        h_ly.addStretch()
        h_ly.addWidget(self.lbl_conexion)

        # ── Tabs ──────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: {GRIS_BG};
            }}
            QTabBar::tab {{
                background: #CFD8DC;
                color: #37474F;
                padding: 10px 22px;
                font-size: 13px;
                border: none;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: {AZUL};
                color: white;
                font-weight: bold;
            }}
            QTabBar::tab:hover {{
                background: #B0BEC5;
            }}
        """)

        self.tab_consultar    = TabConsultar()
        self.tab_nueva        = TabNuevaTarjeta()
        self.tab_mant         = TabMantenimiento()
        self.tab_desact       = TabDesactivar()

        self.tabs.addTab(self.tab_consultar, "🔍  Consultar")
        self.tabs.addTab(self.tab_nueva,     "➕  Nueva Tarjeta")
        self.tabs.addTab(self.tab_mant,      "🔧  Mantenimiento")
        self.tabs.addTab(self.tab_desact,    "🚫  Desactivar")

        # ── Layout central ────────────────────────────────
        central = QWidget()
        cl = QVBoxLayout(central)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)
        cl.addWidget(header)
        cl.addWidget(self.tabs)
        self.setCentralWidget(central)

        # ── Status bar ────────────────────────────────────
        self.statusBar().setStyleSheet(f"background:{BLANCO}; color:{GRIS_T};")
        self.statusBar().showMessage("Iniciando…")

    def actualizar_estado_conexion(self, ok):
        if ok:
            self.lbl_conexion.setText(f"🟢 Conectado a {SERVER_HOST}:{SERVER_PORT}")
            self.lbl_conexion.setStyleSheet("color:#B9F6CA; font-size:12px;")
            self.statusBar().showMessage("Listo.")
        else:
            self.lbl_conexion.setText("🔴 Sin conexión con el servidor")
            self.lbl_conexion.setStyleSheet("color:#FF8A80; font-size:12px;")
            self.statusBar().showMessage("No se pudo conectar al servidor.")


# ════════════════════════════════════════════════════════════
#  Entry point
# ════════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(GRIS_BG))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXTO))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXTO))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(TEXTO))
    app.setPalette(palette)

    win = MainWindow()
    win.show()

    try:
        server.connect()
        win.actualizar_estado_conexion(True)
    except Exception as e:
        win.actualizar_estado_conexion(False)
        QMessageBox.critical(win, "Error de conexión",
            f"No se pudo conectar al servidor en {SERVER_HOST}:{SERVER_PORT}.\n\n"
            f"Asegúrate de que server.py esté corriendo.\n\nDetalle: {e}")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
