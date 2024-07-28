#! /usr/bin/env python

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from assistant import lg_agent
from comfyuiapi import *
import piperengine as engine
import asyncio
import random
import uvicorn
import base64
import json
import signal
import sys

app = FastAPI()

workflowapi = "workflow_api.json"
engine.load('en_GB-alba-medium.onnx')
selected_device_index = 0  # Set your desired device index here

PUNCTUATION = [".", "?", "!", ":", ";", "*", "-", "**"]

async def play_audio_on_device(text, device_index=0):
    engine.say(text)

async def speak(content, device_index=0):
    await play_audio_on_device(content, device_index)

websocket_connections = {}

def setup_connection():
    try:
        ws, server_address, client_id = open_websocket_connection()
        workflow = load_workflow(workflowapi)
        prompt = json.loads(workflow)
        return ws, server_address, client_id, prompt
    except (ConnectionError, TimeoutError) as e:
        print(f"Failed to connect to the server: {e}")
        return None, None, None, None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None, None, None, None

ws, server_address, client_id, prompt = setup_connection()


origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return open("static/index.html", "r").read()

@app.get("/book.png")
async def get_image():
    return FileResponse("static/book.png", media_type="image/png")

@app.websocket("/ws/{endpoint}")
async def websocket_endpoint(websocket: WebSocket, endpoint: str):
    await websocket.accept()
    websocket_connections[endpoint] = websocket
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    except WebSocketDisconnect:
        del websocket_connections[endpoint]
    finally:
        await websocket.close()

async def send_image_to_endpoint(endpoint: str, data: bytes):
    if endpoint in websocket_connections:
        websocket = websocket_connections[endpoint]
        try:
            await websocket.send_bytes(data)
        except Exception as e:
            print(f"Error sending data to {endpoint}: {e}")


async def reconnect_websocket(websocket: WebSocket):
    while True:
        try:
            await websocket_chat_endpoint(websocket)
            break
        except WebSocketDisconnect:
            print("Reconnecting WebSocket...")
            await asyncio.sleep(2)  # Wait before attempting to reconnect

async def process_prompt(sentence, prompt, client_id, server_address, websocket):
    positive_prompt = sentence.strip()
    id_to_class_type = {id: details['class_type'] for id, details in prompt.items()}
    k_sampler_id = next(key for key, value in id_to_class_type.items() if value == 'KSampler')
    k_sampler = prompt[k_sampler_id]
    k_sampler['inputs']['seed'] = generate_random_15_digit_number()
    positive_input_id = k_sampler['inputs']['positive'][0]
    prompt[positive_input_id]['inputs']['text'] = positive_prompt
    prompt_id = queue_prompt(prompt, client_id, server_address)['prompt_id']
    track_progress(prompt, ws, prompt_id)
    images = get_images(prompt_id, server_address, False)
    image_data = get_image_data(images)
    if image_data:
        await send_image_to_endpoint("image", image_data)
        print("image sent\r\n")
    await speak(sentence, selected_device_index)

@app.websocket("/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    is_open = True
    try:
        async for message in websocket.iter_text():
            try:
                word = ""
                sentence = ""
                async for event in lg_agent.astream_events(
                        {"messages": ("user", message)}, config={"configurable": {"thread_id": 1}}, version="v1"):
                    kind = event["event"]
                    if kind == "on_chat_model_stream":
                        token = event["data"]["chunk"].content
                        if token:
                            if token.startswith(" "):
                                if word:
                                    sentence += word
                                word = token
                            else:
                                word += token
                            if any(token.endswith(punct) for punct in PUNCTUATION):
                                sentence += word
                                print(sentence.strip())
                                await websocket.send_text(sentence.strip())
                                await process_prompt(sentence, prompt, client_id, server_address, websocket)
                                sentence = ""
                                word = ""
                if word:
                    sentence += word
                if sentence and is_open:
                    await websocket.send_text(sentence.strip())
                    print(sentence.strip())
                    await process_prompt(sentence, prompt, client_id, server_address, websocket)
            except Exception as e:
                if is_open:
                    try:
                        await websocket.send_text(f"Error: {e}")
                    except RuntimeError as re:
                        print(f"Error sending error message to WebSocket: {re}")
                        is_open = False
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        if is_open:
            try:
                await websocket.send_text(f"Error: {e}")
            except RuntimeError as re:
                print(f"Error sending error message to WebSocket: {re}")
    finally:
        if is_open:
            await websocket.close()



# Signal handler for shutdown
def signal_handler(signal, frame):
    print("Gracefully shutting down...")
    for ws in websocket_connections.values():
        asyncio.create_task(ws.close())
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
