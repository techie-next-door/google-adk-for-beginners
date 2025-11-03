import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

from agent import root_agent

app = FastAPI()

session_service = InMemorySessionService()

async def create_new_session():
    new_session = await session_service.create_session(
        app_name="my_app",
        user_id="example_user",
        state={
            "apple": 5,
            "orange": 10
        }
    )

    print(f"--- Examining Session Properties ---")
    print(f"ID (`id`):                {new_session.id}")
    print(f"Application Name (`app_name`): {new_session.app_name}")
    print(f"User ID (`user_id`):         {new_session.user_id}")
    print(f"State (`state`):           {new_session.state}")
    print(f"Events (`events`):         {new_session.events}")
    print(f"Last Update (`last_update_time`): {new_session.last_update_time:.2f}")
    print(f"---------------------------------")

    return {"message":"Created New Session","id": new_session.id}

async def get_existing_session(session_id:str):
    print(session_id, "///////////")
    existing_session = await session_service.get_session(
        app_name="my_app",
        user_id="example_user",
        session_id=session_id
    )

    print(f"--- Examining Session Properties ---")
    print(f"ID (`id`):                {existing_session.id}")
    print(f"Application Name (`app_name`): {existing_session.app_name}")
    print(f"User ID (`user_id`):         {existing_session.user_id}")
    print(f"State (`state`):           {existing_session.state}")
    print(f"Events (`events`):         {existing_session.events}")
    print(f"Last Update (`last_update_time`): {existing_session.last_update_time:.2f}")
    print(f"---------------------------------")

    return {"message":"Fetched Existing Session","id": existing_session.id}

async def run_agent(session_id:str, query:str):
    print("Current Query:", query)
    runner = Runner(
        app_name="my_app",
        agent=root_agent,
        session_service=session_service
    )

    async for event in runner.run_async(user_id="example_user",session_id=session_id,new_message=types.Content
                                  (role="user",parts=[types.Part(text=query)])):
        print("EVENT AUTHOR:", event.author)
        print("EVENT ACTIONS:", event.actions)

        if event.is_final_response() and event and event.content.parts:
            final_response = event.content.parts[0].text
            print(final_response)
            yield final_response

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            data_dict = json.loads(data)
            session_id = data_dict.get("session_id")
            query = data_dict.get("query")
            if not session_id:
                session = await create_new_session()
                async for response in run_agent(session["id"],query):
                    await websocket.send_text(json.dumps({"session_id": session,"response": response}))
            elif session_id:
                session = await get_existing_session(session_id)
                async for response in run_agent(session["id"],query):
                    await websocket.send_text(json.dumps({"session_id": session,"response": response}))
            else:
                await websocket.send_text(json.dumps({"response": "No action performed"}))
    except WebSocketDisconnect:
        print("WebSocket disconnected")

@app.get("/")
async def root():
    return JSONResponse(content={"message": "FastAPI is running"})

# To run: uvicorn main:app --reload