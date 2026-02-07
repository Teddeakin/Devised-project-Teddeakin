const button = document.getElementById("SearchBtn");
const input = document.getElementById("SteamIdInput");

async function fetchJSON(url) {
    const res = await fetch(url);

    if (!res.ok) {
        throw new Error(`Request failed: ${res.status}`);
    }

    return res.json();
}

button.addEventListener("click", async () => {
    const steamId = input.value.trim();

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
