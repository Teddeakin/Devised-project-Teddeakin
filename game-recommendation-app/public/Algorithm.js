const appData = JSON.parse(localStorage.getItem("appData")) || null;

if (!appData || !appData.Merged || !appData.Merged.games.length) {
    document.getElementById("status").innerText = "No merged game data found. Please go back to Accounts page first.";
}

// Python -----------------------------------------------------------------

function showWeightedDetails(game) {
    const panel = document.getElementById("WeightedDetailsPanel");
    if (!panel || !game) return;

    const genreDetails = (game.details?.genres || [])
        .map(g => `<li>${g.name}: ${g.weighted} weighted points</li>`)
        .join("");

    const tagDetails = (game.details?.tags || [])
        .map(t => `<li>${t.name}: ${t.weighted} weighted points</li>`)
        .join("");

    panel.innerHTML = `
        <h3>${game.name}</h3>
        <p><strong>Final Score:</strong> ${game.score}</p>

        <p><strong>Formula:</strong></p>
        <p>
            (${game.formula?.genre_score_raw || 0} × ${game.formula?.weights?.genre || 0}) +
            (${game.formula?.tag_score_raw || 0} × ${game.formula?.weights?.tag || 0}) +
            (${game.formula?.quality_raw || 0} × ${game.formula?.weights?.metacritic || 0})
        </p>

        <p><strong>Breakdown:</strong></p>
        <ul>
            <li>Genre Total: ${game.breakdown?.genre_total || 0}</li>
            <li>Tag Total: ${game.breakdown?.tag_total || 0}</li>
            <li>Metacritic Total: ${game.breakdown?.metacritic_total || 0}</li>
        </ul>

        <p><strong>Genre Contributions:</strong></p>
        <ul>${genreDetails || "<li>None</li>"}</ul>

        <p><strong>Tag Contributions:</strong></p>
        <ul>${tagDetails || "<li>None</li>"}</ul>
    `;
}

let weightedChart = null;

const pythonButton = document.getElementById("SendPythonBTN");

pythonButton.addEventListener("click", async () => {
    try {
        const response = await fetch("/api/run-algorithm", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(appData)
        });

        if (!response.ok) throw new Error("Server error");

        const result = await response.json();

        if (result.error) {
            document.getElementById("Python-responce").innerText = "Error: " + result.error;
            return;
        }

        const topGames = result.slice(0, 10);

        const recommendationString = topGames
            .slice(0, 3)
            .map(game => `${game.name} (Match Score: ${game.score})`)
            .join(", ");

        document.getElementById("Python-responce").innerHTML = `Scores: ${recommendationString}`;

        const labels = topGames.map(game => game.name);
        const genreTotals = topGames.map(game => game.breakdown?.genre_total || 0);
        const tagTotals = topGames.map(game => game.breakdown?.tag_total || 0);
        const metacriticTotals = topGames.map(game => game.breakdown?.metacritic_total || 0);

        if (weightedChart) {
            weightedChart.destroy();
        }

        const ctx = document.getElementById("WeightedLinearChart").getContext("2d");

        weightedChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Genre Contribution",
                        data: genreTotals,
                        borderWidth: 1
                    },
                    {
                        label: "Tag Contribution",
                        data: tagTotals,
                        borderWidth: 1
                    },
                    {
                        label: "Metacritic Contribution",
                        data: metacriticTotals,
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                onClick: (event, elements) => {
                    if (!elements.length) return;

                    const index = elements[0].index;
                    showWeightedDetails(topGames[index]);
                },
                plugins: {
                    legend: {
                        display: true
                    },
                    tooltip: {
                        callbacks: {
                            title: function (context) {
                                return context[0].label;
                            },
                            label: function (context) {
                                const game = topGames[context.dataIndex];
                                return [
                                    `Final Score: ${game.score}`,
                                    `Genre Total: ${game.breakdown?.genre_total || 0}`,
                                    `Tag Total: ${game.breakdown?.tag_total || 0}`,
                                    `Metacritic Total: ${game.breakdown?.metacritic_total || 0}`
                                ];
                            },
                            afterBody: function (context) {
                                const game = topGames[context[0].dataIndex];
                                const genreLines = (game.details?.genres || []).map(
                                    g => `Genre - ${g.name}: ${g.weighted}`
                                );
                                const tagLines = (game.details?.tags || []).map(
                                    t => `Tag - ${t.name}: ${t.weighted}`
                                );

                                return [
                                    "--- Details ---",
                                    ...genreLines,
                                    ...tagLines
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        stacked: true,
                        title: {
                            display: true,
                            text: "Games"
                        }
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: "Match Strength"
                        }
                    }
                }
            }
        });

        if (topGames.length > 0) {
            showWeightedDetails(topGames[0]);
        }

    } catch (err) {
        console.error("Error running algorithm:", err);
    }
});

// KNN - Cosine -----------------------------------------------------------------------------


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
                width: 1 + normalized * 10
            },
            showlegend: false,
            hovertemplate:
                `<b>${pair.oGame.name}</b> → <b>${pair.rGame.name}</b><br>` +
                `Shared group: ${pair.neighborName}<br>` +
                `<extra></extra>`
        });
    });

    const layout = {
        title: "KNN",
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

// KNN - Euclidean -----------------------------------------------------------------

let KNNEuclideanChart = null;

const KNNButton2 = document.getElementById("KNNAlgorithm2");

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

        if (result.error) {
            document.getElementById("KNN-responce2").innerText = "Error: " + result.error;
            return;
        }

        // ---- Text output ----
        const recommendations = result.recommendations || [];

        document.getElementById("KNN-responce2").innerHTML =
            recommendations.map(game => `${game.name} - ${game.score}`).join("<br>");

        // ---- 3D graph ----
        drawAdjacencyGrid(result);

        // ---- LINE CHART (EUCLIDEAN) ----
        const ctx = document.getElementById("EuclideanChart").getContext("2d");

        // Sort best → worst
        recommendations.sort((a, b) => b.score - a.score);

        const labels = recommendations.map(game => game.name);
        const finalScores = recommendations.map(game => game.score);

        // Get all neighbor labels dynamically
        const neighborLabels = new Set();

        recommendations.forEach(game => {
            Object.keys(game.contributions || {}).forEach(label => {
                neighborLabels.add(label);
            });
        });

        const datasets = [];

        // Final score line
        datasets.push({
            label: "Final Score",
            data: finalScores,
            borderColor: "black",
            pointBackgroundColor: "black",
            borderWidth: 3,
            tension: 0.3,
            pointRadius: 6,
            fill: false
        });

        const colors = ["red", "blue", "green", "orange", "purple"];
        let colorIndex = 0;

        // Add each neighbor influence
        neighborLabels.forEach(label => {
            const data = recommendations.map(game => {
                return game.contributions?.[label] || 0;
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

        // Destroy old chart if it exists
        if (KNNEuclideanChart) KNNEuclideanChart.destroy();

        KNNEuclideanChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                plugins: {
                    tooltip: {
                        callbacks: {
                            title: function (context) {
                                return context[0].label;
                            },
                            label: function (context) {
                                const index = context.dataIndex;
                                const game = recommendations[index];

                                let lines = [];
                                lines.push(`Final Score: ${game.score}`);

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
        console.error("Error running KNN2:", err);
    }
});


// Random Walk -------------------------------------------------------

let randomWalkNetwork = null;

function drawRandomWalkGraph(result) {
    const container = document.getElementById("RandomWalkGraph");
    const detailsPanel = document.getElementById("RandomWalkDetails");

    if (!container) return;

    const graphNodes = result.graph_nodes || [];
    const graphEdges = result.graph_edges || [];
    const recommendations = result.recommendations || [];

    const recommendationMap = {};
    recommendations.forEach(rec => {
        recommendationMap[rec.name.toLowerCase()] = rec;
    });

    const ownedIds = new Set(
        graphNodes
            .filter(node => node.owned)
            .map(node => node.id.toLowerCase())
    );

    const topRecommendedIds = new Set(
        recommendations
            .slice(0, 8)
            .map(rec => rec.name.toLowerCase())
    );

    // Keep support nodes that connect owned games to top recommendations
    const supportNodeIds = new Set();

    graphEdges.forEach(edge => {
        const source = edge.source.toLowerCase();
        const target = edge.target.toLowerCase();

        const sourceImportant = ownedIds.has(source) || topRecommendedIds.has(source);
        const targetImportant = ownedIds.has(target) || topRecommendedIds.has(target);

        // If one end is important, keep the other end as support
        if (sourceImportant && !targetImportant) {
            supportNodeIds.add(target);
        }
        if (targetImportant && !sourceImportant) {
            supportNodeIds.add(source);
        }
    });

    // Limit support nodes to strongest-scoring ones
    const supportNodesRanked = graphNodes
        .filter(node => supportNodeIds.has(node.id.toLowerCase()))
        .sort((a, b) => (b.score || 0) - (a.score || 0))
        .slice(0, 12);

    const finalNodeIds = new Set([
        ...ownedIds,
        ...topRecommendedIds,
        ...supportNodesRanked.map(node => node.id.toLowerCase())
    ]);

    const filteredNodes = graphNodes.filter(node =>
        finalNodeIds.has(node.id.toLowerCase())
    );

    const filteredEdges = graphEdges.filter(edge => {
        const source = edge.source.toLowerCase();
        const target = edge.target.toLowerCase();

        if (!finalNodeIds.has(source) || !finalNodeIds.has(target)) {
            return false;
        }

        // Keep edges if they touch owned or top-recommended nodes
        return (
            ownedIds.has(source) ||
            ownedIds.has(target) ||
            topRecommendedIds.has(source) ||
            topRecommendedIds.has(target)
        );
    });

    const nodes = filteredNodes.map(node => {
        const id = node.id.toLowerCase();
        const isOwned = ownedIds.has(id);
        const isRecommended = topRecommendedIds.has(id);
        const isSupport = !isOwned && !isRecommended;

        let size = 14 + ((node.score || 0) * 900);
        size = Math.max(12, Math.min(38, size));

        let background = "#888888";
        if (isOwned) background = "#FFD700";
        if (isRecommended) background = "#00FFFF";

        return {
            id,
            label: node.label,
            value: size,
            color: {
                background,
                border: isOwned || isRecommended ? "#ffffff" : "#333333",
                highlight: {
                    background,
                    border: "#ffffff"
                }
            },
            borderWidth: isOwned || isRecommended ? 3 : 1,
            font: {
                color: "#ffffff",
                size: isRecommended ? 16 : 13
            },
            title:
                `${node.label}\n` +
                `Score: ${node.score}\n` +
                (isOwned ? "Owned game" : isRecommended ? "Top recommendation" : "Support node"),
            group: isOwned ? "owned" : isRecommended ? "recommended" : "support"
        };
    });

    const edgeWeightsOnly = filteredEdges.map(edge => edge.weight || 1);
    const minEdgeWeight = Math.min(...edgeWeightsOnly);
    const maxEdgeWeight = Math.max(...edgeWeightsOnly);
    const edgeWeightRange = Math.max(maxEdgeWeight - minEdgeWeight, 1);

    const edges = filteredEdges.map(edge => {
        const source = edge.source.toLowerCase();
        const target = edge.target.toLowerCase();
        const weight = edge.weight || 1;

        // scale each edge between a minimum and maximum thickness
        const normalizedWeight = (weight - minEdgeWeight) / edgeWeightRange;

        // increase this range to make the differences more obvious
        const minWidth = 1;
        const maxWidth = 18;

        const width = minWidth + (normalizedWeight * (maxWidth - minWidth));

        return {
            from: source,
            to: target,
            width,
            color: {
                color: "rgba(0, 255, 255, 0.7)",
                highlight: "rgba(0, 255, 255, 0.85)"
            },
            title:
                `Weight: ${edge.weight}\n` +
                `Profiles: ${(edge.profiles || []).join(", ")}`
        };
    });

    const data = {
        nodes: new vis.DataSet(nodes),
        edges: new vis.DataSet(edges)
    };

    const options = {
        layout: {
            improvedLayout: true
        },
        nodes: {
            shape: "dot",
            scaling: {
                min: 10,
                max: 40
            }
        },
        edges: {
            smooth: {
                type: "dynamic"
            }
        },
        physics: {
            enabled: true,
            stabilization: {
                enabled: true,
                iterations: 250
            },
            barnesHut: {
                gravitationalConstant: -3500,
                centralGravity: 0.18,
                springLength: 160,
                springConstant: 0.025,
                damping: 0.12
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 120,
            navigationButtons: true
        }
    };

    if (randomWalkNetwork) {
        randomWalkNetwork.destroy();
    }

    randomWalkNetwork = new vis.Network(container, data, options);

    randomWalkNetwork = new vis.Network(container, data, options);

    randomWalkNetwork.once("stabilizationIterationsDone", function () {
        randomWalkNetwork.setOptions({ physics: false });
    });

    randomWalkNetwork.on("click", function (params) {
        if (!params.nodes.length) return;

        const nodeId = params.nodes[0];
        const clickedNode = filteredNodes.find(n => n.id.toLowerCase() === nodeId);
        const recommendation = recommendationMap[nodeId];

        const connectedEdges = filteredEdges.filter(edge =>
            edge.source.toLowerCase() === nodeId || edge.target.toLowerCase() === nodeId
        );

        const profileSet = new Set();
        connectedEdges.forEach(edge => {
            (edge.profiles || []).forEach(profile => profileSet.add(profile));
        });

        let influenceHTML = "<li>None</li>";
        if (recommendation && recommendation.influenced_by) {
            const entries = Object.entries(recommendation.influenced_by);
            if (entries.length) {
                influenceHTML = entries
                    .map(([name, value]) => `<li>${name}: ${value}%</li>`)
                    .join("");
            }
        }

        const linkedGames = connectedEdges.map(edge => {
            const source = edge.source.toLowerCase();
            const target = edge.target.toLowerCase();
            return source === nodeId ? edge.target : edge.source;
        });

        detailsPanel.innerHTML = `
            <h3>${clickedNode?.label || nodeId}</h3>
            <p><strong>Owned:</strong> ${clickedNode?.owned ? "Yes" : "No"}</p>
            <p><strong>Final Score:</strong> ${clickedNode?.score ?? "N/A"}</p>
            <p><strong>Connected Profiles:</strong> ${[...profileSet].join(", ") || "None"}</p>
            <p><strong>Connected Games:</strong> ${linkedGames.join(", ") || "None"}</p>
            <p><strong>Top Influence Sources:</strong></p>
            <ul>${influenceHTML}</ul>
        `;
    });
}
const RandomWalkBTN = document.getElementById("RandomWalk");

RandomWalkBTN.addEventListener("click", async () => {
    try {
        const response = await fetch("/api/run-algorithm", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                ...appData,
                algorithmType: "RandomWalk"
            })
        });

        if (!response.ok) throw new Error("Server error");

        const result = await response.json();

        if (result.error) {
            document.getElementById("RandomWalk-Response").innerText = "Error: " + result.error;
            return;
        }

        document.getElementById("RandomWalk-Response").innerHTML =
            (result.recommendations || [])
                .map(game => {
                    const influences = Object.entries(game.influenced_by || {})
                        .map(([name, value]) => `${name}: ${value}%`)
                        .join(", ");

                    return `${game.name} - ${game.score}<br><small>Influenced by: ${influences}</small>`;
                })
                .join("<br><br>");

        drawRandomWalkGraph(result);

    } catch (err) {
        console.error("Error running RandomWalk:", err);
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