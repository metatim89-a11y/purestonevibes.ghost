import os
import sqlite3
import secrets
import json
import logging
import asyncio
import uuid # Added for UUID generation
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, Request, Form, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.responses import FileResponse as StarletteFileResponse
import psutil

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, filename='scribe.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- WebSocket Connection Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Send immediate health check on connection
        await self.send_health_status(websocket)
        await self.broadcast_session_count()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            asyncio.create_task(self.broadcast_session_count())

    async def send_health_status(self, websocket: WebSocket):
        # Verify DB and Inventory
        db_status = "OK"
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("SELECT 1")
            conn.close()
        except:
            db_status = "ERROR"
        
        inventory_status = "OK" if os.path.exists(os.path.join(BASE_DIR, "inventory_final.json")) else "MISSING"

        await websocket.send_text(json.dumps({
            "type": "system_health",
            "db": db_status,
            "inventory": inventory_status,
            "version": "v1.0.4-PROD",
            "uptime": "Active"
        }))

    async def broadcast_session_count(self):
        count = len(self.active_connections)
        await self.broadcast(json.dumps({
            "type": "session_update",
            "count": count
        }))

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # Handle stale connections
                pass

manager = ConnectionManager()

# --- App Initialization ---
app = FastAPI(title="Pure Stone Vibes | Production API", docs_url=None, redoc_url=None)
templates = Jinja2Templates(directory="templates")

# --- Custom StaticFiles with Logging ---
class LoggedStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: dict) -> StarletteFileResponse:
        response = await super().get_response(path, scope)
        if response.status_code == 200:
            logger.info(f"Served static file: {path} (Status: {response.status_code})")
        elif response.status_code == 304:
            logger.info(f"Served static file (cached): {path} (Status: {response.status_code})")
        else:
            logger.warning(f"Failed to serve static file: {path} (Status: {response.status_code})")
        return response

# --- Error Handling Middleware ---
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        error_msg = f"ERROR: {str(e)} | Path: {request.url.path} | Method: {request.method}"
        logger.error(error_msg)
        # Broadcast the error via WebSocket
        asyncio.create_task(manager.broadcast(json.dumps({
            "type": "error",
            "message": str(e),
            "path": request.url.path,
            "method": request.method,
            "timestamp": datetime.now().isoformat()
        })))
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "details": str(e)}
        )

# --- Configuration & Database ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "inquiries.db")
SECRET_TOKEN = "admin-token-v1" # In production, use environment variables

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                sculpture TEXT,
                sculpture_id TEXT,
                message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
init_db()

# --- Models ---
class LoginRequest(BaseModel):
    username: str
    password: str

# --- Security Helper ---
def verify_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = auth_header.split(" ")[1]
    if token != SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    return token

# --- WebSocket Endpoint ---
@app.websocket("/ws/errors")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    logger.info("📡 [SYSTEM] Dashboard client connected via WebSocket.")
    print("✅ Dashboard Connected.")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("📡 [SYSTEM] Dashboard client disconnected.")

# --- API Endpoints ---

@app.get("/api/trigger_error")
async def trigger_error():
    """Manually trigger an error for testing the dashboard."""
    raise ValueError("Manual test error triggered for dashboard validation!")

@app.get("/api/inventory")
async def get_inventory():
    inventory_path = os.path.join(BASE_DIR, "inventory_final.json")
    if not os.path.exists(inventory_path):
        return JSONResponse(status_code=404, content={"error": "Inventory not found"})
    with open(inventory_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/inventory/{item_id}")
async def get_inventory_item(item_id: str):
    inventory_path = os.path.join(BASE_DIR, "inventory_final.json")
    if not os.path.exists(inventory_path):
        raise HTTPException(status_code=404, detail="Inventory not found")
    with open(inventory_path, "r", encoding="utf-8") as f:
        inventory = json.load(f)
    
    for item in inventory:
        if item.get("id") == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.post("/api/inventory", status_code=status.HTTP_201_CREATED)
async def add_inventory_item(item: dict, token: str = Depends(verify_token)):
    inventory_path = os.path.join(BASE_DIR, "inventory_final.json")
    if not os.path.exists(inventory_path):
        return JSONResponse(status_code=404, content={"error": "Inventory not found"})
    
    with open(inventory_path, "r+", encoding="utf-8") as f:
        inventory = json.load(f)
        item["id"] = str(uuid.uuid4()) # Assign a unique ID
        inventory.append(item)
        f.seek(0) # Rewind to beginning
        json.dump(inventory, f, indent=4)
        f.truncate() # Truncate remaining content
    return {"message": "Item added successfully", "item_id": item["id"]}

@app.put("/api/inventory/{item_id}")
async def update_inventory_item(item_id: str, updated_item: dict, token: str = Depends(verify_token)):
    inventory_path = os.path.join(BASE_DIR, "inventory_final.json")
    if not os.path.exists(inventory_path):
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    with open(inventory_path, "r+", encoding="utf-8") as f:
        inventory = json.load(f)
        found = False
        for i, item in enumerate(inventory):
            if item.get("id") == item_id:
                inventory[i] = {**item, **updated_item} # Merge updates
                found = True
                break
        
        if not found:
            raise HTTPException(status_code=404, detail="Item not found")
        
        f.seek(0)
        json.dump(inventory, f, indent=4)
        f.truncate()
    return {"message": "Item updated successfully"}

@app.delete("/api/inventory/{item_id}")
async def delete_inventory_item(item_id: str, token: str = Depends(verify_token)):
    inventory_path = os.path.join(BASE_DIR, "inventory_final.json")
    if not os.path.exists(inventory_path):
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    with open(inventory_path, "r+", encoding="utf-8") as f:
        inventory = json.load(f)
        initial_len = len(inventory)
        inventory = [item for item in inventory if item.get("id") != item_id]
        
        if len(inventory) == initial_len:
            raise HTTPException(status_code=404, detail="Item not found")
        
        f.seek(0)
        json.dump(inventory, f, indent=4)
        f.truncate()
    return {"message": "Item deleted successfully"}

@app.post("/api/login")
async def login(data: LoginRequest):
    if (data.username in ["tester1", "tester2"]) and data.password == "admin":
        print(f"Login Successful: {data.username}")
        return {"success": True, "username": data.username, "token": SECRET_TOKEN}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/inquiry")
async def create_inquiry(
    name: str = Form(...),
    email: str = Form(...),
    sculpture: Optional[str] = Form(None),
    sculpture_id: Optional[str] = Form(None),
    message: Optional[str] = Form(None),
    db: sqlite3.Connection = Depends(get_db)
):
    try:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO inquiries (name, email, sculpture, sculpture_id, message) VALUES (?, ?, ?, ?, ?)",
            (name, email, sculpture, sculpture_id, message)
        )
        db.commit()
        print(f"Inquiry Saved: {name} for {sculpture} (ID: {sculpture_id})")
        return RedirectResponse(url="/inquiry.html?success=true", status_code=303)
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save inquiry")

@app.get("/api/inquiries")
async def get_inquiries(token: str = Depends(verify_token), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM inquiries ORDER BY created_at DESC")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.get("/api/stats")
async def get_stats(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM inquiries")
    total_inquiries = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT sculpture) FROM inquiries WHERE sculpture IS NOT NULL")
    unique_sculptures_inquired = cursor.fetchone()[0]
    cursor.execute("""
        SELECT sculpture, COUNT(*) as count
        FROM inquiries
        WHERE sculpture IS NOT NULL
        GROUP BY sculpture
        ORDER BY count DESC
        LIMIT 5
    """)
    top_sculptures = [dict(row) for row in cursor.fetchall()]
    cursor.execute("""
        SELECT name, email, sculpture, created_at
        FROM inquiries
        ORDER BY created_at DESC
        LIMIT 10
    """)
    recent_inquiries = [dict(row) for row in cursor.fetchall()]
    return {
        "total_inquiries": total_inquiries,
        "unique_sculptures_inquired": unique_sculptures_inquired,
        "top_sculptures": top_sculptures,
        "recent_inquiries": recent_inquiries
    }

@app.get("/api/system_metrics")
async def get_system_metrics():
    # CPU Usage
    cpu_percent = psutil.cpu_percent(interval=1) # Blocking, waits for 1 second
    cpu_count = psutil.cpu_count(logical=True)

    # Memory Usage
    mem_info = psutil.virtual_memory()
    mem_total = round(mem_info.total / (1024 ** 3), 2) # GB
    mem_used = round(mem_info.used / (1024 ** 3), 2)  # GB
    mem_percent = mem_info.percent

    return {
        "cpu_percent": cpu_percent,
        "cpu_count": cpu_count,
        "memory_total_gb": mem_total,
        "memory_used_gb": mem_used,
        "memory_percent": mem_percent,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/logs/{log_file_name}", response_class=PlainTextResponse)
async def get_logs(log_file_name: str, token: str = Depends(verify_token)):
    if log_file_name not in ["scribe.log", "startuplog.log"]:
        raise HTTPException(status_code=404, detail="Log file not found.")
    
    log_path = os.path.join(BASE_DIR, log_file_name)
    if not os.path.exists(log_path):
        raise HTTPException(status_code=404, detail="Log file does not exist.")
    
    with open(log_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/version")
async def get_version():
    version_path = os.path.join(BASE_DIR, "version.json")
    if not os.path.exists(version_path):
        return {"version": "N/A", "message": "version.json not found"}
    with open(version_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.post("/api/version")
async def update_version(new_version: dict, token: str = Depends(verify_token)):
    version_path = os.path.join(BASE_DIR, "version.json")
    with open(version_path, "w", encoding="utf-8") as f:
        json.dump(new_version, f, indent=4)
    return {"message": "Version updated successfully", "new_version": new_version}

@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
async def custom_swagger_ui_html(request: Request):
    return templates.TemplateResponse(
        "custom_swagger_ui.html",
        {"request": request, "openapi_url": app.openapi_url}
    )

# --- Static File Serving ---

@app.get("/landing", response_class=FileResponse)
async def read_index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

@app.get("/debug", response_class=FileResponse)
async def read_debug():
    return FileResponse(os.path.join(BASE_DIR, "debug.html"))

@app.get("/splat", response_class=FileResponse)
async def read_splat():
    return FileResponse(os.path.join(BASE_DIR, "dashboard.html"))

app.mount("/namedpics", LoggedStaticFiles(directory=os.path.join(BASE_DIR, "namedpics")), name="namedpics")
app.mount("/", LoggedStaticFiles(directory=BASE_DIR, html=True), name="root")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
