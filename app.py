import gradio as gr
import random
import copy

# -----------------------------
# DATASETS (4 Grand Slams)
# -----------------------------
tournaments = {
    "Wimbledon": [
        {"name": "Federer", "wins": 8},
        {"name": "Djokovic", "wins": 7},
        {"name": "Nadal", "wins": 2},
        {"name": "Sampras", "wins": 7},
        {"name": "Alcaraz", "wins": 2},
        {"name": "Murray", "wins": 7},
        {"name": "Borg", "wins": 5},
        {"name": "Laver", "wins": 2},
        {"name": "Newcombe", "wins": 2},
        {"name": "McEnroe", "wins": 3},
        {"name": "Becker", "wins": 3},
        {"name": "Connors", "wins": 2},
        {"name": "Edberg", "wins": 2}     
    ],
    "US Open": [
        {"name": "Federer", "wins": 5},
        {"name": "Sampras", "wins": 5},
        {"name": "Djokovic", "wins": 4},
        {"name": "Connors", "wins": 5},
        {"name": "Nadal", "wins": 4},
        {"name": "McEnroe", "wins": 4},
        {"name": "Lendl", "wins": 3},
        {"name": "Alcaraz", "wins": 2},
        {"name": "Agassi", "wins": 2},
        {"name": "Rafter", "wins": 2},
        {"name": "Edberg", "wins": 2}
    ],
    "Australian Open": [
        {"name": "Djokovic", "wins": 10},
        {"name": "Federer", "wins": 6},
        {"name": "Nadal", "wins": 2},
        {"name": "Agassi", "wins": 4},
        {"name": "Rosewall", "wins": 2},
        {"name": "Wilander", "wins": 3},
        {"name": "Becker", "wins": 2},
        {"name": "Courier", "wins": 2},
        {"name": "Kriek", "wins": 2},
        {"name": "Lendl", "wins": 2},
        {"name": "Sampras", "wins": 2},
        {"name": "Newcombe", "wins": 2},
        {"name": "Sinner", "wins": 2},
        {"name": "Vilas", "wins": 2}
    ],
    "French Open": [
        {"name": "Nadal", "wins": 14},
        {"name": "Djokovic", "wins": 3},
        {"name": "Federer", "wins": 1},
        {"name": "Borg", "wins": 6},
        {"name": "Wilander", "wins": 3},
        {"name": "Lendl", "wins": 3},
        {"name": "Kuerten", "wins": 3},
        {"name": "Kodes", "wins": 2},
        {"name": "Courier", "wins": 2},
        {"name": "Bruguera", "wins": 2},
        {"name": "Alcaraz", "wins": 2}
    ]
}

# Global state
current_players = []

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def get_names(players):
    return [f"{p['name']}({p['wins']})" for p in players]

def format_leaderboard(players):
    return "\n".join(
        [f"{i+1}. {p['name']} ({p['wins']} titles)" for i, p in enumerate(players)]
    )

# -----------------------------
# MERGE SORT
# -----------------------------
def merge_sort(players, steps):
    if len(players) <= 1:
        return players

    mid = len(players) // 2
    left = players[:mid]
    right = players[mid:]

    steps.append(f"Splitting: {get_names(players)} → {get_names(left)} | {get_names(right)}")

    left_sorted = merge_sort(left, steps)
    right_sorted = merge_sort(right, steps)

    return merge(left_sorted, right_sorted, steps)

def merge(left, right, steps):
    result = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        p1 = left[i]
        p2 = right[j]

        steps.append(f"Comparing {p1['name']} ({p1['wins']}) vs {p2['name']} ({p2['wins']})")

        if p1["wins"] >= p2["wins"]:
            result.append(p1)
            steps.append(f"→ {p1['name']} added")
            i += 1
        else:
            result.append(p2)
            steps.append(f"→ {p2['name']} added")
            j += 1

    while i < len(left):
        result.append(left[i])
        steps.append(f"→ {left[i]['name']} added (remaining)")
        i += 1

    while j < len(right):
        result.append(right[j])
        steps.append(f"→ {right[j]['name']} added (remaining)")
        j += 1

    steps.append(f"Merged: {get_names(result)}")
    return result

# -----------------------------
# LOAD TOURNAMENT
# -----------------------------
def load_tournament(tournament_name):
    global current_players

    if tournament_name not in tournaments:
        return "Invalid tournament", "", gr.update(choices=[]), gr.update(choices=[])

    current_players = copy.deepcopy(tournaments[tournament_name])

    leaderboard = format_leaderboard(current_players)
    player_names = [p["name"] for p in current_players]

    return (
        leaderboard,
        "Tournament loaded.",
        gr.update(choices=player_names, value=None),
        gr.update(choices=player_names, value=None)
    )

# -----------------------------
# SORT FUNCTION
# -----------------------------
def sort_players():
    global current_players

    if not current_players:
        return "No players loaded.", ""

    steps = []
    sorted_list = merge_sort(current_players, steps)

    current_players = sorted_list

    return format_leaderboard(sorted_list), "\n".join(steps)

# -----------------------------
# MATCH SIMULATION
# -----------------------------
def simulate_match_ui(p1_name, p2_name):
    global current_players

    if not current_players:
        return "Load a tournament first.", "", ""

    if not p1_name or not p2_name:
        return "Please select both players.", "", ""

    if p1_name == p2_name:
        return "Choose two different players.", "", ""

    p1 = None
    p2 = None

    for p in current_players:
        if p["name"] == p1_name:
            p1 = p
        if p["name"] == p2_name:
            p2 = p

    if p1 is None or p2 is None:
        return "Invalid players selected.", "", ""

    total = p1["wins"] + p2["wins"]
    probA = 0.5 if total == 0 else p1["wins"] / total

    winner = p1 if random.random() < probA else p2
    winner["wins"] += 1

    steps = []
    sorted_list = merge_sort(current_players, steps)
    current_players = sorted_list

    leaderboard = format_leaderboard(sorted_list)

    return f"{winner['name']} wins the match!", leaderboard, "\n".join(steps)

# -----------------------------
# GRADIO UI
# -----------------------------
with gr.Blocks() as app:

    gr.Markdown("# 🎾 Grand Slam Ranking Visualizer (Merge Sort)")
    gr.Markdown("⚠️ Select a tournament first to load players.")

    tournament_dropdown = gr.Dropdown(
        choices=list(tournaments.keys()),
        label="Select Tournament"
    )

    load_button = gr.Button("Load Tournament")

    leaderboard_box = gr.Textbox(label="Leaderboard", lines=10)
    status_box = gr.Textbox(label="Status")

    sort_button = gr.Button("Sort Players")

    steps_box = gr.Textbox(label="Merge Sort Steps", lines=15)

    gr.Markdown("## 🎮 Simulate Match")

    player1 = gr.Dropdown(label="Player 1")
    player2 = gr.Dropdown(label="Player 2")

    match_button = gr.Button("Play Match")

    match_result = gr.Textbox(label="Match Result")

    # -----------------------------
    # CONNECT FUNCTIONS
    # -----------------------------
    load_button.click(
        fn=load_tournament,
        inputs=tournament_dropdown,
        outputs=[leaderboard_box, status_box, player1, player2]
    )

    sort_button.click(
        fn=sort_players,
        inputs=[],
        outputs=[leaderboard_box, steps_box]
    )

    match_button.click(
        fn=simulate_match_ui,
        inputs=[player1, player2],
        outputs=[match_result, leaderboard_box, steps_box]
    )

# Run app
app.launch()