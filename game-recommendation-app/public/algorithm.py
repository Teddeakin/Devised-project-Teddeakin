import sys
import json

try:
    input_data = sys.stdin.read()
    data = json.loads(input_data)

    merged_games = data.get("Merged", {}).get("games", [])

    # Example algorithm:
    # Return top 5 most played games
    sorted_games = sorted(
        merged_games,
        key=lambda g: g["hours"],
        reverse=True
    )

    top5 = sorted_games[:5]

    print(json.dumps(top5))

except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)