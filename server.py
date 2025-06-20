# By Star Dream
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import shutil
import os
import uuid
from wand.image import Image
import uvicorn

app = FastAPI()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/convert")
async def convert(
    file: UploadFile = File(...),
    format: str = Form(...),
    quality: int = Form(None)
):
    SUPPORTED = {"png", "jpeg", "webp", "avif", "tiff", "gif"}
    target = format.lower()
    if target not in SUPPORTED:
        raise HTTPException(status_code=400, detail=f"不支持的格式: {target}")

    uid = str(uuid.uuid4())
    in_path = os.path.join(UPLOAD_DIR, f"{uid}_{file.filename}")
    out_name = f"{uid}.{target}"
    out_path = os.path.join(OUTPUT_DIR, out_name)

    with open(in_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        with Image(filename=in_path) as img:
            img.format = target.upper()
            if target == "webp" and quality is not None:
                img.compression_quality = quality
            img.save(filename=out_path)
    except Exception as e:
        os.remove(in_path)
        raise HTTPException(status_code=500, detail=f"转换失败: {e}")

    try:
        os.remove(in_path)
    except:
        pass

    return FileResponse(
        out_path,
        media_type=f"image/{target}",
        filename=out_name
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9998)
