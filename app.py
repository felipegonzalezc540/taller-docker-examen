
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "clave-taller-docker"

DB_PATH = os.environ.get("DB_PATH", "productos.db")


def conectar():
    carpeta = os.path.dirname(DB_PATH)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)

    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_tabla():
    with conectar() as conexion:
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                categoria TEXT NOT NULL,
                precio REAL NOT NULL
            )
        """)


@app.route("/", methods=["GET", "POST"])
def inicio():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        categoria = request.form.get("categoria", "").strip()

        try:
            precio = float(request.form.get("precio", ""))
            if precio < 0:
                raise ValueError
        except ValueError:
            flash("Ingresa un precio válido.", "error")
            return redirect(url_for("inicio"))

        if not nombre or not categoria:
            flash("Completa todos los campos.", "error")
            return redirect(url_for("inicio"))

        with conectar() as conexion:
            conexion.execute(
                "INSERT INTO productos (nombre, categoria, precio) VALUES (?, ?, ?)",
                (nombre, categoria, precio)
            )

        flash("Producto guardado correctamente.", "success")
        return redirect(url_for("inicio"))

    with conectar() as conexion:
        productos = conexion.execute(
            "SELECT * FROM productos ORDER BY id DESC"
        ).fetchall()

    return render_template("index.html", productos=productos)


crear_tabla()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
