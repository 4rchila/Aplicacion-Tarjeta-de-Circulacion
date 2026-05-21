# ============================================================
#  database.py  –  Capa de acceso a datos (usada por el servidor)
# ============================================================

import psycopg2
import psycopg2.extras
import uuid
from datetime import date, datetime
from config import DB_CONFIG


# ─── Helpers ────────────────────────────────────────────────

def _conn():
    return psycopg2.connect(**DB_CONFIG)

def _rows(cur):
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]

def _row(cur):
    if not cur.description:
        return None
    cols = [d[0] for d in cur.description]
    r = cur.fetchone()
    return dict(zip(cols, r)) if r else None

def _serialize(obj):
    """Convierte tipos no-JSON a string."""
    if isinstance(obj, (date, datetime)):
        return str(obj)
    return obj

def _clean(data):
    """Limpia recursivamente un dict/list para serialización JSON."""
    if isinstance(data, list):
        return [_clean(i) for i in data]
    if isinstance(data, dict):
        return {k: _serialize(v) for k, v in data.items()}
    return data


# ─── Catálogos ──────────────────────────────────────────────

def listar_marcas():
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT id_marca, nombre FROM marca ORDER BY nombre")
            return _clean(_rows(cur))

def listar_lineas(id_marca=None):
    with _conn() as c:
        with c.cursor() as cur:
            if id_marca:
                cur.execute(
                    "SELECT id_linea, nombre, id_marca FROM linea WHERE id_marca=%s ORDER BY nombre",
                    (id_marca,)
                )
            else:
                cur.execute("SELECT id_linea, nombre, id_marca FROM linea ORDER BY nombre")
            return _clean(_rows(cur))

def listar_colores():
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT id_color, descripcion FROM color ORDER BY descripcion")
            return _clean(_rows(cur))

def listar_tipos():
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT id_tipo, descripcion FROM tipo_vehiculo ORDER BY descripcion")
            return _clean(_rows(cur))

def listar_usos():
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT id_uso, descripcion FROM uso ORDER BY descripcion")
            return _clean(_rows(cur))


# ─── Propietario ────────────────────────────────────────────

def buscar_propietario(nit):
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute(
                "SELECT nit, cui, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido "
                "FROM propietario WHERE nit=%s",
                (nit,)
            )
            return _clean(_row(cur))

def crear_propietario(d):
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute(
                "INSERT INTO propietario (nit, cui, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido) "
                "VALUES (%s,%s,%s,%s,%s,%s)",
                (d['nit'], d['cui'], d['primer_nombre'], d.get('segundo_nombre', ''),
                 d['primer_apellido'], d.get('segundo_apellido', ''))
            )
        c.commit()


# ─── Vehículo ───────────────────────────────────────────────

def buscar_vehiculo(chasis):
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute("""
                SELECT v.chasis, v.vin, v.serie, v.numero_motor, v.anio_modelo,
                       v.asientos, v.ejes, v.cilindros, v.cilindraje_cc, v.tonelaje,
                       v.id_tipo, v.id_marca, v.id_linea, v.id_color, v.id_uso,
                       m.nombre  AS marca_nombre,
                       l.nombre  AS linea_nombre,
                       col.descripcion AS color_nombre,
                       t.descripcion AS tipo_nombre,
                       u.descripcion AS uso_nombre
                FROM vehiculo v
                JOIN marca        m ON v.id_marca = m.id_marca
                JOIN linea        l ON v.id_linea = l.id_linea
                JOIN color        col ON v.id_color = col.id_color
                JOIN tipo_vehiculo t ON v.id_tipo = t.id_tipo
                JOIN uso          u ON v.id_uso  = u.id_uso
                WHERE v.chasis = %s
            """, (chasis,))
            return _clean(_row(cur))

def crear_vehiculo(d):
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute("""
                INSERT INTO vehiculo
                    (chasis, vin, serie, numero_motor, anio_modelo, asientos, ejes,
                     cilindros, cilindraje_cc, tonelaje, id_tipo, id_marca, id_linea, id_color, id_uso)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                d['chasis'], d['vin'], d['serie'], d['numero_motor'],
                d['anio_modelo'], d['asientos'], d['ejes'], d['cilindros'],
                d['cilindraje_cc'], d['tonelaje'],
                d['id_tipo'], d['id_marca'], d['id_linea'], d['id_color'], d['id_uso']
            ))
        c.commit()

def actualizar_motor(chasis, nuevo_motor):
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute("UPDATE vehiculo SET numero_motor=%s WHERE chasis=%s", (nuevo_motor, chasis))
        c.commit()

def actualizar_color(chasis, id_color):
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute("UPDATE vehiculo SET id_color=%s WHERE chasis=%s", (id_color, chasis))
        c.commit()


# ─── Placa ──────────────────────────────────────────────────

def buscar_placa(numero_placa):
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute(
                "SELECT numero_placa, chasis, fecha_asignacion, estado FROM placa WHERE numero_placa=%s",
                (numero_placa,)
            )
            return _clean(_row(cur))

def crear_placa(numero_placa, chasis, fecha_asignacion):
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute(
                "INSERT INTO placa (numero_placa, chasis, fecha_asignacion, estado) VALUES (%s,%s,%s,'ACTIVA')",
                (numero_placa, chasis, fecha_asignacion)
            )
        c.commit()


# ─── Tarjeta de Circulación ─────────────────────────────────

def consultar_tarjeta(campo, valor):
    """
    campo: 'numero_tarjeta' | 'numero_placa' | 'chasis' | 'nit'
    Devuelve lista (puede ser >1 si se busca por NIT).
    """
    condiciones = {
        'numero_tarjeta': 'tc.numero_tarjeta = %s',
        'numero_placa':   'tc.numero_placa   = %s',
        'chasis':         'tc.chasis         = %s',
        'nit':            'tc.nit_propietario = %s',
    }
    cond = condiciones.get(campo, 'tc.numero_tarjeta = %s')

    with _conn() as c:
        with c.cursor() as cur:
            cur.execute(f"""
                SELECT
                    tc.numero_tarjeta,  tc.codigo_sat,
                    tc.fecha_emision,   tc.fecha_vencimiento,
                    tc.estado           AS tarjeta_estado,
                    tc.nit_propietario, tc.chasis,
                    tc.numero_placa,

                    p.cui,              p.primer_nombre,
                    p.segundo_nombre,   p.primer_apellido,
                    p.segundo_apellido,

                    v.vin,              v.serie,
                    v.numero_motor,     v.anio_modelo,
                    v.asientos,         v.ejes,
                    v.cilindros,        v.cilindraje_cc,
                    v.tonelaje,

                    m.nombre            AS marca,
                    l.nombre            AS linea,
                    col.descripcion     AS color,
                    t.descripcion       AS tipo_vehiculo,
                    u.descripcion       AS uso,

                    pl.fecha_asignacion AS placa_fecha,
                    pl.estado           AS placa_estado,

                    cui.numero_cui,
                    cui.codigo_qr,
                    cui.fecha_generacion AS cui_fecha
                FROM tarjeta_circulacion tc
                JOIN propietario  p   ON tc.nit_propietario = p.nit
                JOIN vehiculo     v   ON tc.chasis          = v.chasis
                JOIN marca        m   ON v.id_marca         = m.id_marca
                JOIN linea        l   ON v.id_linea         = l.id_linea
                JOIN color        col ON v.id_color         = col.id_color
                JOIN tipo_vehiculo t  ON v.id_tipo          = t.id_tipo
                JOIN uso          u   ON v.id_uso           = u.id_uso
                JOIN placa        pl  ON tc.numero_placa    = pl.numero_placa
                LEFT JOIN codigo_unico_identificador cui
                                      ON tc.numero_tarjeta  = cui.numero_tarjeta
                WHERE {cond}
                ORDER BY tc.fecha_emision DESC
            """, (valor,))
            return _clean(_rows(cur))

def crear_tarjeta(d):
    """
    d: numero_tarjeta, codigo_sat, fecha_emision, fecha_vencimiento,
       nit_propietario, chasis, numero_placa
    Retorna el numero_cui generado.
    """
    numero_cui = str(uuid.uuid4())[:8].upper()
    hoy        = date.today()
    hora_ahora = datetime.now().time()
    codigo_qr  = f"TC-{d['numero_tarjeta']}-{numero_cui}"

    with _conn() as c:
        with c.cursor() as cur:
            cur.execute("""
                INSERT INTO tarjeta_circulacion
                    (numero_tarjeta, codigo_sat, fecha_emision, fecha_vencimiento,
                     estado, nit_propietario, chasis, numero_placa)
                VALUES (%s,%s,%s,%s,'ACTIVA',%s,%s,%s)
            """, (
                d['numero_tarjeta'], d['codigo_sat'],
                d['fecha_emision'], d['fecha_vencimiento'],
                d['nit_propietario'], d['chasis'], d['numero_placa']
            ))
            cur.execute("""
                INSERT INTO codigo_unico_identificador
                    (numero_cui, fecha_generacion, hora_generacion,
                     fecha_registro, codigo_qr, numero_tarjeta)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (numero_cui, hoy, hora_ahora, hoy, codigo_qr, d['numero_tarjeta']))
        c.commit()
    return numero_cui

def cambio_dueno(numero_tarjeta, nuevo_nit):
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute(
                "UPDATE tarjeta_circulacion SET nit_propietario=%s WHERE numero_tarjeta=%s",
                (nuevo_nit, numero_tarjeta)
            )
        c.commit()

def desactivar_tarjeta(numero_tarjeta, razon):
    """razon: 'impago' | 'vencimiento'"""
    estado = 'INACTIVA_IMPAGO' if razon == 'impago' else 'INACTIVA_VENCIMIENTO'
    with _conn() as c:
        with c.cursor() as cur:
            cur.execute(
                "UPDATE tarjeta_circulacion SET estado=%s WHERE numero_tarjeta=%s",
                (estado, numero_tarjeta)
            )
            cur.execute("""
                UPDATE placa SET estado='INACTIVA'
                WHERE numero_placa = (
                    SELECT numero_placa FROM tarjeta_circulacion WHERE numero_tarjeta=%s
                )
            """, (numero_tarjeta,))
        c.commit()
