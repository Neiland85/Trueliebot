from flask import Flask, jsonify, request

from auth import (admin_required, create_auth_routes, initialize_auth,
                  token_required)
from db import get_db_connection

app = Flask(__name__)

# Inicializar autenticación
initialize_auth(app)
create_auth_routes(app)


@app.route("/api/feedback", methods=["POST"])
@token_required
def registrar_feedback(user_data):
    """Registra feedback de usuario sobre un análisis."""
    if not request.is_json:
        return jsonify({"error": "Se esperaba formato JSON"}), 400

    data = request.get_json()

    # Validar datos requeridos
    required_fields = ["analisis_id", "tipo"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Campo requerido: {field}"}), 400

    # Usar el ID de usuario del token si no se proporciona
    if "usuario_id" not in data:
        data["usuario_id"] = user_data.get("user_id")

    # Validar tipo de feedback
    if data["tipo"] not in ["positivo", "negativo", "sugerencia"]:
        return jsonify({"error": "Tipo de feedback inválido"}), 400

    # Conectar a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO feedback (analisis_id, usuario_id, tipo, comentario, fecha_creacion)
            VALUES (?, ?, ?, ?, datetime('now'))
        """,
            (
                data["analisis_id"],
                data["usuario_id"],
                data["tipo"],
                data.get("comentario", ""),
            ),
        )

        feedback_id = cursor.lastrowid

        # Registrar en log
        cursor.execute(
            """
            INSERT INTO logs (accion, tabla, registro_id, usuario_id, detalles, fecha)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """,
            (
                "crear",
                "feedback",
                feedback_id,
                data["usuario_id"],
                f"Feedback {data['tipo']} para análisis {data['analisis_id']}",
            ),
        )

        conn.commit()

        return (
            jsonify(
                {
                    "message": "Feedback registrado correctamente",
                    "feedback_id": feedback_id,
                }
            ),
            201,
        )

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route("/api/feedback/<int:analisis_id>", methods=["GET"])
@token_required
def obtener_feedback(user_data, analisis_id):
    """Consulta feedback asociado a un análisis."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT f.id, f.analisis_id, f.usuario_id, f.tipo, f.comentario, f.fecha_creacion
            FROM feedback f
            WHERE f.analisis_id = ?
        """,
            (analisis_id,),
        )

        feedback_items = cursor.fetchall()

        result = []
        for item in feedback_items:
            result.append(
                {
                    "id": item[0],
                    "analisis_id": item[1],
                    "usuario_id": item[2],
                    "tipo": item[3],
                    "comentario": item[4],
                    "fecha_creacion": item[5],
                }
            )

        return jsonify({"feedback": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route("/api/patrones", methods=["POST"])
@token_required
def registrar_patron(user_data):
    """Registra un nuevo patrón de manipulación."""
    if not request.is_json:
        return jsonify({"error": "Se esperaba formato JSON"}), 400

    data = request.get_json()

    # Validar datos requeridos
    required_fields = ["descripcion", "expresion_regular"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Campo requerido: {field}"}), 400

    # Usar el ID de usuario del token si no se proporciona
    if "creado_por" not in data:
        data["creado_por"] = user_data.get("user_id")

    # Si el patrón se está validando, verificar que sea admin
    if data.get("validado", False) and user_data.get("role") != "admin":
        return (
            jsonify(
                {
                    "message": "Solo administradores pueden validar patrones",
                    "error": "Forbidden",
                }
            ),
            403,
        )

    # Conectar a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO patrones (descripcion, expresion_regular, creado_por, validado, fecha_creacion)
            VALUES (?, ?, ?, ?, datetime('now'))
        """,
            (
                data["descripcion"],
                data["expresion_regular"],
                data["creado_por"],
                data.get("validado", False),
            ),
        )

        patron_id = cursor.lastrowid

        # Registrar en log
        cursor.execute(
            """
            INSERT INTO logs (accion, tabla, registro_id, usuario_id, detalles, fecha)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """,
            (
                "crear",
                "patrones",
                patron_id,
                data["creado_por"],
                f"Patrón creado: {data['descripcion'][:30]}...",
            ),
        )

        conn.commit()

        return (
            jsonify(
                {"message": "Patrón registrado correctamente", "patron_id": patron_id}
            ),
            201,
        )

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route("/api/patrones", methods=["GET"])
@token_required
def obtener_patrones(user_data):
    """Lista todos los patrones registrados."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Administradores ven todos los patrones, usuarios solo los validados
        if user_data.get("role") == "admin":
            cursor.execute(
                """
                SELECT p.id, p.descripcion, p.expresion_regular, p.creado_por, p.validado, p.fecha_creacion
                FROM patrones p
                ORDER BY p.fecha_creacion DESC
            """
            )
        else:
            cursor.execute(
                """
                SELECT p.id, p.descripcion, p.expresion_regular, p.creado_por, p.validado, p.fecha_creacion
                FROM patrones p
                WHERE p.validado = 1
                ORDER BY p.fecha_creacion DESC
            """
            )

        patrones = cursor.fetchall()

        result = []
        for p in patrones:
            result.append(
                {
                    "id": p[0],
                    "descripcion": p[1],
                    "expresion_regular": p[2],
                    "creado_por": p[3],
                    "validado": bool(p[4]),
                    "fecha_creacion": p[5],
                }
            )

        return jsonify({"patrones": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route("/api/estadisticas", methods=["GET"])
@admin_required
def obtener_estadisticas(user_data):
    """Devuelve estadísticas básicas de uso, feedback y patrones validados."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Estadísticas de conversaciones
        cursor.execute("SELECT COUNT(*) FROM conversaciones")
        total_conversaciones = cursor.fetchone()[0]

        # Estadísticas de feedback
        cursor.execute("SELECT COUNT(*), tipo FROM feedback GROUP BY tipo")
        feedback_stats = cursor.fetchall()

        # Patrones validados vs no validados
        cursor.execute(
            """
            SELECT 
                SUM(CASE WHEN validado = 1 THEN 1 ELSE 0 END) as validados,
                SUM(CASE WHEN validado = 0 THEN 1 ELSE 0 END) as pendientes
            FROM patrones
        """
        )
        patrones_stats = cursor.fetchone()

        # Análisis por día (últimos 7 días)
        cursor.execute(
            """
            SELECT 
                date(fecha_creacion) as fecha, 
                COUNT(*) as total
            FROM analisis
            WHERE fecha_creacion >= date('now', '-7 days')
            GROUP BY date(fecha_creacion)
            ORDER BY fecha DESC
        """
        )
        analisis_por_dia = cursor.fetchall()

        stats = {
            "conversaciones": {"total": total_conversaciones},
            "feedback": {},
            "patrones": {
                "validados": patrones_stats[0] if patrones_stats[0] else 0,
                "pendientes": patrones_stats[1] if patrones_stats[1] else 0,
            },
            "analisis_ultimos_7_dias": [],
        }

        for fb in feedback_stats:
            stats["feedback"][fb[1]] = fb[0]

        for a in analisis_por_dia:
            stats["analisis_ultimos_7_dias"].append({"fecha": a[0], "total": a[1]})

        return jsonify(stats)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
