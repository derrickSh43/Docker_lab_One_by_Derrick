from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import docker
import asyncio
import threading
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

docker_client = docker.from_env()
sessions = {}

def cleanup_session(websocket):
    session = sessions.get(websocket)
    if session:
        print("🧹 Cleaning up container...")
        try:
            session["socket"].close()
        except:
            pass
        try:
            session["container"].kill()
        except:
            pass
        del sessions[websocket]

@app.websocket("/ws/{lab_number}")
async def websocket_endpoint(websocket: WebSocket, lab_number: int):
    print(f"📡 WebSocket connection attempt for Lab {lab_number}")
    await websocket.accept()
    print("✅ WebSocket accepted")

    if websocket in sessions:
        print(f"🔴 Already connected with an active container, skipping creation.")
        return

    try:
        lab_image = f"lab{lab_number}-image"
        container = docker_client.containers.run(
            lab_image,
            command="/bin/bash",
            tty=True,
            stdin_open=True,
            detach=True,
            remove=True,
        )
        print(f"🟢 Started container: {container.short_id}")

        exec_id = docker_client.api.exec_create(container.id, "/bin/bash", tty=True, stdin=True)['Id']
        sock = docker_client.api.exec_start(exec_id, socket=True, tty=True)

        sessions[websocket] = {"container": container, "socket": sock}

        loop = asyncio.get_event_loop()

        def stream_output():
            try:
                while True:
                    output = sock._sock.recv(1024)
                    if output:
                        asyncio.run_coroutine_threadsafe(
                            websocket.send_text(output.decode(errors="ignore")),
                            loop
                        )
                    else:
                        print("⚠️ Container output stream closed")
                        break
            except Exception as e:
                print(f"❌ Error while streaming output: {e}")

        threading.Thread(target=stream_output, daemon=True).start()

        while True:
            data = await websocket.receive_text()
            if data.startswith("__VALIDATE__"):
                task_num = data.split(" ")[1] if len(data.split(" ")) > 1 else "1"
                print(f"🧪 Validating Lab {lab_number}, Task {task_num}")
                result = container.exec_run(f"/usr/local/bin/validate {task_num}")
                await websocket.send_text("\n🧪 Validation Result:\n" + result.output.decode())
            else:
                sock._sock.send(data.encode())

    except WebSocketDisconnect:
        cleanup_session(websocket)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        cleanup_session(websocket)

@app.get("/labs")
async def get_all_labs():
    lab_dir = "/app/labs"
    labs = []
    if os.path.exists(lab_dir):
        for folder in os.listdir(lab_dir):
            lab_num = folder.replace("Lab ", "")
            try:
                lab_num = int(lab_num)
                with open(f"{lab_dir}/Lab {lab_num}/lab{lab_num}.txt", "r") as f:
                    content = f.read()
                    lines = content.splitlines()
                    title = lines[0].strip()
                    tasks = []
                    current_task = {"title": "", "instructions": []}
                    
                    for line in lines[1:]:
                        if line.startswith("###"):
                            if current_task["title"]:
                                # Process instructions into list and paragraph
                                instructions = current_task["instructions"]
                                list_items = []
                                paragraph = []
                                in_list = False
                                for inst in instructions:
                                    if inst.strip() and not inst.startswith("Task:"):
                                        in_list = True
                                        list_items.append(inst.strip())
                                    elif inst.startswith("Task:"):
                                        in_list = False
                                        paragraph.append(inst[5:].strip())
                                    elif not inst.strip() and in_list:
                                        in_list = False
                                    elif not in_list and inst.strip():
                                        paragraph.append(inst.strip())
                                # Format as HTML
                                html_instructions = ""
                                if list_items:
                                    html_instructions += "<ul>" + "".join(f"<li>{item.replace('`', '<code>').replace('`', '</code>')}</li>" for item in list_items) + "</ul>"
                                if paragraph:
                                    html_instructions += "<p>" + " ".join(paragraph).replace("`", "<code>").replace("`", "</code>") + "</p>"
                                tasks.append({
                                    "title": current_task["title"].strip(),
                                    "instructions": html_instructions
                                })
                            current_task = {"title": line[3:].strip(), "instructions": []}
                        elif line.strip() or not current_task["instructions"]:  # Include blank lines after first non-blank
                            current_task["instructions"].append(line)
                    
                    if current_task["title"]:
                        instructions = current_task["instructions"]
                        list_items = []
                        paragraph = []
                        in_list = False
                        for inst in instructions:
                            if inst.strip() and not inst.startswith("Task:"):
                                in_list = True
                                list_items.append(inst.strip())
                            elif inst.startswith("Task:"):
                                in_list = False
                                paragraph.append(inst[5:].strip())
                            elif not inst.strip() and in_list:
                                in_list = False
                            elif not in_list and inst.strip():
                                paragraph.append(inst.strip())
                        html_instructions = ""
                        if list_items:
                            html_instructions += "<ul>" + "".join(f"<li>{item.replace('`', '<code>').replace('`', '</code>')}</li>" for item in list_items) + "</ul>"
                        if paragraph:
                            html_instructions += "<p>" + " ".join(paragraph).replace("`", "<code>").replace("`", "</code>") + "</p>"
                        tasks.append({
                            "title": current_task["title"].strip(),
                            "instructions": html_instructions
                        })

                    labs.append({
                        "number": lab_num,
                        "title": title,
                        "tasks": tasks
                    })
            except (ValueError, FileNotFoundError, IndexError) as e:
                print(f"⚠️ Error processing Lab {lab_num}: {e}")
                continue
    return {"labs": sorted(labs, key=lambda x: x["number"])}

@app.get("/lab/{lab_number}")
async def get_lab_instructions(lab_number: int):
    try:
        with open(f"/app/labs/Lab {lab_number}/lab{lab_number}.txt", "r") as f:
            return {f"lab{lab_number}_instructions": f.read()}
    except FileNotFoundError:
        return {"error": f"Lab {lab_number} instructions not found"}

app.mount("/", StaticFiles(directory="/app/static", html=True), name="static")