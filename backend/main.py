from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import os
from aura import generate_aura_image, analyze_colors, map_rgb_to_aura
from uuid import uuid4

app = FastAPI(title="Aura Polaroid Booth API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP = "temp"
os.makedirs(TEMP, exist_ok=True)

@app.post("/api/generate/")
async def generate(
    file: UploadFile = File(...),
    filter_name: str = Form("none"),
    caption: str = Form("")
):
    unique = uuid4().hex
    in_path = os.path.join(TEMP, f"input_{unique}.jpg")
    contents = await file.read()
    with open(in_path, "wb") as f:
        f.write(contents)

    out_filename = f"aura_{unique}.jpg"
    out_path = os.path.join(TEMP, out_filename)
    generate_aura_image(in_path, out_path, filter_name=filter_name, caption=caption)

    primary = analyze_colors(in_path, k=3)
    color_cards = []
    for rgb in primary:
        name, meaning = map_rgb_to_aura(rgb)
        color_cards.append({"hex": rgb, "aura": name, "meaning": meaning})

    return JSONResponse({
        "image": f"/api/result/{out_filename}",
        "analysis": color_cards
    })

@app.get("/api/result/{filename}")
async def get_result(filename: str):
    path = os.path.join(TEMP, filename)
    if not os.path.exists(path):
        return JSONResponse({"error": "not found"}, status_code=404)
    return FileResponse(path, media_type="image/jpeg")