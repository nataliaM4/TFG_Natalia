// =========================================================
// MENÚ LATERAL
// =========================================================
const menuToggle = document.getElementById("menu-toggle");
const sideMenu = document.getElementById("side-menu");

menuToggle.addEventListener("click", () => {
    sideMenu.classList.toggle("open");
});

// =========================================================
// ESTADO
// =========================================================
let currentCaseId = null;

// =========================================================
// MOSTRAR UN CASO EN PANTALLA
// =========================================================
function showCase(data) {
    currentCaseId = data.case_id;

    document.getElementById("thumb-flair").src = data.flair;
    document.getElementById("thumb-t1").src = data.t1;
    document.getElementById("thumb-t1ce").src = data.t1ce;
    document.getElementById("thumb-t2").src = data.t2;

    document.getElementById("input-placeholder").style.display = "none";
    document.getElementById("thumb-grid").style.display = "grid";

    const caseLabel = document.getElementById("case-label");
    caseLabel.textContent = "Caso usado: " + (data.case_id + 1);
    caseLabel.style.display = "block";

    document.getElementById("img-mask-real").src = data.mask_real;
    document.getElementById("real-mask-corner").style.display = "block";

    // Reinicia el panel de predicción hasta que se pulse "Generar predicción"
    document.getElementById("img-pred").style.display = "none";
    document.getElementById("output-placeholder").style.display = "block";
    document.getElementById("output-placeholder").textContent =
        "Pulsa \"Generar predicción\" para ver el resultado";
    document.getElementById("dice-result").textContent = "";

    document.getElementById("bg-watermark").classList.add("hidden");
}

// =========================================================
// IMAGEN ALEATORIA
// =========================================================
document.getElementById("menu-random").addEventListener("click", async () => {
    sideMenu.classList.remove("open");
    const res = await fetch("/api/random_case");
    const data = await res.json();
    showCase(data);
});

// =========================================================
// IR A LA GALERÍA
// =========================================================
document.getElementById("menu-gallery").addEventListener("click", () => {
    window.location.href = "/gallery";
});

// =========================================================
// IR A LA PÁGINA DE SUBIR IMAGEN
// =========================================================
document.getElementById("menu-upload").addEventListener("click", () => {
    window.location.href = "/upload";
});

// =========================================================
// SI VENIMOS DE "USAR ESTA IMAGEN" (preview.html), cargamos
// ese caso automáticamente al entrar en la página principal.
// =========================================================
window.addEventListener("DOMContentLoaded", async () => {
    const params = new URLSearchParams(window.location.search);
    const caseParam = params.get("case");

    if (caseParam !== null) {
        const res = await fetch("/api/case/" + caseParam);
        if (res.ok) {
            const data = await res.json();
            showCase(data);
        }
        // Limpia el parámetro de la URL sin recargar la página
        window.history.replaceState({}, "", "/");
    }
});

// =========================================================
// GENERAR PREDICCIÓN
// =========================================================
document.getElementById("btn-generate").addEventListener("click", async () => {
    if (currentCaseId === null) {
        alert("Primero elige una imagen (Imagen aleatoria o Ver imágenes).");
        return;
    }

    const btn = document.getElementById("btn-generate");
    btn.disabled = true;
    btn.textContent = "Generando...";

    try {
        const response = await fetch("/api/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ case_id: currentCaseId }),
        });
        const data = await response.json();

        if (data.error) {
            alert("Error: " + data.error);
            return;
        }

        document.getElementById("output-placeholder").style.display = "none";
        const imgPred = document.getElementById("img-pred");
        imgPred.src = data.mask_pred;
        imgPred.style.display = "block";

        document.getElementById("dice-result").innerHTML =
            "Coeficiente Dice: <b>" + data.dice.toFixed(4) + "</b>";
    } finally {
        btn.disabled = false;
        btn.textContent = "Generar predicción";
    }
});