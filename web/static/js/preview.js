// =========================================================
// VISTA PREVIA DE UN CASO
// =========================================================
const caseId = document.body.dataset.caseId;

async function loadCase() {
    const response = await fetch("/api/case/" + caseId);
    const data = await response.json();

    document.getElementById("prev-flair").src = data.flair;
    document.getElementById("prev-t1").src = data.t1;
    document.getElementById("prev-t1ce").src = data.t1ce;
    document.getElementById("prev-t2").src = data.t2;
    document.getElementById("prev-mask-real").src = data.mask_real;
}

loadCase();

// =========================================================
// USAR ESTE CASO EN LA PANTALLA PRINCIPAL
// =========================================================
document.getElementById("btn-use").addEventListener("click", () => {
    window.location.href = "/?case=" + caseId;
});
