# football-tracking-rt
An end-to-end project to track football players' position on the pitch. The system simulates 22 players (home &amp; away) with realistic roles and behaviors (formations, game states like attack, defend, press), streams their positions in real time, and visualizes team structure dynamically.

Currently, the system runs locally using Docker.

<img width="1351" height="633" alt="Captura de pantalla 2025-12-28 144302" src="https://github.com/user-attachments/assets/de8dac2d-96ed-4171-8928-1d44e6cc4fc2" />

# How to run 
It is mandatory to create the virtual environment to execute the py files. The requirements are listed in the requirements file.
The user can run the steps sequentially. It is important to keep the order.

## Run the positioning simulator
```
cd ./simulator/
python run_all_simulators.py
```
## MQTT to Kafka
```
python .\mqtt_to_kafka\mqtt_to_kafka.py
```
## DB saving
The next point is optional. It allows to storage historical data and perform an offline analysis.
The table must be created through Docker.
```
cd .\football-tracking-rt\docker
docker exec -it timescaledb psql -U postgres -d football
SELECT * FROM player_positions ORDER BY timestamp DESC LIMIT 10;
CREATE TABLE player_positions (
    team TEXT NOT NULL,
    player_id INT NOT NULL,
    role TEXT NOT NULL,
    game_state TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    x_meters DOUBLE PRECISION NOT NULL,
    y_meters DOUBLE PRECISION NOT NULL,
    speed_mps DOUBLE PRECISION,
    PRIMARY KEY (player_id, timestamp)
);
SELECT create_hypertable('player_positions', 'timestamp');
```
Execute the Python script.
```
python .\consumer\kafka_to_timescaledb.py
```
## API deployment 
```
cd ./api/
uvicorn realtime_api:app --reload --port=8001
```
## Draw the stadium
A local website will be launched drawing the players on the field.
```
cd ./frontend/
start index.html
```
