import sys
import json
import io
import math

sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main(app_data):
    try:

        with open('gameCache.json', 'r', encoding='utf-8') as f:
            cache = json.load(f)

        user_games = app_data.get('Merged', {}).get('games', [])

        # store owned games in a set so they can be filtered out later
        owned_games = {game["name"].lower().strip() for game in user_games}

        user_profile = {"genres": {}, "tags": {}}
        total_hours = 0

        for game in user_games:
            name_key = game['name'].lower().strip() # normalise the name(s)
            hours = float(game.get('hours', 0)) # get playtime as a number
            total_hours += hours

            if name_key in cache:
                data = cache[name_key] # looking through teh cache to find the data for the namekey

                for g in data.get('genres', []): # go through the genres assigned to the namekey
                    user_profile["genres"][g] = user_profile["genres"].get(g, 0) + hours # tells it work on the current genre its looping through and add the hours that are here

                for t in data.get('tags', []):
                    user_profile["tags"][t] = user_profile["tags"].get(t, 0) + (hours * 0.5) # does the same for tags but is half the value

        candidates = [
            {"name": "Halo Reach", "genres": ["action", "shooter"], "tags": ["sci-fi", "classic"], "metacritic": 91},
            {"name": "Counter-Strike 2", "genres": ["action", "shooter"], "tags": ["competitive", "tactical"], "metacritic": 82},
            {"name": "Apex Legends", "genres": ["action", "shooter"], "tags": ["battle-royale", "movement"], "metacritic": 88},
            {"name": "Valorant", "genres": ["action", "shooter"], "tags": ["tactical", "hero-shooter"], "metacritic": 80},
            {"name": "Stardew Valley", "genres": ["rpg", "simulation", "indie"], "tags": ["relaxing", "crafting"], "metacritic": 89},
            {"name": "Animal Crossing", "genres": ["simulation"], "tags": ["relaxing", "social"], "metacritic": 90},
            {"name": "Unpacked", "genres": ["puzzle", "indie"], "tags": ["relaxing", "short"], "metacritic": 84},
            {"name": "Slime Rancher", "genres": ["adventure", "indie"], "tags": ["cute", "exploration"], "metacritic": 81},
            {"name": "Hades", "genres": ["action", "indie"], "tags": ["roguelike", "great-soundtrack"], "metacritic": 93},
            {"name": "Slay the Spire", "genres": ["strategy", "indie"], "tags": ["roguelike", "deck-builder"], "metacritic": 89},
            {"name": "Dead Cells", "genres": ["action", "indie"], "tags": ["roguelike", "metroidvania"], "metacritic": 89},
            {"name": "Balatro", "genres": ["strategy", "indie"], "tags": ["roguelike", "addictive"], "metacritic": 90},
            {"name": "Elden Ring", "genres": ["action", "rpg"], "tags": ["difficult", "open-world"], "metacritic": 96},
            {"name": "Dark Souls III", "genres": ["action", "rpg"], "tags": ["difficult", "dark-fantasy"], "metacritic": 89},
            {"name": "sekiro: shadows die twice", "genres": ["action", "adventure"], "tags": ["difficult", "stealth"], "metacritic": 90},
            {"name": "Lies of P", "genres": ["action", "rpg"], "tags": ["difficult", "souls-like"], "metacritic": 80},
            {"name": "Baldurs Gate 3", "genres": ["rpg", "strategy"], "tags": ["story-rich", "turn-based"], "metacritic": 96},
            {"name": "The Witcher 3", "genres": ["rpg", "action"], "tags": ["open-world", "story-rich"], "metacritic": 92},
            {"name": "Cyberpunk 2077", "genres": ["rpg", "action"], "tags": ["sci-fi", "open-world"], "metacritic": 86},
            {"name": "Starfield", "genres": ["rpg", "action"], "tags": ["space", "exploration"], "metacritic": 83},
            {"name": "Age of Empires II", "genres": ["strategy"], "tags": ["rts", "historical"], "metacritic": 92},
            {"name": "Starcraft II", "genres": ["strategy"], "tags": ["rts", "sci-fi"], "metacritic": 93},
            {"name": "Manor Lords", "genres": ["strategy", "simulation"], "tags": ["city-builder", "historical"], "metacritic": 84},
            {"name": "Civilization VI", "genres": ["strategy"], "tags": ["4x", "turn-based"], "metacritic": 88},
            {"name": "Forza Horizon 5", "genres": ["racing", "sports"], "tags": ["open-world", "cars"], "metacritic": 92},
            {"name": "Gran Turismo 7", "genres": ["racing", "sports"], "tags": ["simulation", "cars"], "metacritic": 87},
            {"name": "F1 24", "genres": ["racing", "sports"], "tags": ["simulation", "competitive"], "metacritic": 78},
            {"name": "Assetto Corsa", "genres": ["racing", "sports"], "tags": ["simulation", "realistic"], "metacritic": 85},
            {"name": "FC 25", "genres": ["sports"], "tags": ["football", "competitive"], "metacritic": 76},
            {"name": "NBA 2K25", "genres": ["sports"], "tags": ["basketball", "competitive"], "metacritic": 79},
            {"name": "Madden NFL 25", "genres": ["sports"], "tags": ["american-football", "competitive"], "metacritic": 70},
            {"name": "Rocket League", "genres": ["sports", "action"], "tags": ["competitive", "multiplayer"], "metacritic": 86},
            {"name": "Resident Evil 4", "genres": ["action", "horror"], "tags": ["remake", "survival-horror"], "metacritic": 93},
            {"name": "Silent Hill 2", "genres": ["horror", "adventure"], "tags": ["psychological", "remake"], "metacritic": 86},
            {"name": "Phasmophobia", "genres": ["horror", "indie"], "tags": ["co-op", "ghosts"], "metacritic": 80},
            {"name": "Dead by Daylight", "genres": ["horror", "action"], "tags": ["asymmetrical", "survival"], "metacritic": 71},
            {"name": "Minecraft", "genres": ["sandbox", "survival"], "tags": ["crafting", "creative"], "metacritic": 93},
            {"name": "Rust", "genres": ["survival", "action"], "tags": ["pvp", "crafting"], "metacritic": 69},
            {"name": "Ark Survival Ascended", "genres": ["survival", "action"], "tags": ["dinosaurs", "crafting"], "metacritic": 70},
            {"name": "Terraria", "genres": ["sandbox", "action"], "tags": ["crafting", "exploration"], "metacritic": 83},
            {"name": "Deus Ex", "genres": ["rpg", "shooter"], "tags": ["cyberpunk", "immersive-sim"], "metacritic": 90},
            {"name": "Dishonored 2", "genres": ["action", "adventure"], "tags": ["stealth", "immersive-sim"], "metacritic": 88},
            {"name": "Prey", "genres": ["action", "shooter"], "tags": ["sci-fi", "immersive-sim"], "metacritic": 82},
            {"name": "Hitman 3", "genres": ["action", "stealth"], "tags": ["assassin", "sandbox"], "metacritic": 87}
        ]

        # make generic genres contribute less because they show up in lots of games
        genre_penalty = {
            "action": 0.65,
            "rpg": 0.65,
            "adventure": 0.75,
            "simulation": 0.8,
            "sports": 0.75,
            "strategy": 0.8,
            "shooter": 0.75
        }

        # get all metacritic scores from the candidates so they can be scaled relative to each other
        candidate_metas = [g["metacritic"] for g in candidates if g.get("metacritic") is not None]
        min_meta = min(candidate_metas) if candidate_metas else 0
        max_meta = max(candidate_metas) if candidate_metas else 100
        meta_range = max(max_meta - min_meta, 1) # prevents division by 0 if all metas are the same

        # get the biggest profile values so genres/tags can be normalised down to a more equal scale
        max_genre_profile = max(user_profile["genres"].values(), default=1)
        max_tag_profile = max(user_profile["tags"].values(), default=1)

        results = []

        for game in candidates: # look through each of potential candidates
            name_key = game["name"].lower().strip()

            # skip games the user already owns so they can't be recommended back
            if name_key in owned_games:
                continue

            genre_score_raw = 0
            genre_details = []

            for g in game['genres']: # look at the genres in the candidates
                raw_value = user_profile["genres"].get(g, 0) # find that genre in the users profile
                penalty = genre_penalty.get(g, 1.0) # if its a broad genre reduce how much it is worth
                adjusted_value = raw_value * penalty # create the reduced genre value

                genre_score_raw += adjusted_value # add the adjusted genre score instead of the full one

                if raw_value > 0:
                    genre_details.append({
                        "name": g,
                        "raw": round(raw_value, 2),
                        "adjusted": round(adjusted_value, 2),
                        "weighted": 0 # fill this in later once the normalising and weight has been applied
                    })

            tag_score_raw = 0
            tag_details = []

            for t in game['tags']:
                raw_value = user_profile["tags"].get(t, 0) # find the tag in the user profile and add it to the score
                tag_score_raw += raw_value

                if raw_value > 0:
                    tag_details.append({
                        "name": t,
                        "raw": round(raw_value, 2),
                        "weighted": 0 # fill this in later once the normalising and weight has been applied
                    })

            # normalise the genre and tag values so they are on a similar scale
            genre_score = genre_score_raw / max_genre_profile if max_genre_profile > 0 else 0
            tag_score = tag_score_raw / max_tag_profile if max_tag_profile > 0 else 0

            # scale metacritic relative to the range of candidate games so it actually contributes
            quality = (game['metacritic'] - min_meta) / meta_range if game.get("metacritic") is not None else 0

            # genre still matters most, then tag, but metacritic now has a bit more influence
            w1, w2, w3 = 0.50, 0.35, 0.15

            genre_weighted = genre_score * w1
            tag_weighted = tag_score * w2
            metacritic_weighted = quality * w3

            final_score = genre_weighted + tag_weighted + metacritic_weighted

            # work out each genres weighted amount after the adjusting + normalising
            for item in genre_details:
                adjusted_normalized = (item["adjusted"] / max_genre_profile) if max_genre_profile > 0 else 0
                item["weighted"] = round(adjusted_normalized * w1, 4)

            # do the same for tags but without the genre penalty part
            for item in tag_details:
                normalized_tag = (item["raw"] / max_tag_profile) if max_tag_profile > 0 else 0
                item["weighted"] = round(normalized_tag * w2, 4)

            results.append({
                "name": game["name"],
                "score": round(final_score, 4),
                "breakdown": {
                    "genre_total": round(genre_weighted, 4),
                    "tag_total": round(tag_weighted, 4),
                    "metacritic_total": round(metacritic_weighted, 4)
                },
                "details": {
                    "genres": genre_details,
                    "tags": tag_details
                },
                "formula": {
                    "genre_score_raw": round(genre_score_raw, 2),
                    "tag_score_raw": round(tag_score_raw, 2),
                    "quality_raw": round(quality, 4),
                    "weights": {
                        "genre": w1,
                        "tag": w2,
                        "metacritic": w3
                    }
                }
            })

        # Sort by highest score
        results = sorted(results, key=lambda x: x['score'], reverse=True)
        print(json.dumps(results))

    except Exception as e:
        print(json.dumps({"error": str(e)}))


def KNN(app_data):
    try:
        with open('gameCache.json', 'r', encoding='utf-8') as f:
            cache = json.load(f)

        user_games = app_data.get('Merged', {}).get('games', [])

        user_games_normalized = {n["name"].lower().strip() for n in user_games}
        user_games_dict = {n["name"].lower().strip(): float(n.get("hours", 0)) for n in user_games}

        player_profiles = [
            {"label": "FPS", "gameData": {"halo reach": 80, "counter-strike 2": 150, "apex legends": 120, "valorant": 90, "call of duty: warzone": 140, "rainbow six siege": 110}},
            {"label": "Hero Shooter", "gameData": {"valorant": 120, "overwatch": 150, "apex legends": 100, "marvel rivals": 80, "team fortress 2": 70, "paladins": 60}},
            {"label": "Cozy", "gameData": {"stardew valley": 150, "animal crossing": 100, "unpacking": 40, "slime rancher": 60, "spiritfarer": 70, "a little to the left": 35}},
            {"label": "Life Sim / Farming", "gameData": {"stardew valley": 140, "coral island": 90, "disney dreamlight valley": 100, "my time at sandrock": 80, "story of seasons": 70, "sun haven": 75}},
            {"label": "Roguelike", "gameData": {"hades": 120, "slay the spire": 100, "dead cells": 90, "balatro": 80, "risk of rain 2": 85, "enter the gungeon": 70}},
            {"label": "Deckbuilder / Strategy Roguelike", "gameData": {"slay the spire": 140, "balatro": 110, "monster train": 90, "inscryption": 80, "wildfrost": 60, "across the obelisk": 50}},
            {"label": "Soulslike", "gameData": {"elden ring": 200, "dark souls iii": 100, "sekiro: shadows die twice": 80, "lies of p": 70, "dead cells": 90, "ori and the blind forest": 1.9}},
            {"label": "Action RPG", "gameData": {"elden ring": 150, "the witcher 3": 140, "monster hunter: world": 110, "nioh 2": 80, "dragon's dogma 2": 70, "dark souls iii": 90}},
            {"label": "CRPG / Narrative RPG", "gameData": {"baldur's gate 3": 180, "divinity: original sin 2": 130, "disco elysium": 90, "pillars of eternity": 70, "pathfinder: wrath of the righteous": 60, "dragon age: origins": 80}},
            {"label": "Open World RPG", "gameData": {"the witcher 3": 150, "cyberpunk 2077": 100, "starfield": 60, "skyrim": 170, "fallout 4": 110, "horizon zero dawn": 80}},
            {"label": "RTS", "gameData": {"age of empires ii": 150, "starcraft ii": 120, "manor lords": 80, "warcraft iii": 90, "command & conquer remastered": 70, "company of heroes 2": 60}},
            {"label": "Grand Strategy / 4X", "gameData": {"civilization vi": 110, "stellaris": 130, "crusader kings iii": 120, "hearts of iron iv": 100, "endless legend": 70, "humankind": 60}},
            {"label": "Racing", "gameData": {"forza horizon 5": 100, "gran turismo 7": 120, "f1 24": 90, "assetto corsa": 70, "need for speed heat": 60, "dirt rally 2.0": 65}},
            {"label": "Sports", "gameData": {"fc 25": 200, "nba 2k25": 150, "madden nfl 25": 80, "rocket league": 120, "tony hawk's pro skater 1 + 2": 50, "pga tour 2k23": 40}},
            {"label": "Horror", "gameData": {"resident evil 4": 60, "silent hill 2": 50, "phasmophobia": 100, "dead by daylight": 150, "outlast": 55}},
            {"label": "Survival / Sandbox", "gameData": {"minecraft": 200, "rust": 150, "ark survival ascended": 120, "terraria": 100, "valheim": 110, "don't starve together": 80}},
            {"label": "Immersive Sim", "gameData": {"deus ex": 80, "dishonored 2": 70, "prey": 90, "hitman 3": 110, "system shock remake": 60, "deathloop": 75}},
            {"label": "Stealth", "gameData": {"hitman 3": 120, "dishonored 2": 90, "metal gear solid v: the phantom pain": 140, "splinter cell: blacklist": 70, "thief": 50, "aragami": 45}},
            {"label": "Platformer / Metroidvania", "gameData": {"ori and the blind forest": 100, "hollow knight": 150, "dead cells": 80, "celeste": 90, "metroid dread": 70, "blasphemous": 60}},
            {"label": "Creative / Building", "gameData": {"minecraft": 180, "terraria": 90, "cities: skylines": 130, "planet coaster": 80, "satisfactory": 120, "factorio": 140}}
        ]

        total_games_list = set(user_games_normalized)

        for p in player_profiles:
            total_games_list.update(p["gameData"].keys())

        total_games_list = sorted(list(total_games_list))

        vector = []
        total = sum(user_games_dict.values())

        for t in total_games_list:
            game_hours = user_games_dict.get(t, 0) / total if total > 0 else 0
            vector.append(game_hours)

        distances = []

        for p in player_profiles:
            total_p = sum(p["gameData"].values())

            vec = []
            for t in total_games_list:
                value = p["gameData"].get(t, 0) / total_p if total_p > 0 else 0
                vec.append(value)

            dot_product = sum(vector[i] * vec[i] for i in range(len(total_games_list)))

            magnitude_user = math.sqrt(sum(vector[i] ** 2 for i in range(len(total_games_list))))
            magnitude_profile = math.sqrt(sum(vec[i] ** 2 for i in range(len(total_games_list))))

            if magnitude_user > 0 and magnitude_profile > 0:
                similarity = dot_product / (magnitude_user * magnitude_profile)
            else:
                similarity = 0

            distances.append({
                "label": p["label"],
                "similarity": similarity,
                "data": p["gameData"]
            })

        ranked = sorted(distances, key=lambda x: x["similarity"], reverse=True)
        top_k = ranked[:3]

        game_adjacency_list = []
        neighbor_names = [n["label"] for n in top_k]

        all_neighbor_games = set()
        for n in top_k:
            all_neighbor_games.update(n["data"].keys())

        for g_name in all_neighbor_games:

            total_n1 = sum(top_k[0]["data"].values()) if len(top_k) > 0 else 1
            total_n2 = sum(top_k[1]["data"].values()) if len(top_k) > 1 else 1
            total_n3 = sum(top_k[2]["data"].values()) if len(top_k) > 2 else 1

            coords = {
                "x": (top_k[0]["data"].get(g_name, 0) / total_n1) * 100,
                "y": (top_k[1]["data"].get(g_name, 0) / total_n2) * 100,
                "z": (top_k[2]["data"].get(g_name, 0) / total_n3) * 100
            }
            owners = [p["label"] for p in player_profiles if g_name.lower().strip() in {k.lower().strip() for k in p["gameData"].keys()}]

            active_neighbors = [n["label"] for n in top_k if g_name.lower().strip() in {k.lower().strip() for k in n["data"].keys()}]

            pulls = [coords["x"], coords["y"], coords["z"]]
            max_pull_index = pulls.index(max(pulls))
            primary_neighbor = neighbor_names[max_pull_index]

            strength = max(coords["x"], coords["y"], coords["z"])

            game_adjacency_list.append({
                "name": g_name,
                "coords": coords,
                "owned": g_name.lower().strip() in user_games_normalized,
                "group": primary_neighbor, 
                "groups": active_neighbors,
                "all_owners": ", ".join(owners), 
                "strength": strength
            })

        results = {}

        for rank, neighbor in enumerate(top_k):
            weight = 1 - (rank * 0.2)

            game_data = neighbor["data"]
            total_neighbor = sum(game_data.values())

            for title, hours in game_data.items():
                name_key = title.lower().strip()

                if name_key not in user_games_normalized:

                    neighbor_relevance = (hours / total_neighbor) * 10

                    final_score = neighbor_relevance * weight

                    if name_key not in results: 
                        results[name_key] = {
                            "name": title,
                            "score": 0,
                            "contributions": {}
                        }      
                    results[name_key]["score"] += final_score
                    results[name_key]["contributions"][neighbor["label"]] = final_score

        final = sorted(results.values(), key=lambda x: x["score"], reverse=True)

        for item in final:
            total = sum(item["contributions"].values())

            if total > 0:
                for k in item["contributions"]:
                    item["contributions"][k] /= total

            for k in item["contributions"]:
                item["contributions"][k] = round(item["contributions"][k], 2)

            item["score"] = round(item["score"], 2)

        print(json.dumps({"recommendations": final, "similarities": ranked, "game_adjacency": game_adjacency_list, "neighbors": neighbor_names}))

    except Exception as e:
        print(json.dumps({"error": f"KNN Engine Error: {str(e)}"}))



def KNN2(app_data):
    try:
        user_games = app_data.get('Merged', {}).get('games', [])

        user_games_normalized = {g["name"].lower().strip() for g in user_games}
        user_games_dict = {
            g["name"].lower().strip(): float(g.get("hours", 0))
            for g in user_games
        }

        player_profiles = [
            {"label": "FPS", "gameData": {"halo reach": 80, "counter-strike 2": 150, "apex legends": 120, "valorant": 90, "call of duty: warzone": 140, "rainbow six siege": 110}},
            {"label": "Hero Shooter", "gameData": {"valorant": 120, "overwatch": 150, "apex legends": 100, "marvel rivals": 80, "team fortress 2": 70, "paladins": 60}},
            {"label": "Cozy", "gameData": {"stardew valley": 150, "animal crossing": 100, "unpacking": 40, "slime rancher": 60, "spiritfarer": 70, "a little to the left": 35}},
            {"label": "Life Sim / Farming", "gameData": {"stardew valley": 140, "coral island": 90, "disney dreamlight valley": 100, "my time at sandrock": 80, "story of seasons": 70, "sun haven": 75}},
            {"label": "Roguelike", "gameData": {"hades": 120, "slay the spire": 100, "dead cells": 90, "balatro": 80, "risk of rain 2": 85, "enter the gungeon": 70}},
            {"label": "Deckbuilder / Strategy Roguelike", "gameData": {"slay the spire": 140, "balatro": 110, "monster train": 90, "inscryption": 80, "wildfrost": 60, "across the obelisk": 50}},
            {"label": "Soulslike", "gameData": {"elden ring": 200, "dark souls iii": 100, "sekiro: shadows die twice": 80, "lies of p": 70, "dead cells": 90, "ori and the blind forest": 1.9}},
            {"label": "Action RPG", "gameData": {"elden ring": 150, "the witcher 3": 140, "monster hunter: world": 110, "nioh 2": 80, "dragon's dogma 2": 70, "dark souls iii": 90}},
            {"label": "CRPG / Narrative RPG", "gameData": {"baldur's gate 3": 180, "divinity: original sin 2": 130, "disco elysium": 90, "pillars of eternity": 70, "pathfinder: wrath of the righteous": 60, "dragon age: origins": 80}},
            {"label": "Open World RPG", "gameData": {"the witcher 3": 150, "cyberpunk 2077": 100, "starfield": 60, "skyrim": 170, "fallout 4": 110, "horizon zero dawn": 80}},
            {"label": "RTS", "gameData": {"age of empires ii": 150, "starcraft ii": 120, "manor lords": 80, "warcraft iii": 90, "command & conquer remastered": 70, "company of heroes 2": 60}},
            {"label": "Grand Strategy / 4X", "gameData": {"civilization vi": 110, "stellaris": 130, "crusader kings iii": 120, "hearts of iron iv": 100, "endless legend": 70, "humankind": 60}},
            {"label": "Racing", "gameData": {"forza horizon 5": 100, "gran turismo 7": 120, "f1 24": 90, "assetto corsa": 70, "need for speed heat": 60, "dirt rally 2.0": 65}},
            {"label": "Sports", "gameData": {"fc 25": 200, "nba 2k25": 150, "madden nfl 25": 80, "rocket league": 120, "tony hawk's pro skater 1 + 2": 50, "pga tour 2k23": 40}},
            {"label": "Horror", "gameData": {"resident evil 4": 60, "silent hill 2": 50, "phasmophobia": 100, "dead by daylight": 150, "outlast": 55}},
            {"label": "Survival / Sandbox", "gameData": {"minecraft": 200, "rust": 150, "ark survival ascended": 120, "terraria": 100, "valheim": 110, "don't starve together": 80}},
            {"label": "Immersive Sim", "gameData": {"deus ex": 80, "dishonored 2": 70, "prey": 90, "hitman 3": 110, "system shock remake": 60, "deathloop": 75}},
            {"label": "Stealth", "gameData": {"hitman 3": 120, "dishonored 2": 90, "metal gear solid v: the phantom pain": 140, "splinter cell: blacklist": 70, "thief": 50, "aragami": 45}},
            {"label": "Platformer / Metroidvania", "gameData": {"ori and the blind forest": 100, "hollow knight": 150, "dead cells": 80, "celeste": 90, "metroid dread": 70, "blasphemous": 60}},
            {"label": "Creative / Building", "gameData": {"minecraft": 180, "terraria": 90, "cities: skylines": 130, "planet coaster": 80, "satisfactory": 120, "factorio": 140}}
        ]

        # Build shared game space
        total_games_list = set(user_games_normalized)
        for p in player_profiles:
            total_games_list.update(name.lower().strip() for name in p["gameData"].keys())

        total_games_list = sorted(list(total_games_list))

        # User vector
        total_user = sum(user_games_dict.values())
        user_vector = []
        for game_name in total_games_list:
            value = user_games_dict.get(game_name, 0) / total_user if total_user > 0 else 0
            user_vector.append(value)

        distances = []

        for p in player_profiles:
            total_profile = sum(p["gameData"].values())

            profile_vector = []
            for game_name in total_games_list:
                value = p["gameData"].get(game_name, 0) / total_profile if total_profile > 0 else 0
                profile_vector.append(value)

            distance = math.sqrt(
                sum((user_vector[i] - profile_vector[i]) ** 2 for i in range(len(total_games_list)))
            )

            distances.append({
                "label": p["label"],
                "distance": round(distance, 4),
                "data": p["gameData"]
            })

        # Lower distance = better
        ranked = sorted(distances, key=lambda x: x["distance"])
        top_k = ranked[:3]
        neighbor_names = [n["label"] for n in top_k]

        # ---- Build adjacency data for 3D graph ----
        game_adjacency_list = []
        all_neighbor_games = set()

        for n in top_k:
            all_neighbor_games.update(name.lower().strip() for name in n["data"].keys())

        for g_name in all_neighbor_games:
            total_n1 = sum(top_k[0]["data"].values()) if len(top_k) > 0 else 1
            total_n2 = sum(top_k[1]["data"].values()) if len(top_k) > 1 else 1
            total_n3 = sum(top_k[2]["data"].values()) if len(top_k) > 2 else 1

            coords = {
                "x": (top_k[0]["data"].get(g_name, 0) / total_n1) * 100,
                "y": (top_k[1]["data"].get(g_name, 0) / total_n2) * 100,
                "z": (top_k[2]["data"].get(g_name, 0) / total_n3) * 100
            }

            owners = [
                p["label"]
                for p in player_profiles
                if g_name in {k.lower().strip() for k in p["gameData"].keys()}
            ]

            active_neighbors = [
                n["label"]
                for n in top_k
                if g_name in {k.lower().strip() for k in n["data"].keys()}
            ]

            pulls = [coords["x"], coords["y"], coords["z"]]
            max_pull_index = pulls.index(max(pulls))
            primary_neighbor = neighbor_names[max_pull_index]
            strength = max(pulls)

            game_adjacency_list.append({
                "name": g_name,
                "coords": coords,
                "owned": g_name in user_games_normalized,
                "group": primary_neighbor,
                "groups": active_neighbors,
                "all_owners": ", ".join(owners),
                "strength": strength
            })

        # ---- Recommendation scoring ----
        # Convert distance into closeness so nearer neighbors matter more
        closeness_values = []
        for n in top_k:
            closeness = 1 / (1 + n["distance"])
            closeness_values.append(closeness)

        total_closeness = sum(closeness_values) if sum(closeness_values) > 0 else 1

        results = {}

        for i, neighbor in enumerate(top_k):
            weight = closeness_values[i] / total_closeness
            game_data = neighbor["data"]
            total_neighbor = sum(game_data.values())

            for title, hours in game_data.items():
                name_key = title.lower().strip()

                if name_key not in user_games_normalized:
                    neighbor_relevance = (hours / total_neighbor) * 10
                    final_score = neighbor_relevance * weight

                    if name_key not in results:
                        results[name_key] = {
                            "name": title,
                            "score": 0,
                            "contributions": {}
                        }

                    results[name_key]["score"] += final_score
                    results[name_key]["contributions"][neighbor["label"]] = final_score

        final = sorted(results.values(), key=lambda x: x["score"], reverse=True)

        for item in final:
            total_contribution = sum(item["contributions"].values())

            if total_contribution > 0:
                for k in item["contributions"]:
                    item["contributions"][k] /= total_contribution

            for k in item["contributions"]:
                item["contributions"][k] = round(item["contributions"][k], 2)

            item["score"] = round(item["score"], 2)

        print(json.dumps({
            "recommendations": final,
            "similarities": ranked,   # keeping the same key so frontend can reuse structure
            "game_adjacency": game_adjacency_list,
            "neighbors": neighbor_names
        }))

    except Exception as e:
        print(json.dumps({"error": f"KNN2 Engine Error: {str(e)}"}))

# Random Walk -------------------------------------------------------------------------------------

def RandomWalk(app_data):

    try:
        user_games = app_data.get('Merged', {}).get('games', [])
        user_games_normalized = {g["name"].lower().strip() for g in user_games}
        user_games_dict = {
            g["name"].lower().strip(): float(g.get("hours", 0))
            for g in user_games
        }

        player_profiles = [
            {"label": "FPS", "gameData": {"halo reach": 80, "counter-strike 2": 150, "apex legends": 120, "valorant": 90, "call of duty: warzone": 140, "rainbow six siege": 110}},
            {"label": "Hero Shooter", "gameData": {"valorant": 120, "overwatch": 150, "apex legends": 100, "marvel rivals": 80, "team fortress 2": 70, "paladins": 60}},
            {"label": "Cozy", "gameData": {"stardew valley": 150, "animal crossing": 100, "unpacking": 40, "slime rancher": 60, "spiritfarer": 70, "a little to the left": 35}},
            {"label": "Life Sim / Farming", "gameData": {"stardew valley": 140, "coral island": 90, "disney dreamlight valley": 100, "my time at sandrock": 80, "story of seasons": 70, "sun haven": 75}},
            {"label": "Roguelike", "gameData": {"hades": 120, "slay the spire": 100, "dead cells": 90, "balatro": 80, "risk of rain 2": 85, "enter the gungeon": 70}},
            {"label": "Deckbuilder / Strategy Roguelike", "gameData": {"slay the spire": 140, "balatro": 110, "monster train": 90, "inscryption": 80, "wildfrost": 60, "across the obelisk": 50}},
            {"label": "Soulslike", "gameData": {"elden ring": 200, "dark souls iii": 100, "sekiro: shadows die twice": 80, "lies of p": 70, "dead cells": 90, "ori and the blind forest": 1.9}},
            {"label": "Action RPG", "gameData": {"elden ring": 150, "the witcher 3": 140, "monster hunter: world": 110, "nioh 2": 80, "dragon's dogma 2": 70, "dark souls iii": 90}},
            {"label": "CRPG / Narrative RPG", "gameData": {"baldur's gate 3": 180, "divinity: original sin 2": 130, "disco elysium": 90, "pillars of eternity": 70, "pathfinder: wrath of the righteous": 60, "dragon age: origins": 80}},
            {"label": "Open World RPG", "gameData": {"the witcher 3": 150, "cyberpunk 2077": 100, "starfield": 60, "skyrim": 170, "fallout 4": 110, "horizon zero dawn": 80}},
            {"label": "RTS", "gameData": {"age of empires ii": 150, "starcraft ii": 120, "manor lords": 80, "warcraft iii": 90, "command & conquer remastered": 70, "company of heroes 2": 60}},
            {"label": "Grand Strategy / 4X", "gameData": {"civilization vi": 110, "stellaris": 130, "crusader kings iii": 120, "hearts of iron iv": 100, "endless legend": 70, "humankind": 60}},
            {"label": "Racing", "gameData": {"forza horizon 5": 100, "gran turismo 7": 120, "f1 24": 90, "assetto corsa": 70, "need for speed heat": 60, "dirt rally 2.0": 65}},
            {"label": "Sports", "gameData": {"fc 25": 200, "nba 2k25": 150, "madden nfl 25": 80, "rocket league": 120, "tony hawk's pro skater 1 + 2": 50, "pga tour 2k23": 40}},
            {"label": "Horror", "gameData": {"resident evil 4": 60, "silent hill 2": 50, "phasmophobia": 100, "dead by daylight": 150, "outlast": 55}},
            {"label": "Survival / Sandbox", "gameData": {"minecraft": 200, "rust": 150, "ark survival ascended": 120, "terraria": 100, "valheim": 110, "don't starve together": 80}},
            {"label": "Immersive Sim", "gameData": {"deus ex": 80, "dishonored 2": 70, "prey": 90, "hitman 3": 110, "system shock remake": 60, "deathloop": 75}},
            {"label": "Stealth", "gameData": {"hitman 3": 120, "dishonored 2": 90, "metal gear solid v: the phantom pain": 140, "splinter cell: blacklist": 70, "thief": 50, "aragami": 45}},
            {"label": "Platformer / Metroidvania", "gameData": {"ori and the blind forest": 100, "hollow knight": 150, "dead cells": 80, "celeste": 90, "metroid dread": 70, "blasphemous": 60}},
            {"label": "Creative / Building", "gameData": {"minecraft": 180, "terraria": 90, "cities: skylines": 130, "planet coaster": 80, "satisfactory": 120, "factorio": 140}}
        ]

        # stores how strongly each game is connected to others
        graph = {}
        # for front end visualisation, stores each unique game edge once and tracks which profile made that connection
        edge_weights = {}

        # Adding connections between games
        def add_edge(a, b, weight, profile_label):
            # makes it so that a game can't connect to itself
            if a == b:
                return
            
            # makes sure that both games exist in the graph
            if a not in graph:
                graph[a] = {}
            if b not in graph:
                graph[b] = {}
            
            # adds a weighted connection in both directions
            graph[a][b] = graph[a].get(b, 0) + weight
            graph[b][a] = graph[b].get(a, 0) + weight

            edge_key = tuple(sorted([a, b]))

            # if edge hasn't been recored yet add it
            if edge_key not in edge_weights:
                edge_weights[edge_key] = {
                    "source": a,
                    "target": b,
                    "weight": 0,
                    "profiles": set()
                }
            
            # increase edge strength
            edge_weights[edge_key]["weight"] += weight

            # record what profile caused the connection
            edge_weights[edge_key]["profiles"].add(profile_label)
        

        for profile in player_profiles:
            
            # get all of the games from the profile being looped through
            games = list(profile["gameData"].keys())

            # get the total profile hours so the edges can be based on relative strength instead of raw numbers
            total_profile_hours = sum(profile["gameData"].values())

            # make each of the games in this profile related
            for i in range(len(games)):
                for j in range(i + 1, len(games)):

                    game_a = games[i].lower().strip()
                    game_b = games[j].lower().strip()

                    # calculate connection strength - now using each games share of this profile so one profile doesn't overpower the others
                    weight_a = profile["gameData"][games[i]] / total_profile_hours if total_profile_hours > 0 else 0
                    weight_b = profile["gameData"][games[j]] / total_profile_hours if total_profile_hours > 0 else 0
                    weight = (weight_a + weight_b) / 2

                    # add the edge to the graph
                    add_edge(game_a, game_b, weight, profile["label"])


        # combines all the games form the graph with the users games
        all_games = set(graph.keys()) | set(user_games_normalized)

        # only keep user games that are actually in the graph so the walk doesn't waste score on disconnected games
        connected_user_games = {
            game: hours for game, hours in user_games_dict.items()
            if game in graph
        }

        # total hours from users games that can actually spread influence
        connected_total_hours = sum(connected_user_games.values())

        # starting score for each game
        initial_scores = {game: 0 for game in all_games}

        # gives influence to owned games with a higher playtime getting more influence
        if connected_total_hours > 0:
            for game, hours in connected_user_games.items():
                initial_scores[game] = hours / connected_total_hours

        
        scores = initial_scores.copy()

        # tracks what contributed to each games score
        contributions = {game: {} for game in all_games}

        if connected_total_hours > 0:
            for game, hours in connected_user_games.items():
                contributions[game][game] = hours / connected_total_hours

        # how much influence spreads through the graph
        alpha = 0.6

        # number of times influence spreads
        iterations = 10

        for _ in range(iterations):
            propagated = {game: 0 for game in all_games}
            propagated_contributions = {game: {} for game in all_games}

            # first: spread influence from every game
            for game in all_games:
                neighbours = graph.get(game, {})

                # if this game has no neighbours, keep its score where it is
                if not neighbours:
                    propagated[game] += scores.get(game, 0)

                    for source_game, value in contributions.get(game, {}).items():
                        propagated_contributions[game][source_game] = (
                            propagated_contributions[game].get(source_game, 0) + value
                        )

                    continue

                total_neighbours_weight = sum(neighbours.values())

                if total_neighbours_weight == 0:
                    continue

                # spread total score and source contributions to neighbours
                for neighbour, weight in neighbours.items():
                    share_ratio = weight / total_neighbours_weight
                    share_score = scores.get(game, 0) * share_ratio

                    # spread overall score
                    propagated[neighbour] += share_score

                    # spread each source game's influence proportionally
                    for source_game, value in contributions.get(game, {}).items():
                        share_value = value * share_ratio
                        propagated_contributions[neighbour][source_game] = (
                            propagated_contributions[neighbour].get(source_game, 0) + share_value
                        )

            # second: apply damping AFTER all spreading is finished
            new_scores = {}
            new_contributions = {}

            for game in all_games:
                new_scores[game] = (
                    (1 - alpha) * initial_scores.get(game, 0)
                    + alpha * propagated.get(game, 0)
                )

                new_contributions[game] = {}

                # keep some of the original contribution
                for source_game, value in contributions.get(game, {}).items():
                    retained = (1 - alpha) * value
                    if retained > 0:
                        new_contributions[game][source_game] = (
                            new_contributions[game].get(source_game, 0) + retained
                        )

                # add the propagated contribution
                for source_game, value in propagated_contributions.get(game, {}).items():
                    spread = alpha * value
                    if spread > 0:
                        new_contributions[game][source_game] = (
                            new_contributions[game].get(source_game, 0) + spread
                        )

            # update only once per iteration
            scores = new_scores
            contributions = new_contributions
        
        recommendations = []

        for game, score in scores.items():
            if game not in user_games_normalized:
                source_breakdown = contributions.get(game, {})

                sorted_sources = sorted(
                    source_breakdown.items(),
                    key=lambda x: x[1],
                    reverse=True
                )

                total_source = sum(source_breakdown.values())

                if total_source > 0:
                    influenced_by_percent = {
                        source: round((value / total_source) * 100, 2)
                        for source, value in sorted_sources[:5]
                    }
                else:
                    influenced_by_percent = {}

                recommendations.append({
                    "name": game,
                    "score": round(score, 4),
                    "influenced_by": influenced_by_percent
                })

        # remove very weak recommendations so only meaningful ones are shown
        recommendations = [r for r in recommendations if r["score"] > 0.001]

        recommendations.sort(key=lambda x: x["score"], reverse=True)

        # nodes = all games
        graph_nodes = []
        for game in all_games:
            graph_nodes.append({
                "id": game,
                "label": game,
                "owned": game in user_games_normalized,  # highlight owned games
                "score": round(scores.get(game, 0), 4)   # node size/intensity
            })

        # edges = connections between games
        graph_edges = []
        for edge in edge_weights.values():
            graph_edges.append({
                "source": edge["source"],
                "target": edge["target"],
                "weight": round(edge["weight"], 4),   # strength of connection
                "profiles": sorted(list(edge["profiles"]))  # which profiles created this link
            })

        print(json.dumps({
            "recommendations": recommendations[:10],  # top 10 results
            "graph_nodes": graph_nodes,
            "graph_edges": graph_edges
        }))
       
    except Exception as e:
        print(json.dumps({"error": f"KNN2 Engine Error: {str(e)}"}))


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        input_raw = sys.stdin.read()
        if not input_raw:
            sys.exit(0) 

        app_data = json.loads(input_raw)
        # l;oad in the cache here asw

        algorithm_choice = app_data.get('algorithmType', 'Linear')

        if algorithm_choice == 'KNN':
            KNN(app_data)
        elif algorithm_choice == "KNN2":
            KNN2(app_data)
        elif algorithm_choice == "RandomWalk":
            RandomWalk(app_data)
        else:
            main(app_data)

    except Exception as e:
        print(json.dumps({"error": f"Gatekeeper error: {str(e)}"}))

