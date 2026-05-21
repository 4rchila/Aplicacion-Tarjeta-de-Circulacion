# Sistema de Tarjetas de Circulación Vehicular
## Universidad Rafael Landívar — Bases de Datos I

---

## Estructura de archivos

```
circulacion/
├── config.py        ← Configuración (BD + servidor)
├── database.py      ← Operaciones SQL (solo lo usa el servidor)
├── server.py        ← Servidor TCP (ejecutar primero)
├── client.py        ← Interfaz PyQt6 (ejecutar después)
└── requirements.txt
```

---

## Instalación de dependencias

```bash
pip install -r requirements.txt
```

---

## Configuración

Abre `config.py` y ajusta:

```python
DB_CONFIG = {
    "database": "nombre_de_tu_bd",  # tu base de datos
    "user":     "postgres",          # tu usuario
    "password": "tu_contraseña",
}
```

---

## Ejecución

### 1. Iniciar el servidor (terminal 1)
```bash
python server.py
```
Verás:
```
[*] Servidor de Tarjetas de Circulación
[*] Escuchando en 127.0.0.1:9999
```

### 2. Iniciar el cliente (terminal 2)
```bash
python client.py
```

---

## Funcionalidades

| Pestaña | Función |
|---------|---------|
| 🔍 Consultar | Buscar tarjetas por número, placa, chasis o NIT |
| ➕ Nueva Tarjeta | Wizard de 4 pasos: propietario → vehículo → placa → tarjeta |
| 🔧 Mantenimiento | Cambio de dueño, motor o color |
| 🚫 Desactivar | Desactivar por impago o vencimiento |

---

## Arquitectura

```
Cliente (PyQt6)  ←──TCP/JSON──→  Servidor (Python sockets)  ←──→  PostgreSQL
   client.py                          server.py                   database.py
```

El protocolo usa cabecera de 4 bytes (tamaño del mensaje) + JSON UTF-8.
