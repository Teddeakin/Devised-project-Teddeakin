const express = require("express");
const axios = require("axios");

const app = express();
app.use(express.urlencoded({extended: false}));
app.listen(3000, () => console.log("Listening on http://localhost:3000"));

app.use(express.static("./public"));


async function getOwnedGames(steamId) {
    const url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/";

    const response = await axios.get(url, {
        params: {
            key: "FAD844C3BB76FAA2E1682BD0EC145303",
            steamid: steamId,
            include_appinfo: true,
            include_played_free_games: true
        }
    });

    console.log("Owned games RAW response:");
    console.log(response.data);

    return response.data.response;
}

async function getPlayerSummary(steamId) {
    const url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/";

    const response = await axios.get(url, {
        params: {
            key: "FAD844C3BB76FAA2E1682BD0EC145303", 
            steamids: steamId
        }
    });

    console.log("Steam API data:");
    console.log(response.data.response.players[0]);

    return response.data.response.players[0];
}

app.get("/api/steam/games/:steamId", async (req, res) => {
    try {
        const data = await getOwnedGames(req.params.steamId);

        if (!data || !data.games) {
            return res.status(404).json({
                error: "No games found (profile private or invalid SteamID)"
            });
        }

        res.json(data);
    } catch (err) {
        console.error(err.message);
        res.status(500).json({ error: "Failed to fetch owned games" });
    }
});

app.get("/api/steam/profile/:steamId", async (req, res) => {
    try {
        const data = await getPlayerSummary(req.params.steamId);
        res.json(data);
    } catch (err) {
        console.error(err.message);
        res.status(500).json({ error: "Failed to fetch Steam data" });
    }
});