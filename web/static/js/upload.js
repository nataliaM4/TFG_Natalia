// =========================================================
// CONFIGURACIÓN
// =========================================================
const SLOTS = ["flair", "t1", "t1ce", "t2"];
const REQUIRED_SIZE = 240;

// Estado de validez de cada recuadro: true solo si tiene un archivo
// de imagen válido y mide exactamente 240x240 píxeles.
const validity = { flair: false, t1: false, t1ce: false, t2: false };

// Guardamos el File de cada slot para poder enviarlo al servidor.
const files = { flair: null, t1: null, t1ce: null, t2: null };

const generateBtn = document.getElementById("btn-upload-generate");

// =========================================================
// VALIDACIÓN DE CADA RECUADRO
// =========================================================
function setError(slot, message) {
    document.getElementById("error-" + slot).textContent = message || "";
    document.getElementById("slot-" + slot).classList.toggle("invalid", !!message);
    document.getElementById("slot-" + slot).classList.toggle("valid", !message && validity[slot]);
}

function updateGenerateButton() {
    const allValid = SLOTS.every((s) => validity[s]);
    generateBtn.disabled = !allValid;
}

function handleFileSelected(slot, file) {
    validity[slot] = false;
    files[slot] = null;
    document.getElementById("preview-" + slot).style.display = "none";

    if (!file) {
        setError(slot, "");
        updateGenerateButton();
        return;
    }

    if (!file.type.startsWith("image/")) {
        setError(slot, "El archivo seleccionado no es una imagen.");
        updateGenerateButton();
        return;
    }

    const url = URL.createObjectURL(file);
    const img = new Image();

    img.onload = () => {
        if (img.naturalWidth !== REQUIRED_SIZE || img.naturalHeight !== REQUIRED_SIZE) {
            setError(
                slot,
                `Esta imagen mide ${img.naturalWidth}x${img.naturalHeight} px. ` +
                `Debe medir exactamente 240x240 px.`
            );
            updateGenerateButton();
            return;
        }

        // Imagen válida
        validity[slot] = true;
        files[slot] = file;
        setError(slot, "");

        const previewEl = document.getElementById("preview-" + slot);
        previewEl.src = url;
        previewEl.style.display = "block";
        document.querySelector(`#slot-${slot} .upload-placeholder`).style.display = "none";

        updateGenerateButton();
    };

    img.onerror = () => {
        setError(slot, "No se ha podido leer la imagen. Prueba con otro archivo.");
        updateGenerateButton();
    };

    img.src = url;
}

SLOTS.forEach((slot) => {
    document.getElementById("file-" + slot).addEventListener("change", (e) => {
        const file = e.target.files[0] || null;
        handleFileSelected(slot, file);
    });
});

// =========================================================
// GENERAR PREDICCIÓN
// =========================================================
generateBtn.addEventListener("click", async () => {
    const allValid = SLOTS.every((s) => validity[s]);
    if (!allValid) {
        alert("Debes subir las 4 imágenes (FLAIR, T1, T1ce, T2), todas de 240x240 píxeles.");
        return;
    }

    const statusEl = document.getElementById("upload-status");
    generateBtn.disabled = true;
    generateBtn.textContent = "Generando...";
    statusEl.textContent = "";

    const formData = new FormData();
    SLOTS.forEach((slot) => formData.append(slot, files[slot]));

    try {
        const response = await fetch("/api/predict_upload", {
            method: "POST",
            body: formData,
        });
        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById("upload-result-panel").style.display = "block";
        document.getElementById("img-pred-upload").src = data.mask_pred;
        statusEl.textContent = "Predicción generada correctamente.";
    } catch (err) {
        alert("Ha ocurrido un error al generar la predicción. Inténtalo de nuevo.");
    } finally {
        generateBtn.disabled = !SLOTS.every((s) => validity[s]);
        generateBtn.textContent = "Generar predicción";
    }
});