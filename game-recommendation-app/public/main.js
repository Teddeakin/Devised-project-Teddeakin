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
    }
};

const savedData = localStorage.getItem("appData");

if (savedData) {
    const parsed = JSON.parse(savedData);

    Object.assign(appData, parsed);

    if (appData.steam.games.length) {
        document.getElementById("Steam-info").innerHTML = appData.steam.games;
    }

    if (appData.xbox.games.length) {
        document.getElementById("Xbox-info").innerHTML = JSON.stringify(appData.xbox.games);
    }

    if (appData.playstation.games.length) {
        document.getElementById("Playstation-info").innerHTML = appData.playstation.games;
    }
}

// Steam --------------------------------------------------

const SteamButton = document.getElementById("SteamSearchBtn");
const SteamInput = document.getElementById("SteamIdInput");

SteamInput.value = localStorage.getItem("steamId") || "";

async function fetchJSON(url) {
    const res = await fetch(url);

    if (!res.ok) {
        throw new Error(`Request failed: ${res.status}`);
    }

    return res.json();
}

SteamButton.addEventListener("click", async () => {
    const steamId = SteamInput.value.trim();

    if (!steamId) {
        console.log("No SteamID entered");
        return;
    }

    localStorage.setItem("steamId", steamId);

    try {

        const Steam_Profile_Data = await fetchJSON(`/api/steam/profile/${steamId}`);
        console.log("Profile data:", Steam_Profile_Data);

        const Steam_Games_Data = await fetchJSON(`/api/steam/games/${steamId}`);
        console.log("Owned games:", Steam_Games_Data);

        appData.steam.profile = Steam_Profile_Data;
        appData.steam.games = Steam_Games_Data.games.map(game => game.name);

        localStorage.setItem("appData", JSON.stringify(appData));

        document.getElementById("Steam-info").innerHTML = appData.steam.games;

    } catch (err) {
        console.error("Error fetching Steam data:", err.message);
    }
});

// Xbox -----------------------------------------------

const XboxButton = document.getElementById("XboxSearchBtn");
const XboxInput = document.getElementById("XboxGamertagInput");

XboxInput.value = localStorage.getItem("gamertag") || "";

async function fetchJSON(url) {
    const res = await fetch(url);

    const data = await res.json();

    if (!res.ok) {
        throw new Error(data.error || `Request failed: ${res.status}`);
    }

    return data;
}

XboxButton.addEventListener("click", async () => {
    const gamertag = XboxInput.value.trim();

    if (!gamertag) {
        console.log("No gamertag entered");
        return;
    }

    try {

        localStorage.setItem("gamertag", gamertag);

        const Xbox_Profile_Data = await fetchJSON(`/api/xbox/profile/${encodeURIComponent(gamertag)}`);

        console.log("Xbox profile: ", Xbox_Profile_Data);

        const Xboxgames = await fetchJSON(`/api/xbox/game-names/${Xbox_Profile_Data.xuid}`);
        console.log("Xbox games owned: ", Xboxgames);

        appData.xbox.profile = Xbox_Profile_Data;
        appData.xbox.games = Xboxgames;

        localStorage.setItem("appData", JSON.stringify(appData));

        document.getElementById("Xbox-info").innerHTML = JSON.stringify(Xboxgames);

    } catch (err) {
        console.error("Error fetching Xbox data:", err.message);
    }
}
)

// Playstation --------------------------------------------------

const PlaystationButton = document.getElementById("PlaystationSearchBtn");
const PlaystationInput = document.getElementById("PlaystationUserIdInput");

PlaystationInput.value = localStorage.getItem("PlaystationId") || "";

async function fetchJSON(url) {
    const res = await fetch(url);

    if (!res.ok) {
        throw new Error(`Request failed: ${res.status}`);
    }

    return res.json();
}

PlaystationButton.addEventListener("click", async () => {
    const PlaystationId = PlaystationInput.value.trim();

    if (!PlaystationInput) {
        console.log("No SteamID entered");
        return;
    }

    try {

        localStorage.setItem("PlaystationId", PlaystationId);

        const Playstation_Games_Data = await fetchJSON(`/api/playstation/games/${PlaystationId}`);
        console.log("Owned games:", Playstation_Games_Data);

        appData.playstation.games = Playstation_Games_Data.games.map(game => game.name);

        localStorage.setItem("appData", JSON.stringify(appData));

        document.getElementById("Playstation-info").innerHTML = appData.playstation.games;

    } catch (err) {
        console.error("Error fetching Steam data:", err.message);
    }
});