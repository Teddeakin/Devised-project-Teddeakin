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

if (savedData) {
    const parsed = JSON.parse(savedData);

    Object.assign(appData, parsed);

    if (appData.steam.games.length) {
        document.getElementById("Steam-info").innerHTML = appData.steam.games.map(game => `${game.name} - ${game.playtimeHours} hrs`) .join("<br>");
    }

    // if (appData.xbox.games.length) {
    //     document.getElementById("Xbox-info").innerHTML = JSON.stringify(appData.xbox.games);
    // }

    if (appData.playstation.games.length) {
        document.getElementById("Playstation-info").innerHTML = appData.playstation.games .map(game => `${game.name} - ${game.playtime}`) .join("<br>");;
    }

    if (appData.Merged.games.length) {
        document.getElementById("Merged-info").innerHTML = appData.Merged.games .map(game => `${game.name} - ${game.hours.toFixed(1)} hrs`) .join("<br>");
    };

}

// Steam --------------------------------------------------

const SteamButton = document.getElementById("SteamSearchBtn");
const SteamInput = document.getElementById("SteamIdInput");
const SteamDelete = document.getElementById("SteamDeleteBtn");

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
        appData.steam.games = Steam_Games_Data.games.map(game => ({
            name: game.name, 
            appid: game.appid, 
            playtimeHours: (game.playtime_forever / 60).toFixed(1)
        }));

        localStorage.setItem("appData", JSON.stringify(appData));

        document.getElementById("Steam-info").innerHTML = appData.steam.games.map(game => `${game.name} - ${game.playtimeHours} hrs`) .join("<br>");

    } catch (err) {
        console.error("Error fetching Steam data:", err.message);
    }
});

SteamDelete.addEventListener("click", async () => {

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
    console.log("searching");
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

        console.log("Xboxgames")

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

        appData.playstation.games = Playstation_Games_Data.games.map(game => ({
            name: game.name,
            playtime: game.playtime || "0h" 
        }));

        localStorage.setItem("appData", JSON.stringify(appData));

        document.getElementById("Playstation-info").innerHTML = appData.playstation.games .map(game => `${game.name} - ${game.playtime}`) .join("<br>");

    } catch (err) {
        console.error("Error fetching Steam data:", err.message);
    }
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
            // console.log(game.playtime.match(/(\d+)H/));
            const h = game.playtime.match(/(\d+)H/);
            const m = game.playtime.match(/(\d+)M/);
            const s = game.playtime.match(/(\d+)S/);

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
        // console.log(game.name, game.playtime);
    }

    return Array.from(mergedMap.values());
}

const mergeButton = document.getElementById("MergeGamesBtn");

mergeButton.addEventListener("click", () => {

    const mergedGames = mergeAllGames();
    appData.Merged.games = mergedGames;

    localStorage.setItem("appData", JSON.stringify(appData));

    console.log(appData.Merged.games);

    document.getElementById("Merged-info").innerHTML =
        mergedGames
            .map(game => `${game.name} - ${game.hours.toFixed(1)} hrs`)
            .join("<br>");

});

const pythonButton = document.getElementById("SendPythonBTN");

pythonButton.addEventListener("click", async () => {
    try {
        const response = await fetch("/api/run-algorithm", { // 
            method: "POST",
            headers: {
                "Content-Type": "application/json" 
            },
            body: JSON.stringify(appData)
        });
        if (!response.ok) {
            throw new Error("Server error");
        }

        const result = await response.json();

        console.log("Python result:", result);

        document.getElementById("Python-responce").innerHTML =
            result
                .map(game => `${game.name} - ${game.hours.toFixed(1)} hrs`)
                .join("<br>");

    } catch (err) {
        console.error("Error sending data to Python:", err);
    }
});