# ============================================================
#  server.py  –  Servidor TCP  (ejecutar primero)
#  Uso: python server.py
# ============================================================

import socket
import threading
import json
import struct
import sys
import database as db
from config import SERVER_HOST, SERVER_PORT


# ─── Protocolo: cabecera de 4 bytes (big-endian) + JSON UTF-8 ───

def _send(sock, data: dict):
    payload = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
    sock.sendall(struct.pack(">I", len(payload)) + payload)

def _recv(sock):
    raw = _recvall(sock, 4)
    if not raw:
        return None
    length = struct.unpack(">I", raw)[0]
    data = _recvall(sock, length)
    if not data:
        return None
    return json.loads(data.decode("utf-8"))

def _recvall(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


# ─── Despacho de acciones ───────────────────────────────────

def _dispatch(action: str, params: dict) -> dict:
    try:
        match action:
            # Catálogos
            case "listar_marcas":
                return {"success": True, "data": db.listar_marcas()}
            case "listar_lineas":
                return {"success": True, "data": db.listar_lineas(params.get("id_marca"))}
            case "listar_colores":
                return {"success": True, "data": db.listar_colores()}
            case "listar_tipos":
                return {"success": True, "data": db.listar_tipos()}
            case "listar_usos":
                return {"success": True, "data": db.listar_usos()}

            # Propietario
            case "buscar_propietario":
                return {"success": True, "data": db.buscar_propietario(params["nit"])}
            case "crear_propietario":
                db.crear_propietario(params)
                return {"success": True, "data": "Propietario creado"}

            # Vehículo
            case "buscar_vehiculo":
                return {"success": True, "data": db.buscar_vehiculo(params["chasis"])}
            case "crear_vehiculo":
                db.crear_vehiculo(params)
                return {"success": True, "data": "Vehículo creado"}
            case "actualizar_motor":
                db.actualizar_motor(params["chasis"], params["nuevo_motor"])
                return {"success": True, "data": "Motor actualizado"}
            case "actualizar_color":
                db.actualizar_color(params["chasis"], params["id_color"])
                return {"success": True, "data": "Color actualizado"}

            # Placa
            case "buscar_placa":
                return {"success": True, "data": db.buscar_placa(params["numero_placa"])}
            case "crear_placa":
                db.crear_placa(params["numero_placa"], params["chasis"], params["fecha_asignacion"])
                return {"success": True, "data": "Placa creada"}

            # Tarjeta
            case "consultar_tarjeta":
                rows = db.consultar_tarjeta(params["campo"], params["valor"])
                return {"success": True, "data": rows}
            case "crear_tarjeta":
                cui = db.crear_tarjeta(params)
                return {"success": True, "data": {"numero_cui": cui}}
            case "cambio_dueno":
                db.cambio_dueno(params["numero_tarjeta"], params["nuevo_nit"])
                return {"success": True, "data": "Cambio de dueño realizado"}
            case "desactivar_tarjeta":
                db.desactivar_tarjeta(params["numero_tarjeta"], params["razon"])
                return {"success": True, "data": "Tarjeta desactivada"}

            case _:
                return {"success": False, "error": f"Acción desconocida: {action}"}

    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ─── Manejo de cliente ──────────────────────────────────────

def _handle_client(conn: socket.socket, addr):
    print(f"  [+] Conectado: {addr}")
    try:
        while True:
            request = _recv(conn)
            if request is None:
                break
            action = request.get("action", "")
            params = request.get("params", {})
            print(f"  --> {addr}  acción: {action}")
            response = _dispatch(action, params)
            _send(conn, response)
    except Exception as exc:
        print(f"  [!] Error con {addr}: {exc}")
    finally:
        conn.close()
        print(f"  [-] Desconectado: {addr}")


# ─── Entry point ────────────────────────────────────────────

def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((SERVER_HOST, SERVER_PORT))
    srv.listen(10)
    print(f"[*] Servidor de Tarjetas de Circulación")
    print(f"[*] Escuchando en {SERVER_HOST}:{SERVER_PORT}")
    print(f"[*] Ctrl+C para detener\n")

    try:
        while True:
            conn, addr = srv.accept()
            t = threading.Thread(target=_handle_client, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[*] Servidor detenido.")
    finally:
        srv.close()


if __name__ == "__main__":
    main()
