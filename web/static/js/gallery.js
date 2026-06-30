// =========================================================
// GALERÍA DE CASOS DE TEST
// =========================================================
const container = document.getElementById("gallery-grid");

async function loadGallery() {
    const response = await fetch("/api/gallery_list");
    const cases = await response.json();

    cases.forEach((c) => {
        const card = document.createElement("div");
        card.className = "gallery-card";
        card.innerHTML = `
            <img src="/api/thumbnail/${c.id}" alt="${c.title}" class="gallery-thumb" loading="lazy">
            <p>${c.title}</p>
        `;
        card.addEventListener("click", () => {
            window.location.href = "/preview/" + c.id;
        });
        container.appendChild(card);
    });
}

loadGallery();