import os
import sqlite3
import secrets
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Request, Form, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
import json
import logging

logging.basicConfig(level=logging.INFO, filename='scribe.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

from starlette.responses import FileResponse # Import FileResponse for type hinting
from fastapi.staticfiles import StaticFiles # Ensure StaticFiles is imported directly or as alias

# Custom StaticFiles class to add logging for each served file
class LoggedStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: dict) -> FileResponse:
        response = await super().get_response(path, scope)
        if response.status_code == 200:
            logger.info(f"Served static file: {path} (Status: {response.status_code})")
        elif response.status_code == 304:
            logger.info(f"Served static file (cached): {path} (Status: {response.status_code})")
        else:
            logger.warning(f"Failed to serve static file: {path} (Status: {response.status_code})")
        return response

app = FastAPI(title="Pure Stone Vibes | Production API", docs_url=None, redoc_url=None)

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

@app.get("/api/stats")
async def get_stats(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()

    # Total Inquiries
    cursor.execute("SELECT COUNT(*) FROM inquiries")
    total_inquiries = cursor.fetchone()[0]

    # Unique Sculptures Inquired
    cursor.execute("SELECT COUNT(DISTINCT sculpture) FROM inquiries WHERE sculpture IS NOT NULL")
    unique_sculptures_inquired = cursor.fetchone()[0]

    # Top 5 Most Inquired Sculptures
    cursor.execute("""
        SELECT sculpture, COUNT(*) as count
        FROM inquiries
        WHERE sculpture IS NOT NULL
        GROUP BY sculpture
        ORDER BY count DESC
        LIMIT 5
    """)
    top_sculptures = [dict(row) for row in cursor.fetchall()]

    # Recent Inquiries
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

@app.get("/docs", response_class=HTMLResponse, include_in_schema=False) # include_in_schema=False hides it from Swagger itself
async def custom_swagger_ui_html(request: Request):
    return templates.TemplateResponse(
        "custom_swagger_ui.html",
        {"request": request, "openapi_url": app.openapi_url}
    )

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
        # Log the file access using the same logic as LoggedStaticFiles
        logger.info(f"Served HTML page: {file_path} (Status: 200)")
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    logger.warning(f"HTML page not found: {file_path} (Status: 404)")
    return HTMLResponse(content="<h1>404 Not Found</h1>", status_code=404)

# Mount asset directories
app.mount("/namedpics", LoggedStaticFiles(directory=os.path.join(BASE_DIR, "namedpics")), name="namedpics")
# Mount the root directory last to serve remaining assets (css, js, etc.)

if __name__ == "__main__":
    import uvicorn
    import json
    uvicorn.run(app, host="0.0.0.0", port=8000)
