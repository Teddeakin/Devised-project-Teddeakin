const appData = {
    steam: {
        profile: null,
        games: []
    },
    xbox: {
        profile: null,
        games: []
    },
    playstation: {
        profile: null,
        games: []
    },
    Merged: {
        games: []
    }
};

const savedData = localStorage.getItem("appData");

function saveAppData() {
    localStorage.setItem("appData", JSON.stringify(appData));
}

function renderSteamLibrary() {
    const steamInfo = document.getElementById("Steam-info");

    if (appData.steam.games.length) {
        steamInfo.innerHTML = appData.steam.games
            .map(game => `${game.name} - ${game.playtimeHours} hrs`)
            .join("<br>");
    } else {
        steamInfo.innerHTML = "";
    }
}

function renderXboxLibrary() {
    const xboxInfo = document.getElementById("Xbox-info");

    if (appData.xbox.games.length) {
        xboxInfo.innerHTML = appData.xbox.games
            .map(game => {
                if (typeof game === "string") return game;
                if (game.name && game.playtimeMinutes) {
                    return `${game.name} - ${(game.playtimeMinutes / 60).toFixed(1)} hrs`;
                }
                if (game.name) return game.name;
                return JSON.stringify(game);
            })
            .join("<br>");
    } else {
        xboxInfo.innerHTML = "";
    }
}

function renderPlaystationLibrary() {
    const playstationInfo = document.getElementById("Playstation-info");

    if (appData.playstation.games.length) {
        playstationInfo.innerHTML = appData.playstation.games
            .map(game => `${game.name} - ${game.playtime}`)
            .join("<br>");
    } else {
        playstationInfo.innerHTML = "";
    }
}

function renderMergedLibrary() {
    const mergedInfo = document.getElementById("Merged-info");

    if (appData.Merged.games.length) {
        mergedInfo.innerHTML = appData.Merged.games
            .map(game => `${game.name} - ${game.hours.toFixed(1)} hrs`)
            .join("<br>");
    } else {
        mergedInfo.innerHTML = "";
    }
}

function refreshMergedLibrary() {
    appData.Merged.games = mergeAllGames();
    saveAppData();
    renderMergedLibrary();
}

if (savedData) {
    const parsed = JSON.parse(savedData);
    Object.assign(appData, parsed);
}

renderSteamLibrary();
renderXboxLibrary();
renderPlaystationLibrary();
renderMergedLibrary();

async function fetchJSON(url) {
    const res = await fetch(url);
    const data = await res.json();

    if (!res.ok) {
        throw new Error(data.error || `Request failed: ${res.status}`);
    }

    return data;
}

// Steam --------------------------------------------------

const SteamButton = document.getElementById("SteamSearchBtn");
const SteamInput = document.getElementById("SteamIdInput");
const SteamDelete = document.getElementById("SteamDeleteBtn");

SteamInput.value = localStorage.getItem("steamId") || "";

SteamButton.addEventListener("click", async () => {
    const steamId = SteamInput.value.trim();

    if (!steamId) {
        return;
    }

    localStorage.setItem("steamId", steamId);

    try {
        const Steam_Profile_Data = await fetchJSON(`/api/steam/profile/${steamId}`);
        const Steam_Games_Data = await fetchJSON(`/api/steam/games/${steamId}`);

        appData.steam.profile = Steam_Profile_Data;
        appData.steam.games = Steam_Games_Data.games.map(game => ({
            name: game.name,
            appid: game.appid,
            playtimeHours: (game.playtime_forever / 60).toFixed(1)
        }));

        saveAppData();
        renderSteamLibrary();
        refreshMergedLibrary();

    } catch (err) {
        console.error("Error fetching Steam data:", err.message);
    }
});

SteamDelete.addEventListener("click", () => {
    localStorage.removeItem("steamId");

    appData.steam.profile = null;
    appData.steam.games = [];
    appData.Merged.games = [];

    SteamInput.value = "";
    saveAppData();

    renderSteamLibrary();
    refreshMergedLibrary();
});

// Xbox -----------------------------------------------

const XboxButton = document.getElementById("XboxSearchBtn");
const XboxInput = document.getElementById("XboxGamertagInput");
const XboxDelete = document.getElementById("XboxDeleteBtn");

XboxInput.value = localStorage.getItem("gamertag") || "";

XboxButton.addEventListener("click", async () => {
    const gamertag = XboxInput.value.trim();

    if (!gamertag) {
        return;
    }

    try {
        localStorage.setItem("gamertag", gamertag);

        const Xbox_Profile_Data = await fetchJSON(`/api/xbox/profile/${encodeURIComponent(gamertag)}`);
        const Xboxgames = await fetchJSON(`/api/xbox/game-names/${Xbox_Profile_Data.xuid}`);

        appData.xbox.profile = Xbox_Profile_Data;
        appData.xbox.games = Xboxgames;

        saveAppData();
        renderXboxLibrary();
        refreshMergedLibrary();

    } catch (err) {
        console.error("Error fetching Xbox data:", err.message);
    }
});

XboxDelete.addEventListener("click", () => {
    localStorage.removeItem("gamertag");

    appData.xbox.profile = null;
    appData.xbox.games = [];
    appData.Merged.games = [];

    XboxInput.value = "";
    saveAppData();

    renderXboxLibrary();
    refreshMergedLibrary();
});

// Playstation --------------------------------------------------

const PlaystationButton = document.getElementById("PlaystationSearchBtn");
const PlaystationInput = document.getElementById("PlaystationUserIdInput");
const PlaystationDelete = document.getElementById("PlaystationDeleteBtn");

PlaystationInput.value = localStorage.getItem("PlaystationId") || "";

PlaystationButton.addEventListener("click", async () => {
    const PlaystationId = PlaystationInput.value.trim();

    if (!PlaystationId) {
        console.log("No Playstation ID entered");
        return;
    }

    try {
        localStorage.setItem("PlaystationId", PlaystationId);

        const Playstation_Games_Data = await fetchJSON(`/api/playstation/games/${PlaystationId}`);

        appData.playstation.games = Playstation_Games_Data.games.map(game => ({
            name: game.name,
            playtime: game.playtime || "0h"
        }));

        saveAppData();
        renderPlaystationLibrary();
        refreshMergedLibrary();

    } catch (err) {
        console.error("Error fetching Playstation data:", err.message);
    }
});

PlaystationDelete.addEventListener("click", () => {
    localStorage.removeItem("PlaystationId");

    appData.playstation.profile = null;
    appData.playstation.games = [];
    appData.Merged.games = [];

    PlaystationInput.value = "";
    saveAppData();

    renderPlaystationLibrary();
    refreshMergedLibrary();
});

// merging data ---------------------------------------------------

function mergeAllGames() {
    const allGames = [
        ...appData.steam.games,
        ...appData.xbox.games,
        ...appData.playstation.games
    ];

    const mergedMap = new Map();

    for (const game of allGames) {
        const name = game.name.trim().toLowerCase();
        let hours = 0;

        if (game.playtimeHours) {
            hours = parseFloat(game.playtimeHours);
        } else if (game.playtime) {
            const h = game.playtime.match(/(\d+)H/i);
            const m = game.playtime.match(/(\d+)M/i);
            const s = game.playtime.match(/(\d+)S/i);

            const hoursNum = h ? parseInt(h[1]) : 0;
            const minutesNum = m ? parseInt(m[1]) : 0;
            const secondsNum = s ? parseInt(s[1]) : 0;

            hours = hoursNum + minutesNum / 60 + secondsNum / 3600;
        } else if (game.playtimeMinutes) {
            hours = game.playtimeMinutes / 60;
        }

        if (mergedMap.has(name)) {
            mergedMap.get(name).hours += hours;
        } else {
            mergedMap.set(name, {
                name: game.name,
                hours: hours
            });
        }
    }

    return Array.from(mergedMap.values());
}

const mergeButton = document.getElementById("MergeGamesBtn");

mergeButton.addEventListener("click", async () => {
    const mergedGames = mergeAllGames();

    try {
        const response = await fetch("/api/fetch-extra-data", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ games: mergedGames })
        });

        const enrichedGames = await response.json();

        appData.Merged.games = enrichedGames;
        saveAppData();
        renderMergedLibrary();

    } catch (err) {
        console.error("Error fetching extra data:", err);
    }
});


const menuToggle = document.getElementById("menuToggle");
const menuClose = document.getElementById("menuClose");
const sideMenu = document.getElementById("sideMenu");
const menuOverlay = document.getElementById("menuOverlay");

function openMenu() {
    sideMenu.classList.add("open");
    menuOverlay.classList.add("show");
}

function closeMenu() {
    sideMenu.classList.remove("open");
    menuOverlay.classList.remove("show");
}

if (menuToggle) {
    menuToggle.addEventListener("click", openMenu);
}

if (menuClose) {
    menuClose.addEventListener("click", closeMenu);
}

if (menuOverlay) {
    menuOverlay.addEventListener("click", closeMenu);
}