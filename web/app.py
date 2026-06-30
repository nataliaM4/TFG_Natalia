"""
app.py

Servidor Flask para la demo del TFG de Natalia.

Rutas de página:
    GET  /                          -> index.html (pantalla principal)
    GET  /gallery                   -> gallery.html (listado de 251 casos de test)
    GET  /preview/<int:case_id>     -> preview.html (vista previa de un caso)
    GET  /upload                    -> upload.html (subir 4 imágenes propias)

Rutas de API:
    GET  /api/random_case           -> caso de test aleatorio (imágenes en base64)
    GET  /api/case/<int:case_id>    -> caso de test concreto (imágenes en base64)
    GET  /api/gallery_list          -> lista de ids de los 251 casos (para la galería)
    GET  /api/thumbnail/<id>        -> imagen FLAIR en crudo (para la galería)
    POST /api/predict                -> {"case_id": N}  ->  máscara predicha + Dice
    POST /api/predict_upload         -> 4 imágenes subidas -> máscara predicha (sin Dice)
"""

import os
import io
import random
import base64
import logging

from flask import Flask, render_template, jsonify, request, Response
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model as keras_load_model

# Silencia el log automático de cada petición HTTP (p. ej. los 251 GET
# que genera la galería al cargar las miniaturas). Tus propios print()
# de carga del modelo/datos se siguen mostrando con normalidad.
logging.getLogger("werkzeug").setLevel(logging.ERROR)

# ---------------------------------------------------------------------------
# Configuración de rutas de archivos
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "modelo_final.keras")
X_PATH = os.path.join(BASE_DIR, "data", "X_demo.npy")
Y_PATH = os.path.join(BASE_DIR, "data", "y_demo.npy")

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Carga del modelo y de los arrays de test (una sola vez, al arrancar)
# ---------------------------------------------------------------------------
print("Cargando modelo...")
# compile=False: para predecir no hace falta el optimizador ni las métricas
# personalizadas (como dice_metric) con las que se compiló durante el
# entrenamiento. Si en el futuro necesitas volver a entrenar este modelo,
# tendrías que compilarlo de nuevo con esas métricas.
model = keras_load_model(MODEL_PATH, compile=False)
print("Modelo cargado correctamente.")

print("Cargando casos de test...")
X_test = np.load(X_PATH)
Y_test = np.load(Y_PATH)
print(f"{len(X_test)} casos cargados.")


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------
def array_to_png_bytes(array_2d: np.ndarray) -> bytes:
    """Igual que array_to_base64 pero devuelve los bytes PNG en crudo,
    para poder servirlos directamente como imagen (no como JSON)."""
    arr = array_2d.astype(np.float32)
    arr = arr - arr.min()
    if arr.max() > 0:
        arr = arr / arr.max()
    arr = (arr * 255).astype(np.uint8)

    img = Image.fromarray(arr)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def array_to_base64(array_2d: np.ndarray) -> str:
    """Reescala un canal (valores Z-score, con negativos) a 0-255 y lo
    devuelve como PNG en base64, listo para usar en un <img src=...>."""
    arr = array_2d.astype(np.float32)
    arr = arr - arr.min()
    if arr.max() > 0:
        arr = arr / arr.max()
    arr = (arr * 255).astype(np.uint8)

    img = Image.fromarray(arr)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode()
    return "data:image/png;base64," + encoded


def mask_to_base64(mask_2d: np.ndarray) -> str:
    """Convierte una máscara (0-1) en una imagen PNG binaria (0/255) en base64."""
    binary = (mask_2d > 0.5).astype(np.uint8) * 255
    img = Image.fromarray(binary)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode()
    return "data:image/png;base64," + encoded


def get_case(case_id: int) -> dict:
    """Devuelve las 4 secuencias y la máscara real de un caso, en base64."""
    x = X_test[case_id]
    y = Y_test[case_id]
    return {
        "case_id": case_id,
        "flair": array_to_base64(x[:, :, 0]),
        "t1": array_to_base64(x[:, :, 1]),
        "t1ce": array_to_base64(x[:, :, 2]),
        "t2": array_to_base64(x[:, :, 3]),
        "mask_real": mask_to_base64(y[:, :, 0]),
    }


# ---------------------------------------------------------------------------
# Rutas de página
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/gallery")
def gallery():
    return render_template("gallery.html")


@app.route("/preview/<int:case_id>")
def preview(case_id):
    if case_id < 0 or case_id >= len(X_test):
        return "Caso inexistente", 404
    return render_template("preview.html", case_id=case_id)


@app.route("/upload")
def upload_page():
    return render_template("upload.html")


# ---------------------------------------------------------------------------
# Rutas de API
# ---------------------------------------------------------------------------
@app.route("/api/random_case")
def random_case():
    idx = random.randint(0, len(X_test) - 1)
    return jsonify(get_case(idx))


@app.route("/api/case/<int:case_id>")
def case(case_id):
    if case_id < 0 or case_id >= len(X_test):
        return jsonify({"error": "Caso inexistente"}), 404
    return jsonify(get_case(case_id))


@app.route("/api/thumbnail/<int:case_id>")
def thumbnail(case_id):
    """Devuelve la imagen FLAIR de un caso como PNG real (no JSON),
    para usarla directamente en <img src="/api/thumbnail/ID">."""
    if case_id < 0 or case_id >= len(X_test):
        return "Caso inexistente", 404
    flair = X_test[case_id][:, :, 0]
    png_bytes = array_to_png_bytes(flair)
    return Response(png_bytes, mimetype="image/png")


@app.route("/api/gallery_list")
def gallery_list():
    data = [{"id": i, "title": f"Caso {i + 1}"} for i in range(len(X_test))]
    return jsonify(data)


@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json()
    case_id = data.get("case_id")

    if case_id is None or case_id < 0 or case_id >= len(X_test):
        return jsonify({"error": "case_id inválido"}), 400

    x = np.expand_dims(X_test[case_id], axis=0)   # (1, 240, 240, 4)
    pred = model.predict(x, verbose=0)[0]          # (240, 240, 1)

    real = Y_test[case_id]                         # (240, 240, 1)
    pred_bin = (pred > 0.5).astype(np.float32)
    intersection = np.sum(pred_bin * real)
    dice = (2 * intersection) / (np.sum(pred_bin) + np.sum(real) + 1e-8)

    return jsonify({
        "mask_pred": mask_to_base64(pred[:, :, 0]),
        "dice": round(float(dice), 4),
    })


# Orden de canales con el que se entrenó el modelo:
# np.stack([flair, t1, t1ce, t2], axis=-1)
UPLOAD_CHANNELS = ["flair", "t1", "t1ce", "t2"]
UPLOAD_LABELS = {"flair": "FLAIR", "t1": "T1", "t1ce": "T1ce", "t2": "T2"}
TARGET_SIZE = (240, 240)  # tamaño con el que se entrenó el modelo


@app.route("/api/predict_upload", methods=["POST"])
def predict_upload():
    """
    Recibe exactamente 4 imágenes subidas manualmente (flair, t1, t1ce, t2),
    cada una de 240x240 píxeles, y devuelve la máscara predicha.
    No hay máscara real disponible (no es un caso del dataset), así que
    tampoco se calcula el coeficiente Dice.
    """
    # 1) Comprobar que llegan las 4 claves esperadas, con un archivo real dentro
    faltantes = [
        UPLOAD_LABELS[k] for k in UPLOAD_CHANNELS
        if k not in request.files or request.files[k].filename == ""
    ]
    if faltantes:
        return jsonify({
            "error": "Faltan imágenes por subir: " + ", ".join(faltantes) +
                     ". Debes subir exactamente las 4 secuencias."
        }), 400

    # 2) Comprobar que cada archivo es una imagen válida y mide 240x240
    canales = {}
    for key in UPLOAD_CHANNELS:
        file = request.files[key]
        try:
            img = Image.open(file.stream).convert("L")
        except Exception:
            return jsonify({
                "error": f"El archivo subido como {UPLOAD_LABELS[key]} no es una imagen válida."
            }), 400

        if img.size != TARGET_SIZE:
            ancho, alto = img.size
            return jsonify({
                "error": (
                    f"La imagen de {UPLOAD_LABELS[key]} mide {ancho}x{alto} píxeles. "
                    f"El modelo necesita imágenes de exactamente 240x240 píxeles, "
                    f"ya que es el tamaño con el que fue entrenado."
                )
            }), 400

        canales[key] = np.array(img, dtype=np.float32)

    # 3) Apilar y normalizar igual que en el notebook (Z-score sobre las 4
    #    secuencias juntas, no canal a canal por separado)
    stacked = np.stack([canales[k] for k in UPLOAD_CHANNELS], axis=-1)  # (240,240,4)
    mean = stacked.mean()
    std = stacked.std()
    if std == 0:
        std = 1.0
    normalized = (stacked - mean) / std
    x = np.expand_dims(normalized, axis=0).astype(np.float32)  # (1,240,240,4)

    # 4) Predecir
    pred = model.predict(x, verbose=0)[0]  # (240, 240, 1)

    return jsonify({"mask_pred": mask_to_base64(pred[:, :, 0])})


if __name__ == "__main__":
    app.run(debug=True, port=5000)