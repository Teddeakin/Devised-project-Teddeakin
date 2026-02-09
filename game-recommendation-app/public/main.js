// Steam --------------------------------------------------

const SteamButton = document.getElementById("SteamSearchBtn");
const SteamInput = document.getElementById("SteamIdInput");

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

    try {
        const Steam_Profile_Data = await fetchJSON(`/api/steam/profile/${steamId}`);
        console.log("Profile data:", Steam_Profile_Data);

        const Steam_Games_Data = await fetchJSON(`/api/steam/games/${steamId}`);
        console.log("Owned games:", Steam_Games_Data);

    } catch (err) {
        console.error("Error fetching Steam data:", err.message);
    }
});

// Xbox -----------------------------------------------

const XboxButton = document.getElementById("XboxSearchBtn");
const XboxInput = document.getElementById("XboxGamertagInput");

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
        const Xbox_Profile_Data = await fetchJSON(
            `/api/xbox/profile/${encodeURIComponent(gamertag)}`
        );

        console.log("Xbox profile: ", Xbox_Profile_Data);

        const Xboxgames = await fetchJSON(`/api/xbox/game-names/${Xbox_Profile_Data.xuid}`);
        console.log("Xbox games owned: ", Xboxgames);

    } catch (err) {
        console.error("Error fetching Xbox data:", err.message);
    }
}
)