import subprocess
import sys
import time

NUM_PLAYERS = 11
processes = []

PYTHON = sys.executable  # python env

try:
    # Local team (home)
    for player_id in range(1, NUM_PLAYERS + 1):
        print(f"Player {player_id} (home) warming up")
        p = subprocess.Popen(
            [PYTHON, "player_simulator.py", str(player_id), "home"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        processes.append((f"home-{player_id}", p))
        time.sleep(0.05)

    # Away team (away)
    for player_id in range(1, NUM_PLAYERS + 1):
        print(f"Player {player_id} (away) warming up")
        p = subprocess.Popen(
            [PYTHON, "player_simulator.py", str(player_id), "away"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        processes.append((f"away-{player_id}", p))
        time.sleep(0.05)

    print(f"22 players on the field. Ctrl+C to stop.")

    # Logs
    while True:
        for player_id, p in processes:
            line = p.stdout.readline()
            if line:
                print(f"[{player_id}] {line.strip()}")
        time.sleep(0.01)

except KeyboardInterrupt:
    print("Stopping simulation…")
    for _, p in processes:
        p.terminate()
    print("Final whistle.")
