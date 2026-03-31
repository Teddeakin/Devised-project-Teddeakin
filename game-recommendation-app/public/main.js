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
        document.getElementById("Steam-info").innerHTML = appData.steam.games.map(game => `${game.name} - ${game.playtimeHours} hrs`).join("<br>");
    }

    // if (appData.xbox.games.length) {
    //     document.getElementById("Xbox-info").innerHTML = JSON.stringify(appData.xbox.games);
    // }

    if (appData.playstation.games.length) {
        document.getElementById("Playstation-info").innerHTML = appData.playstation.games.map(game => `${game.name} - ${game.playtime}`).join("<br>");;
    }

    // // console.log(appData.steam.games)
    // // console.log(appData.playstation.games)

    if (appData.Merged.games.length) {
        document.getElementById("Merged-info").innerHTML = appData.Merged.games.map(game => `${game.name} - ${game.hours.toFixed(1)} hrs`).join("<br>");
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
        // console.log("No SteamID entered");
        return;
    }

    localStorage.setItem("steamId", steamId);

    try {

        const Steam_Profile_Data = await fetchJSON(`/api/steam/profile/${steamId}`);
        // console.log("Profile data:", Steam_Profile_Data);

        const Steam_Games_Data = await fetchJSON(`/api/steam/games/${steamId}`);
        // console.log("Owned games:", Steam_Games_Data);

        appData.steam.profile = Steam_Profile_Data;
        appData.steam.games = Steam_Games_Data.games.map(game => ({
            name: game.name,
            appid: game.appid,
            playtimeHours: (game.playtime_forever / 60).toFixed(1)
        }));

        localStorage.setItem("appData", JSON.stringify(appData));

        document.getElementById("Steam-info").innerHTML = appData.steam.games.map(game => `${game.name} - ${game.playtimeHours} hrs`).join("<br>");

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
    // console.log("searching");
    const gamertag = XboxInput.value.trim();

    if (!gamertag) {
        // console.log("No gamertag entered");
        return;
    }

    try {

        localStorage.setItem("gamertag", gamertag);

        const Xbox_Profile_Data = await fetchJSON(`/api/xbox/profile/${encodeURIComponent(gamertag)}`);

        // console.log("Xbox profile: ", Xbox_Profile_Data);

        const Xboxgames = await fetchJSON(`/api/xbox/game-names/${Xbox_Profile_Data.xuid}`);
        // console.log("Xbox games owned: ", Xboxgames);

        appData.xbox.profile = Xbox_Profile_Data;
        appData.xbox.games = Xboxgames;

        // console.log("Xboxgames")

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
        // console.log("No SteamID entered");
        return;
    }

    try {

        localStorage.setItem("PlaystationId", PlaystationId);

        const Playstation_Games_Data = await fetchJSON(`/api/playstation/games/${PlaystationId}`);
        // console.log("Owned games:", Playstation_Games_Data);

        appData.playstation.games = Playstation_Games_Data.games.map(game => ({
            name: game.name,
            playtime: game.playtime || "0h"
        }));

        localStorage.setItem("appData", JSON.stringify(appData));

        document.getElementById("Playstation-info").innerHTML = appData.playstation.games.map(game => `${game.name} - ${game.playtime}`).join("<br>");

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
            // // console.log(game.playtime.match(/(\d+)H/));
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
        // // console.log(game.name, game.playtime);
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
        localStorage.setItem("appData", JSON.stringify(appData));

        document.getElementById("Merged-info").innerHTML =
            mergedGames
                .map(game => `${game.name} - ${game.hours.toFixed(1)} hrs`)
                .join("<br>");

    } catch (err) {
        console.error("Error fetching extra data:", err);
    }
});

// Python -----------------------------------------------------------------

let weightedChart = null; // storing the chart 

const pythonButton = document.getElementById("SendPythonBTN"); /// rename 

pythonButton.addEventListener("click", async () => {
    try {
        const response = await fetch("/api/run-algorithm", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(appData)
        });

        if (!response.ok) throw new Error("Server error");

        const result = await response.json();
        // console.log("Algorithm Results:", result);

        // Check if Python sent an error back
        if (result.error) {
            document.getElementById("Python-responce").innerText = "Error: " + result.error;
            return;
        }

        const recommendationString = result
            .slice(0, 3) // Take the top 3 recommendations
            .map(game => `${game.name} (Match Score: ${game.score})`)
            .join(", ");

        document.getElementById("Python-responce").innerHTML = `Scores: ${recommendationString}`;

        // get the x and y axis
        const labels = result.map(game => game.name);
        const scores = result.map(game => game.score);
        // add something for colours?

        if (weightedChart) { // checks if there already a chart and removes it
            weightedChart.destroy();
        }

        const ctx = document.getElementById("WeightedLinearChart").getContext("2d");

        weightedChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "weighted Chart Score",
                    data: scores,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,

                plugins: {
                    legend: {
                        display: true
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return `Score: ${context.raw}`;
                            }
                        }
                    }
                },

                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: "Match Strength"
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: "Games"
                        }
                    }
                }
            }
        })

    } catch (err) {
        console.error("Error running algorithm:", err);
    }
});


function drawAdjacencyGrid(result) {
    const gamePoints = result.game_adjacency || [];
    const neighbors = result.neighbors || [];
    if (!gamePoints.length || !neighbors.length) return;

    const owned = gamePoints.filter(g => g.owned);
    const recs = gamePoints.filter(g => !g.owned);

    const getHover = (set) =>
        set.map(g => {
            const groups = (g.groups || []).join(", ") || g.group || "None";
            return `<b>${g.name}</b><br>Groups: ${groups}<extra></extra>`; // <br>Profiles: ${g.all_owners}
        });

    const dataTraces = [
        {
            x: owned.map(g => g.coords.x),
            y: owned.map(g => g.coords.y),
            z: owned.map(g => g.coords.z),
            mode: "markers",
            name: "Your Games",
            hovertext: getHover(owned),
            hovertemplate: "%{hovertext}",
            marker: { size: 10, color: "#FFD700" },
            type: "scatter3d"
        },
        {
            x: recs.map(g => g.coords.x),
            y: recs.map(g => g.coords.y),
            z: recs.map(g => g.coords.z),
            mode: "markers",
            name: "Suggestions",
            hovertext: getHover(recs),
            hovertemplate: "%{hovertext}",
            marker: { size: 7, color: "#00FFFF", opacity: 0.7 },
            type: "scatter3d"
        }
    ];

    const seenPairs = new Set();
    const groupPairs = [];

    neighbors.forEach(neighborName => {
        const groupOwned = owned.filter(g => (g.groups || []).includes(neighborName));
        const groupRecs = recs.filter(g => (g.groups || []).includes(neighborName));

        groupOwned.forEach(oGame => {
            groupRecs.forEach(rGame => {
                const pairKey = [oGame.name.toLowerCase(), rGame.name.toLowerCase(), neighborName]
                    .join("|");

                if (!seenPairs.has(pairKey)) {
                    seenPairs.add(pairKey);
                    groupPairs.push({
                        oGame,
                        rGame,
                        neighborName,
                        strength: rGame.strength || 0
                    });
                }
            });
        });
    });

    const sortedPairs = [...groupPairs].sort((a, b) => b.strength - a.strength);

    sortedPairs.forEach((pair, index) => {
        const normalized =
            sortedPairs.length === 1 ? 1 : 1 - index / (sortedPairs.length - 1);

        dataTraces.push({
            type: "scatter3d",
            mode: "lines",
            x: [pair.oGame.coords.x, pair.rGame.coords.x],
            y: [pair.oGame.coords.y, pair.rGame.coords.y],
            z: [pair.oGame.coords.z, pair.rGame.coords.z],
            line: {
                color: `rgba(0, 255, 255, ${0.2 + normalized * 0.8})`,
                width: 1 + normalized * 4
            },
            showlegend: false,
            hovertemplate:
                `<b>${pair.oGame.name}</b> → <b>${pair.rGame.name}</b><br>` +
                `Shared group: ${pair.neighborName}<br>` +
                `<extra></extra>`
        });
    });

    const layout = {
        title: "KNN - cosine",
        paper_bgcolor: "#1a1a1a",
        font: { color: "white" },
        scene: {
            xaxis: { title: neighbors[0] || "N1" },
            yaxis: { title: neighbors[1] || "N2" },
            zaxis: { title: neighbors[2] || "N3" }
        },
        margin: { l: 0, r: 0, b: 0, t: 40 }
    };

    Plotly.newPlot("AdjacencyGrid", dataTraces, layout);
}

KNNCosineChart = null;

const KNNButton = document.getElementById("KNNAlgorithm");

KNNButton.addEventListener("click", async () => {
    try {
        const response = await fetch("/api/run-algorithm", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                ...appData,
                algorithmType: "KNN"
            })
        });

        const result = await response.json();
        // console.log("FULL RESULT:", result);
        // console.log("Recommendations:", result.recommendations);
        // Display results in your KNN UI section
        document.getElementById("KNN-responce").innerHTML = result.recommendations.map(game => `${game.name} - ${game.score}`).join("<br>");

        drawAdjacencyGrid(result);

        const ctx = document.getElementById("CosineChart").getContext("2d");

        // Build scatter data for the recommended games themselves

        const recommendations = result.recommendations || [];

        // console.log("Recommendations array:", recommendations);
        // console.log("First recommendation:", recommendations[0]);

        // Sort best → worst
        recommendations.sort((a, b) => b.score - a.score);

        // console.log("Sorted recommendations:", recommendations);

        // X-axis
        const labels = recommendations.map(game => game.name);

        // Final scores
        const finalScores = recommendations.map(game => game.score);

        // console.log("Final scores:", finalScores);

        // Get all neighbor labels dynamically
        const neighborLabels = new Set();

        recommendations.forEach(game => {
            Object.keys(game.contributions || {}).forEach(label => {
                neighborLabels.add(label);
            });
        });

        // console.log("Neighbor labels:", [...neighborLabels]);

        // Build datasets for each neighbor
        const datasets = [];

        // Final combined score (main line)
        datasets.push({
            label: "Final Score",
            data: finalScores,
            borderColor: 'black',
            pointBackgroundColor: 'black',
            borderWidth: 3,
            tension: 0.3,
            pointRadius: 6,
            fill: false
        });

        const colors = [
            'red',
            'blue',
            'green',
            'orange',
            'purple'
        ];

        let colorIndex = 0;

        // Add each neighbor as its own line
        neighborLabels.forEach(label => {
            const data = recommendations.map(game => {
                const value = game.contributions?.[label];

                // console.log(`Game: ${game.name}, Label: ${label}, Value:`, value);

                return value || 0;
            });

            datasets.push({
                label: `${label} Influence`,
                data: data,
                borderColor: colors[colorIndex % colors.length],
                pointBackgroundColor: colors[colorIndex % colors.length],
                borderWidth: 2,
                tension: 0.3,
                pointRadius: 4,
                fill: false
            });

            colorIndex++;
        });

        if (KNNCosineChart) KNNCosineChart.destroy();

        KNNCosineChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                plugins: {
                    tooltip: {
                        callbacks: {

                            // Title = game name
                            title: function (context) {
                                return context[0].label;
                            },

                            // Main content
                            label: function (context) {
                                const index = context.dataIndex;
                                const game = recommendations[index];

                                let lines = [];

                                // Final score
                                lines.push(`Final Score: ${game.score}`);

                                // Contributions breakdown
                                if (game.contributions) {
                                    Object.entries(game.contributions).forEach(([label, value]) => {
                                        lines.push(`${label}: ${(value * 100).toFixed(1)}%`);
                                    });
                                }

                                return lines;
                            }
                        }
                    }
                }
            }
        });

    } catch (err) {
        console.error("Error running algorithm:", err);
    }
})

const KNNButton2 = document.getElementById("KNNAlgorithm2"); // rename

KNNButton2.addEventListener("click", async () => {
    try {
        const response = await fetch("/api/run-algorithm", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                ...appData,
                algorithmType: "KNN2"
            })
        });

        const result = await response.json();

        // Display results in your KNN UI section
        document.getElementById("KNN-responce2").innerHTML = JSON.stringify(result, null, 2);

    } catch (err) {
        console.error("Error running algorithm:", err);
    }
})