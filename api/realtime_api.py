import json
from fastapi import FastAPI, WebSocket
from aiokafka import AIOKafkaConsumer
import asyncio
import uvicorn

app = FastAPI()

async def get_consumer():
    consumer = AIOKafkaConsumer(
        "players_topic",
        bootstrap_servers="localhost:9092",
        group_id="ws_group",
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )
    await consumer.start()
    return consumer

@app.websocket("/ws/positions")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connected successfully")

    consumer = await get_consumer()

    try:
        async for msg in consumer:
            await websocket.send_json(msg.value)
            await asyncio.sleep(0.02)  # 50fps

    except Exception as e:
        print("WebSocket error:", e)

    finally:
        await consumer.stop()

if __name__ == "__main__":
    uvicorn.run("realtime_api:app", host="0.0.0.0", port=8001, reload=True)
