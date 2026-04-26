from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np
from rembg import remove
import io
import base64

app = FastAPI(title="Image Editor API")

# Enable CORS for your website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your domain
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

# =============== BACKGROUND REMOVAL ===============
@app.post("/remove-background")
async def remove_background(file: UploadFile = File(...)):
    """Remove background from image (AI-powered)"""
    try:
        unique_id = str(uuid.uuid4())
        input_path = f"temp/input_{unique_id}.png"
        output_path = f"temp/output_{unique_id}.png"
        
        # Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process with rembg
        with open(input_path, "rb") as i:
            input_data = i.read()
            output_data = remove(input_data)
        
        with open(output_path, "wb") as o:
            o.write(output_data)
        
        return FileResponse(output_path, media_type="image/png", filename="no-bg.png")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if os.path.exists(input_path): os.remove(input_path)

# =============== APPLY FILTERS ===============
@app.post("/apply-filter")
async def apply_filter(
    file: UploadFile = File(...),
    filter_type: str = Form(...)
):
    """Apply filters: grayscale, sepia, blur, sharpen, edge, emboss, contour"""
    try:
        unique_id = str(uuid.uuid4())
        input_path = f"temp/input_{unique_id}.png"
        output_path = f"temp/output_{unique_id}.png"
        
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        img = Image.open(input_path)
        
        # Convert to RGB if needed
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
    saturation: float = Form(0),
    sharpness: float = Form(0)
):
    """Adjust brightness, contrast, saturation, sharpness"""
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
        
        if sharpness != 0:
            factor = 1 + (sharpness / 100)
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(factor)
        
        img.convert('RGB').save(output_path, 'JPEG', quality=90)
        return FileResponse(output_path, media_type="image/jpeg", filename="adjusted.jpg")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)

# =============== CROP IMAGE ===============
@app.post("/crop-image")
async def crop_image(
    file: UploadFile = File(...),
    x: int = Form(...),
    y: int = Form(...),
    width: int = Form(...),
    height: int = Form(...)
):
    """Crop image to specified coordinates"""
    try:
        unique_id = str(uuid.uuid4())
        input_path = f"temp/input_{unique_id}.png"
        output_path = f"temp/output_{unique_id}.png"
        
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        img = Image.open(input_path)
        cropped = img.crop((x, y, x + width, y + height))
        cropped.save(output_path)
        
        return FileResponse(output_path, media_type="image/png", filename="cropped.png")
        
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

# =============== ADD TEXT TO IMAGE ===============
@app.post("/add-text")
async def add_text(
    file: UploadFile = File(...),
    text: str = Form(...),
    x: int = Form(...),
    y: int = Form(...),
    font_size: int = Form(30),
    color_r: int = Form(255),
    color_g: int = Form(255),
    color_b: int = Form(255)
):
    """Add text overlay to image"""
    try:
        from PIL import ImageDraw, ImageFont
        
        unique_id = str(uuid.uuid4())
        input_path = f"temp/input_{unique_id}.png"
        output_path = f"temp/output_{unique_id}.png"
        
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        img = Image.open(input_path).convert('RGBA')
        draw = ImageDraw.Draw(img)
        
        # Try to load a nice font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        draw.text((x, y), text, fill=(color_r, color_g, color_b, 255), font=font)
        
        img.save(output_path)
        return FileResponse(output_path, media_type="image/png", filename="text-added.png")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)

# =============== GET IMAGE INFO ===============
@app.post("/image-info")
async def get_image_info(file: UploadFile = File(...)):
    """Get image dimensions, format, size"""
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

# =============== COMPRESS IMAGE ===============
@app.post("/compress-image")
async def compress_image(
    file: UploadFile = File(...),
    quality: int = Form(85),
    max_width: int = Form(0),
    max_height: int = Form(0)
):
    """Compress image with quality setting"""
    try:
        unique_id = str(uuid.uuid4())
        input_path = f"temp/input_{unique_id}.png"
        output_path = f"temp/output_{unique_id}.jpg"
        
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        img = Image.open(input_path)
        
        # Resize if max dimensions provided
        if max_width > 0 and max_height > 0:
            img.thumbnail((max_width, max_height), Image.LANCZOS)
        
        img.convert('RGB').save(output_path, 'JPEG', quality=quality, optimize=True)
        
        original_size = os.path.getsize(input_path)
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
