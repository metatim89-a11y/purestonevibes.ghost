import os
import sqlite3
import secrets
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Request, Form, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel

app = FastAPI(title="Pure Stone Vibes | Production API")

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

# Initialize SQLite Table
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

# --- API Endpoints ---

@app.get("/api/inventory")
async def get_inventory():
    inventory_path = os.path.join(BASE_DIR, "inventory_final.json")
    if not os.path.exists(inventory_path):
        return JSONResponse(status_code=404, content={"error": "Inventory not found"})
    with open(inventory_path, "r", encoding="utf-8") as f:
        return json.load(f)

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
        # Redirect to success page (standard for static forms)
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

# --- Static File Serving ---

# Serve the main HTML pages directly from root
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open(os.path.join(BASE_DIR, "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Explicit routes for key pages to ensure they resolve without .html if needed
@app.get("/{page_name}.html", response_class=HTMLResponse)
async def read_page(page_name: str):
    file_path = os.path.join(BASE_DIR, f"{page_name}.html")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>404 Not Found</h1>", status_code=404)

# Mount asset directories
app.mount("/namedpics", StaticFiles(directory=os.path.join(BASE_DIR, "namedpics")), name="namedpics")
# Mount the root directory last to serve remaining assets (css, js, etc.)
app.mount("/", StaticFiles(directory=BASE_DIR), name="root")

if __name__ == "__main__":
    import uvicorn
    import json
    uvicorn.run(app, host="0.0.0.0", port=8000)
