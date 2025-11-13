from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from aura import generate_aura_image, analyze_colors, map_rgb_to_aura
from uuid import uuid4

app = FastAPI(
    title="✨ Aura Polaroid Booth",
    description="Capture your magical aura in vintage Polaroid style",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup directories
TEMP = "temp"
OUTPUT = "output"
os.makedirs(TEMP, exist_ok=True)
os.makedirs(OUTPUT, exist_ok=True)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "✨ Aura Polaroid Booth API - Ready for Magic!"}

@app.post("/api/generate/")
async def generate_aura(
    file: UploadFile = File(...),
    filter_name: str = Form("none"),
    caption: str = Form("")
):
    try:
        unique_id = uuid4().hex
        input_path = os.path.join(TEMP, f"input_{unique_id}.jpg")
        
        # Read and save uploaded file
        contents = await file.read()
        with open(input_path, "wb") as f:
            f.write(contents)
        
        # Generate output filename and path
        output_filename = f"aura_{unique_id}.jpg"
        output_path = os.path.join(OUTPUT, output_filename)
        
        # Generate aura image and get color analysis
        final_path, color_analysis = generate_aura_image(
            input_path, 
            output_path, 
            filter_name=filter_name, 
            caption=caption
        )
        
        # Format color analysis
        color_cards = []
        for i, (aura_name, meaning) in enumerate(color_analysis):
            color_cards.append({
                "aura": aura_name,
                "meaning": meaning,
                "priority": i + 1
            })
        
        return JSONResponse({
            "success": True,
            "image": f"/api/result/{output_filename}",
            "analysis": color_cards,
            "message": "✨ Your magical aura has been revealed!"
        })
        
    except Exception as e:
        print(f"Backend error: {str(e)}")
        return JSONResponse({
            "success": False,
            "error": f"Magic failed: {str(e)}"
        }, status_code=500)

@app.get("/api/result/{filename}")
async def get_result(filename: str):
    path = os.path.join(OUTPUT, filename)
    if not os.path.exists(path):
        return JSONResponse({"error": "Aura not found"}, status_code=404)
    return FileResponse(path, media_type="image/jpeg", filename=filename)

@app.get("/api/health")
async def health_check():
    return {"status": "✨ Magical and ready!", "timestamp": __import__("datetime").datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)