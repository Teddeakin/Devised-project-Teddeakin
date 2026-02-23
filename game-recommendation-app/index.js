const express = require("express");
const axios = require("axios");

const app = express();
app.use(express.urlencoded({ extended: false }));
app.listen(3000, () => console.log("Listening on http://localhost:3000"));

app.use(express.static("./public"));

// Steam -------------------------------------------------------------------------------------

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

    console.log("Owned games:");
    console.log(response.data);

    return response.data.response;
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
        res.status(500).json({
            error: "Failed to fetch owned games"
        });
    }
});

async function getPlayerSummary(steamId) {
    const url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/";

    const response = await axios.get(url, {
        params: {
            key: "FAD844C3BB76FAA2E1682BD0EC145303",
            steamids: steamId
        }
    });

    const player = response.data?.response?.players?.[0];

    return player || null;
}

app.get("/api/steam/profile/:steamId", async (req, res) => {
    try {
        const data = await getPlayerSummary(req.params.steamId);

        if (!data) {
            return res.status(404).json({
                error: "Profile not found or private"
            });
        }

        res.json(data);
    } catch (err) {
        console.error(err.message);
        res.status(500).json({
            error: "Failed to fetch Steam profile"
        });
    }
});

// Xbox ---------------------------------------------------------------------------------

async function searchXboxUser(gamertag) {
    const response = await axios.get(
        `https://xbl.io/api/v2/search/${encodeURIComponent(gamertag)}`,
        {
            headers: {
                "X-Authorization": "c005e453-5d6e-42a1-bdd6-db77b821800a"
            }
        }
    );

    console.log("Search result:");
    console.log(response.data);

    const result = response.data.people?.[0];
    if (!result) return null;

    return result.xuid;
}

async function getXboxProfileByXuid(xuid) {
    const response = await axios.get(
        `https://xbl.io/api/v2/account/${xuid}`,
        {
            headers: {
                "X-Authorization": "22b72ce9-0cda-406e-a17d-9d06af8e6350"
            }
        }
    );

    console.log("Xbox profile:");
    console.log(response.data);

    return response.data;
}

app.get("/api/xbox/profile/:gamertag", async (req, res) => {
    try {
        const xuid = await searchXboxUser(req.params.gamertag);

        if (!xuid) {
            return res.status(404).json({ error: "Gamertag not found" });
        }

        const profile = await getXboxProfileByXuid(xuid);

        res.json({
            xuid,
            profile
        });

    } catch (err) {
        console.error(err.response?.data || err.message);
        res.status(500).json({ error: "Failed to fetch Xbox profile" });
    }
});

// all info to go back to and pick out the stuff i need
// async function getXboxGamesPlayed(xuid) {
//     const response = await axios.get(
//         `https://xbl.io/api/v2/achievements/player/${xuid}`,
//         {
//             headers: {
//                 "X-Authorization": "c005e453-5d6e-42a1-bdd6-db77b821800a"
//             }
//         }
//     );

//     console.log("Xbox games played:");
//     console.log(response.data);

//     return response.data;
// }

// app.get("/api/xbox/games/:xuid", async (req, res) => {
//     try {
//         const data = await getXboxGamesPlayed(req.params.xuid);
//         res.json(data);
//     } catch (err) {
//         console.error(err.response?.data || err.message);
//         res.status(500).json({ error: "Failed to fetch Xbox games" });
//     }
// });

// function for just the names of games owned - xbox

async function getXboxGameNames(xuid) {
    const response = await axios.get(
        `https://xbl.io/api/v2/player/titleHistory/${xuid}`,
        {
            headers: {
                "X-Authorization": "22b72ce9-0cda-406e-a17d-9d06af8e6350"
            }
        }
    );

    console.log("FULL Xbox title history response:");
    console.log(JSON.stringify(response.data, null, 2));

    return response.data.titles?.map(title => title.name) || [];
}

// async function getXboxGameNames(xuid) {
//     const response = await axios.get(
//         `https://xbl.io/api/v2/achievements/player/${xuid}`,
//         {
//             headers: {
//                 "X-Authorization": "c005e453-5d6e-42a1-bdd6-db77b821800a"
//             }
//         }
//     );

//     const names = response.data.titles.map(title => title.name);

//     console.log("Xbox game names:");
//     console.log(names);

//     return names;
// }

app.get("/api/xbox/game-names/:xuid", async (req, res) => {
    try {
        const names = await getXboxGameNames(req.params.xuid);
        res.json(names);
    } catch (err) {
        console.error(err.response?.data || err.message);
        res.status(500).json({ error: "Failed to fetch game names" });
    }
});


// Playstation ---------------------------------------------------------------------------

let psnApi;

async function loadPsnApi() {
    if (!psnApi) {
        psnApi = await import("psn-api");
    }
    return psnApi;
}

async function psnLogin(npsso) {
    const psn = await loadPsnApi();

    const accessCode = await psn.exchangeNpssoForAccessCode(npsso);
    const tokens = await psn.exchangeCodeForAccessToken(accessCode);

    return tokens.accessToken;
}

async function getAccountId(accessToken, username) {
    const psn = await loadPsnApi();

    const result = await psn.makeUniversalSearch(
        { accessToken },
        username,
        "SocialAllAccounts"
    );

    const domain = result.domainResponses?.[0];

    if (!domain?.results?.length) {
        throw new Error("User not found");
    }

    return domain.results[0].socialMetadata.accountId;
}


async function getUserPlayStationGames(accessToken, accountId) {
    const psn = await loadPsnApi();

    let allGames = [];
    let offset = 0;
    const limit = 100;

    while (true) {
        const response = await psn.getUserPlayedGames(
            { accessToken },
            accountId,
            { limit, offset }
        );

        const games = response.titles ?? [];
        allGames.push(...games);

        if (!response.nextOffset) break;

        offset = response.nextOffset;
    }

    return allGames
        .filter(game => game.category.includes("game"))
        .map(game => ({
            name: game.name,
            platform: game.category,
            playtime: game.playDuration,
            lastPlayed: game.lastPlayedDateTime
        }));
}




const NPSSO = "xL33nLA5qsWsO1PoNkzYrzmL5dmwjbnyb5A7GWpxraNxEOoXORZTiXt96nKoPaaw";


app.get("/api/playstation/games/:username", async (req, res) => {
    try {
        const accessToken = await psnLogin(NPSSO);

        const accountId = await getAccountId(
            accessToken,
            req.params.username
        );

        const games = await getUserPlayStationGames(
            accessToken,
            accountId
        );

        res.json({ games });

    } catch (err) {
        console.error("PSN ERROR:", err);
        res.status(500).json({ error: err.message });
    }
});


// normalisation ------------------------------------------------------------------------

