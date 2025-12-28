import time
import random
import json
import numpy as np
import paho.mqtt.client as mqtt
from datetime import datetime, timezone
import sys

# --------------------------------------------
# CONFIG
# --------------------------------------------
BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPIC = "football/players"

SEND_INTERVAL = 0.2
GPS_NOISE = 0.3

FIELD_LENGTH = 105
FIELD_WIDTH = 68

# --------------------------------------------
# GAME MODEL
# --------------------------------------------
GAME_STATES = ["ATTACK", "DEFEND", "PRESS"]

ROLE_ANCHORS = {
    1: ("GK",  (5, 15)),
    2: ("RB",  (30, 55)),
    3: ("RCB", (25, 40)),
    4: ("LCB", (25, 28)),
    5: ("LB",  (30, 13)),
    6: ("DM",  (45, 34)),
    7: ("RCM", (55, 42)),
    8: ("LCM", (55, 26)),
    9: ("RW",  (75, 55)),
    10:("ST",  (80, 34)),
    11:("LW",  (75, 13)),
}

STATE_X_OFFSET = {
    "ATTACK":  +10,
    "DEFEND":  -10,
    "PRESS":   +5
}

STATE_SPEED_FACTOR = {
    "ATTACK": 1.0,
    "DEFEND": 0.7,
    "PRESS":  1.3
}

# --------------------------------------------
# HELPERS
# --------------------------------------------
def mirror_anchor(anchor):
    """Mirror position for away team"""
    x, y = anchor
    return FIELD_LENGTH - x, FIELD_WIDTH - y

def apply_gps_noise(position):
    return position + np.random.normal(0, GPS_NOISE, size=2)

# --------------------------------------------
# MOVEMENT
# --------------------------------------------
def move_player(anchor, game_state, team):
    base_x, base_y = anchor

    offset = STATE_X_OFFSET[game_state]

    # Away team attacks in opposite direction
    if team == "away":
        offset = -offset

    target_x = base_x + offset

    dx = random.uniform(-3, 3)
    dy = random.uniform(-3, 3)

    speed = random.uniform(0.5, 4.0) * STATE_SPEED_FACTOR[game_state]

    new_pos = np.array([
        target_x + dx,
        base_y + dy
    ])

    new_pos[0] = np.clip(new_pos[0], 0, FIELD_LENGTH)
    new_pos[1] = np.clip(new_pos[1], 0, FIELD_WIDTH)

    return new_pos, speed

# --------------------------------------------
# MAIN
# --------------------------------------------
def simulate_player(player_id, team):
    role, base_anchor = ROLE_ANCHORS[player_id]

    anchor = base_anchor
    if team == "away":
        anchor = mirror_anchor(base_anchor)

    client = mqtt.Client()
    client.connect(BROKER_HOST, BROKER_PORT, 60)

    game_state = random.choice(GAME_STATES)
    last_state_change = time.time()

    print(f"Simulating {team.upper()} Player {player_id} ({role})")

    while True:
        if time.time() - last_state_change > random.randint(20, 40):
            game_state = random.choice(GAME_STATES)
            last_state_change = time.time()
            print(f"[{team.upper()} STATE] -> {game_state}")

        pos, speed = move_player(anchor, game_state, team)
        gps_pos = apply_gps_noise(pos)

        message = {
            "team": team,
            "player_id": player_id,
            "role": role,
            "game_state": game_state,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "x_meters": float(gps_pos[0]),
            "y_meters": float(gps_pos[1]),
            "speed_mps": float(speed)
        }

        client.publish(TOPIC, json.dumps(message))
        time.sleep(SEND_INTERVAL)

# --------------------------------------------
# EXEC
# --------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python player_simulator.py <player_id 1-11> <home|away>")
        sys.exit(1)

    player_id = int(sys.argv[1])
    team = sys.argv[2]

    simulate_player(player_id, team)
