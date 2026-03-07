import os
import json
from datetime import datetime
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Pure Stone Vibes Marketplace")

# Directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = BASE_DIR
INQUIRIES_FILE = os.path.join(BASE_DIR, "inquiries.json")

# Ensure inquiries file exists
if not os.path.exists(INQUIRIES_FILE):
    with open(INQUIRIES_FILE, "w") as f:
        json.dump([], f)

# Mount namedpics specifically for image access
app.mount("/namedpics", StaticFiles(directory=os.path.join(STATIC_DIR, "namedpics")), name="namedpics")

# Serve main site files
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open(os.path.join(STATIC_DIR, "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/{page_name}.html", response_class=HTMLResponse)
async def read_page(page_name: str):
    file_path = os.path.join(STATIC_DIR, f"{page_name}.html")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>404 Not Found</h1>", status_code=404)

# Handle Inquiries
@app.post("/api/inquiry")
async def handle_inquiry(
    name: str = Form(...),
    email: str = Form(...),
    sculpture: str = Form(None),
    message: str = Form(None),
    bot_field: str = Form(None)
):
    # Honeypot check
    if bot_field:
        return {"status": "ignored", "reason": "bot detected"}

    inquiry_data = {
        "timestamp": datetime.now().isoformat(),
        "name": name,
        "email": email,
        "sculpture": sculpture,
        "message": message
    }

    # Save to local inquiries.json
    try:
        with open(INQUIRIES_FILE, "r+") as f:
            data = json.load(f)
            data.append(inquiry_data)
            f.seek(0)
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving inquiry: {e}")

    # Redirect to success page (matching previous Netlify behavior)
    return RedirectResponse(url="/inquiry.html?success=true", status_code=303)

# Serve remaining static assets at the end
app.mount("/", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
