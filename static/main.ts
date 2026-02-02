
interface UserCard {
    id: number;
    instance_id: string;
    obtained_at: number;
    name: string;
    rarity: string;
    image: string;
}


type UserState = {
    ins: number;
    cards: UserCard[];
};

let user: UserState = {
    ins: 0,
    cards: []
};


const insDiv = document.getElementById("ins-balance")!;
const boosterDiv = document.getElementById("booster")!;
const collectionDiv = document.getElementById("collection")!;

const imageLightbox = document.createElement("div");
imageLightbox.id = "image-lightbox";
imageLightbox.innerHTML = `<img alt="Card preview">`;
document.body.appendChild(imageLightbox);

const lightboxImg = imageLightbox.querySelector("img") as HTMLImageElement;

function showImageFull(src: string) {
    lightboxImg.src = src;
    imageLightbox.classList.add("show");
}

imageLightbox.addEventListener("click", () => {
    imageLightbox.classList.remove("show");
});

const boosterOverlay = document.createElement("div");
boosterOverlay.id = "booster-overlay";
boosterOverlay.innerHTML = `
  <div class="booster-content">
    <img class="booster-image" alt="Booster reveal">
    <div class="booster-caption">
      <strong class="booster-name"></strong>
      <span class="booster-rarity"></span>
      <span class="booster-hint">Click…</span>
    </div>
  </div>
`;
document.body.appendChild(boosterOverlay);

const boosterImg = boosterOverlay.querySelector(".booster-image") as HTMLImageElement;
const boosterName = boosterOverlay.querySelector(".booster-name") as HTMLElement;
const boosterRarity = boosterOverlay.querySelector(".booster-rarity") as HTMLElement;

let boosterReveal: { cards: UserCard[]; index: number } | null = null;

function startBoosterReveal(cards: UserCard[]) {
    boosterReveal = { cards, index: 0 };
    boosterBtn.disabled = true;
    showBoosterStage(0);
    boosterOverlay.classList.add("show");
}

function showBoosterStage(index: number) {
    const card = boosterReveal!.cards[index];
    boosterImg.src = card.image;
    boosterName.textContent = card.name;
    boosterRarity.textContent = card.rarity;
    boosterOverlay.classList.add("animate");
    setTimeout(() => boosterOverlay.classList.remove("animate"), 400);
}

function endBoosterReveal() {
    boosterOverlay.classList.remove("show");
    boosterReveal = null;
    boosterBtn.disabled = false;
}

boosterOverlay.addEventListener("click", () => {
    if (!boosterReveal) return;
    if (boosterReveal.index === 0) {
        boosterReveal.index = 1;
        showBoosterStage(1);
    } else {
        endBoosterReveal();
    }
});


function updateINS() {
    insDiv.textContent = `INS: ${user.ins.toFixed(2)}`;
}


const addInsBtn = document.getElementById("add-ins-btn")!;
addInsBtn.addEventListener("click", async () => {
    try {
        const res = await fetch("/ins/add", {
            method: "POST",
            credentials: "include"
        });
        const json = await res.json();
        user.ins = json.ins;
        updateINS();
    } catch (err) {
        console.error(err);
    }
});

function showTab(tab: string) {
    document.querySelectorAll(".tab-content").forEach(t => {
        (t as HTMLElement).style.display = "none";
    });

    (document.getElementById(tab)!).style.display = "flex";

    if (tab === "collection") renderCollection();
}


document.querySelectorAll(".tabs button").forEach(btn => {
    btn.addEventListener("click", () => {
        const tab = (btn as HTMLElement).dataset.tab;
        if (tab) showTab(tab);
    });
});


const boosterBtn = document.createElement("button");
boosterBtn.textContent = "OPEN BOOSTER (-10 INS)";
boosterBtn.onclick = openBooster;
boosterDiv.appendChild(boosterBtn);

async function openBooster() {
    try {
        const res = await fetch("/booster/open", {
            method: "POST",
            credentials: "include"
        });
        const json = await res.json();
        if (json.detail) {
            alert(json.detail);
            return;
        }
        user.ins = json.ins_balance;
        updateINS();

        const newCards = json.cards.map((c: any) => ({
            id: c.id,
            instance_id: c.instance_id,
            obtained_at: c.obtained_at || Date.now() / 1000,
            name: c.name,
            rarity: c.rarity,
            image: c.image
        }));
        user.cards.push(...newCards);
        startBoosterReveal(newCards);
    } catch (err) {
        console.error(err);
        alert("Error opening booster");
    }
}


function renderCollection() {
    collectionDiv.innerHTML = "<h2>Collection</h2>";

    if (!user.cards || user.cards.length === 0) {
        collectionDiv.innerHTML += "<p>No cards yet</p>";
        return;
    }

    const container = document.createElement("div");
    container.classList.add("card-grid");

    for (const card of user.cards) {
        const cardDiv = document.createElement("div");
        cardDiv.classList.add("card", `rarity-${card.rarity}`);
        cardDiv.innerHTML = `
            <img src="${card.image}" alt="${card.name}">
            <div class="card-name">${card.name}</div>
            <div class="card-rarity">${card.rarity}</div>
        `;
        cardDiv.querySelector("img")!.addEventListener("click", (e) => {
            e.stopPropagation();
            showImageFull(card.image);
        });
        container.appendChild(cardDiv);
    }

    collectionDiv.appendChild(container);
}


async function fetchData() {
    try {
        const res = await fetch("/collection", { credentials: "include" });
        const json = await res.json();
        if (json.detail) {
            alert(json.detail);
            return;
        }
        user.ins = json.ins;
        user.cards = json.cards.map((c: any) => ({
            id: c.id,
            instance_id: c.instance_id,
            obtained_at: c.obtained_at || Date.now() / 1000,
            name: c.name,
            rarity: c.rarity,
            image: c.image
        }));
        updateINS();
    } catch (err) {
        console.error(err);
    }
}

fetchData();
showTab("booster");
