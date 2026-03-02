import sys # gives standard input/ output
import json # gives the same functionality as parsing and stringify

try:
    input_data = sys.stdin.read() 
    data = json.loads(input_data) # converts the string to python object

    merged_games = data.get("Merged", {}).get("games", []) # safely gets the data (same a ?)

    sorted_games = sorted( 
        merged_games,
        key=lambda g: g["hours"], 
        reverse=True
    )

    top5 = sorted_games[:5]

    print(json.dumps(top5)) # sends "top5" to stdout

except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)