from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import io

app = FastAPI(title="Image Editor API")

# Enable CORS for your website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create temp directory
os.makedirs("temp", exist_ok=True)

# =============== HEALTH CHECK ===============
@app.get("/")
def root():
    return {"message": "Image Editor API is running!", "status": "active"}

@app.get("/health")
def health():
    return {"status": "ok"}

# =============== APPLY FILTERS ===============
@app.post("/apply-filter")
async def apply_filter(
    file: UploadFile = File(...),
    filter_type: str = Form(...)
):
    """Apply filters: grayscale, sepia, blur, sharpen, edge, emboss, contour, invert"""
    try:
        unique_id = str(uuid.uuid4())
        input_path = f"temp/input_{unique_id}.png"
        output_path = f"temp/output_{unique_id}.png"
        
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        img = Image.open(input_path)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        if filter_type == "grayscale":
            img = ImageOps.grayscale(img)
            img = img.convert('RGB')
        
        elif filter_type == "sepia":
            img = ImageOps.grayscale(img)
            img = img.convert('RGB')
            width, height = img.size
            pixels = img.load()
            for py in range(height):
                for px in range(width):
                    r, g, b = img.getpixel((px, py))
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    pixels[px, py] = (min(255, tr), min(255, tg), min(255, tb))
        
        elif filter_type == "blur":
            img = img.filter(ImageFilter.BLUR)
        
        elif filter_type == "sharpen":
            img = img.filter(ImageFilter.SHARPEN)
        
        elif filter_type == "edge":
            img = img.filter(ImageFilter.FIND_EDGES)
        
        elif filter_type == "emboss":
            img = img.filter(ImageFilter.EMBOSS)
        
        elif filter_type == "contour":
            img = img.filter(ImageFilter.CONTOUR)
        
        elif filter_type == "invert":
            img = ImageOps.invert(img)
        
        img.save(output_path)
        return FileResponse(output_path, media_type="image/png", filename=f"{filter_type}.png")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)

# =============== ADJUST IMAGE ===============
@app.post("/adjust-image")
async def adjust_image(
    file: UploadFile = File(...),
    brightness: float = Form(0),
    contrast: float = Form(0),
    saturation: float = Form(0)
):
    """Adjust brightness, contrast, saturation"""
    try:
        unique_id = str(uuid.uuid4())
        input_path = f"temp/input_{unique_id}.png"
        output_path = f"temp/output_{unique_id}.jpg"
        
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        img = Image.open(input_path)
        
        if brightness != 0:
            factor = 1 + (brightness / 100)
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(factor)
        
        if contrast != 0:
            factor = 1 + (contrast / 100)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(factor)
        
        if saturation != 0:
            factor = 1 + (saturation / 100)
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(factor)
        
        img.convert('RGB').save(output_path, 'JPEG', quality=90)
        return FileResponse(output_path, media_type="image/jpeg", filename="adjusted.jpg")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)

# =============== RESIZE IMAGE ===============
@app.post("/resize-image")
async def resize_image(
    file: UploadFile = File(...),
    width: int = Form(...),
    height: int = Form(...),
    maintain_ratio: bool = Form(True)
):
    """Resize image to specified dimensions"""
    try:
        unique_id = str(uuid.uuid4())
        input_path = f"temp/input_{unique_id}.png"
        output_path = f"temp/output_{unique_id}.png"
        
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        img = Image.open(input_path)
        
        if maintain_ratio:
            img.thumbnail((width, height), Image.LANCZOS)
        else:
            img = img.resize((width, height), Image.LANCZOS)
        
        img.save(output_path)
        return FileResponse(output_path, media_type="image/png", filename="resized.png")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)

# =============== ROTATE / FLIP IMAGE ===============
@app.post("/transform-image")
async def transform_image(
    file: UploadFile = File(...),
    action: str = Form(...)
):
    """Actions: rotate_90, rotate_180, rotate_270, flip_h, flip_v"""
    try:
        unique_id = str(uuid.uuid4())
        input_path = f"temp/input_{unique_id}.png"
        output_path = f"temp/output_{unique_id}.png"
        
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        img = Image.open(input_path)
        
        if action == "rotate_90":
            img = img.rotate(90, expand=True)
        elif action == "rotate_180":
            img = img.rotate(180, expand=True)
        elif action == "rotate_270":
            img = img.rotate(270, expand=True)
        elif action == "flip_h":
            img = ImageOps.mirror(img)
        elif action == "flip_v":
            img = ImageOps.flip(img)
        
        img.save(output_path)
        return FileResponse(output_path, media_type="image/png", filename=f"{action}.png")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)

# =============== COMPRESS IMAGE ===============
@app.post("/compress-image")
async def compress_image(
    file: UploadFile = File(...),
    quality: int = Form(85)
):
    """Compress image with quality setting"""
    try:
        unique_id = str(uuid.uuid4())
        input_path = f"temp/input_{unique_id}.png"
        output_path = f"temp/output_{unique_id}.jpg"
        
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        img = Image.open(input_path)
        
        original_size = os.path.getsize(input_path)
        img.convert('RGB').save(output_path, 'JPEG', quality=quality, optimize=True)
        compressed_size = os.path.getsize(output_path)
        
        return FileResponse(
            output_path, 
            media_type="image/jpeg", 
            filename="compressed.jpg",
            headers={
                "X-Original-Size": str(original_size),
                "X-Compressed-Size": str(compressed_size),
                "X-Saved-Percent": str(round((1 - compressed_size/original_size) * 100, 1))
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)

# =============== GET IMAGE INFO ===============
@app.post("/image-info")
async def get_image_info(file: UploadFile = File(...)):
    """Get image dimensions and size"""
    try:
        unique_id = str(uuid.uuid4())
        input_path = f"temp/input_{unique_id}.png"
        
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        img = Image.open(input_path)
        size = os.path.getsize(input_path)
        
        return JSONResponse({
            "width": img.width,
            "height": img.height,
            "format": img.format,
            "mode": img.mode,
            "size_bytes": size,
            "size_kb": round(size / 1024, 2)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)
