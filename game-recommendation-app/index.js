const express = require("express");
const axios = require("axios");
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const app = express();
app.use(express.urlencoded({ extended: false }));
app.use(express.json());
app.use(express.static("./public"));

const server = app.listen(3000, () => {
    console.log("Listening on http://localhost:3000");
});

server.on("close", () => {
    console.log("Server closed");
});

server.on("error", (err) => {
    console.error("Server error:", err);
});

// starts the website on Accounts.html
app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "public", "Accounts.html"));
});

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
                "X-Authorization": "22b72ce9-0cda-406e-a17d-9d06af8e6350"
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

const NPSSO = "3SNP0MDfNRhqrFNczg8seDAylwrgNmRCzMaPpg43uDmsKyLRC9aOLwAdTksIpidV";

app.get("/api/playstation/games/:username", async (req, res) => {
    try {
        const accessToken = await psnLogin(NPSSO);
        const accountId = await getAccountId(accessToken, req.params.username);
        const games = await getUserPlayStationGames(accessToken, accountId);

        res.json({ games });
    } catch (err) {
        console.error("PSN ERROR:", err);
        res.status(500).json({ error: err.message });
    }
});

// Python -----------------------------------------------------------------

app.post("/api/run-algorithm", (req, res) => {
    const python = spawn("python", ["public/algorithm.py"]);

    let result = "";
    let error = "";

    python.stdin.write(JSON.stringify(req.body));
    python.stdin.end();

    python.stdout.on("data", (data) => {
        result += data.toString();
    });

    python.stderr.on("data", (data) => {
        error += data.toString();
    });

    python.on("close", (code) => {
        if (code !== 0) {
            console.error("Python exited with error:", error);
            return res.status(500).json({ error: "Python failed" });
        }

        try {
            const parsed = JSON.parse(result);
            res.json(parsed);
        } catch (err) {
            console.error("Invalid JSON from Python:", result);
            res.status(500).json({ error: "Invalid response from Python" });
        }
    });
});

// Cache data ----------------------------------------------------------

const CACHE_FILE = path.join(__dirname, "gameCache.json");
const STARTER_GAMES_FILE = path.join(__dirname, "starter_games_cache.json");
const RAWG_API_KEY = "f8a5b9f2158646e280f46891ec77ca44";

function normalizeName(name) {
    return String(name || "")
        .replace(/[™®©]/g, " ")
        .normalize("NFKD")
        .replace(/[^\x00-\x7F]/g, "")
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, " ")
        .replace(/\s+/g, " ")
        .trim();
}

function readCache() {
    if (!fs.existsSync(CACHE_FILE)) return {};

    const raw = JSON.parse(fs.readFileSync(CACHE_FILE, "utf8"));
    const normalized = {};

    for (const [key, value] of Object.entries(raw)) {
        normalized[normalizeName(key)] = value;
    }

    return normalized;
}

function writeCache(data) {
    const ordered = Object.fromEntries(
        Object.entries(data).sort(([a], [b]) => a.localeCompare(b))
    );

    fs.writeFileSync(CACHE_FILE, JSON.stringify(ordered, null, 2), "utf8");
}

function readStarterGames() {
    if (!fs.existsSync(STARTER_GAMES_FILE)) return [];
    return JSON.parse(fs.readFileSync(STARTER_GAMES_FILE, "utf8"));
}

function simplifyGameData(rawgData) {
    if (!rawgData) return { error: "No data found" };

    return {
        id: rawgData.id,
        name: rawgData.name,
        released: rawgData.released,
        metacritic: rawgData.metacritic,
        rating: rawgData.rating,
        genres: rawgData.genres?.map(g => g.slug) || [],
        tags: rawgData.tags?.filter(t => t.language === "eng").map(t => t.slug) || [],
        esrb: rawgData.esrb_rating?.slug || "not-rated",
        image: rawgData.background_image
    };
}

async function fetchRawgGame(gameName) {
    const response = await axios.get("https://api.rawg.io/api/games", {
        params: {
            key: RAWG_API_KEY,
            search: gameName,
            page_size: 5
        }
    });

    const results = response.data.results || [];
    if (!results.length) return null;

    const target = normalizeName(gameName);

    results.sort((a, b) => {
        const aName = normalizeName(a.name);
        const bName = normalizeName(b.name);

        let aScore = 0;
        let bScore = 0;

        if (aName === target) aScore += 100;
        else if (aName.includes(target) || target.includes(aName)) aScore += 40;
        aScore += (a.metacritic || 0) / 10;
        aScore += a.rating || 0;

        if (bName === target) bScore += 100;
        else if (bName.includes(target) || target.includes(bName)) bScore += 40;
        bScore += (b.metacritic || 0) / 10;
        bScore += b.rating || 0;

        return bScore - aScore;
    });

    return results[0];
}

let starterCacheReady = false;
let starterCachePromise = null;

async function ensureStarterCache() {
    if (starterCacheReady) return;
    if (starterCachePromise) return starterCachePromise;

    starterCachePromise = (async () => {
        const starterGames = readStarterGames();
        const cache = readCache();

        let updated = false;
        let addedCount = 0;

        for (const title of starterGames) {
            const key = normalizeName(title);

            if (cache[key]) continue;

            try {
                const rawData = await fetchRawgGame(title);

                if (!rawData) {
                    console.log(`No RAWG result for starter game: ${title}`);
                    continue;
                }

                cache[key] = simplifyGameData(rawData);
                updated = true;
                addedCount++;

                console.log(`Cached starter game: ${title}`);

                await new Promise(resolve => setTimeout(resolve, 250));
            } catch (err) {
                console.error(`Failed starter cache fetch for ${title}:`, err.message);
            }
        }

        if (updated) {
            writeCache(cache);
        }

        starterCacheReady = true;
        console.log(`Starter cache ready. Added ${addedCount} new games.`);
    })();

    return starterCachePromise;
}

ensureStarterCache().catch(err => {
    console.error("Starter cache initialization failed:", err.message);
});


app.post("/api/fetch-extra-data", async (req, res) => {
    const { games } = req.body;

    await ensureStarterCache();

    let cache = readCache();
    let updated = false;

    const enrichedGames = await Promise.all(games.map(async (game) => {
        const gameKey = normalizeName(game.name);

        if (cache[gameKey]) {
            return { ...game, extraData: cache[gameKey] };
        }

        try {
            const rawData = await fetchRawgGame(game.name);

            if (!rawData) {
                return game;
            }

            const cleanData = simplifyGameData(rawData);
            cache[gameKey] = cleanData;
            updated = true;

            return { ...game, extraData: cleanData };
        } catch (error) {
            console.error(`Failed to fetch extra data for ${game.name}:`, error.message);
            return game;
        }
    }));

    if (updated) writeCache(cache);
    res.json(enrichedGames);
});