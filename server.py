# =====================================================================
# Copyright (c) 2026 Jeremy McGehee (Klankton)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero General Public License for more details.
# =====================================================================
import os
import io
import psycopg2
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from PIL import Image, ImageOps

# Import the exact processing function from your original file
from watermark_app import process_image

app = FastAPI(title="Watermark Core Engine API")
DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watermarked_records (
            id SERIAL PRIMARY KEY,
            source_filename VARCHAR(255),
            watermark_filename VARCHAR(255),
            density REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/bake")
async def bake_watermark(
    density: float = Form(0.10),
    source: UploadFile = File(...),
    watermark: UploadFile = File(...)
):
    try:
        # Save temporary files inside the container to hand off to your original function
        src_path = f"/tmp/{source.filename}"
        wm_path = f"/tmp/{watermark.filename}"
        out_path = f"/tmp/out_{source.filename}"
        
        with open(src_path, "wb") as f: f.write(await source.read())
        with open(wm_path, "wb") as f: f.write(await watermark.read())
        
        # --- AUTOMATIC WATERMARK INVERSION ---
        # We invert the mask here so the frequency difference math can hide it perfectly
        from PIL import ImageOps
        with Image.open(wm_path) as wm_img:
            # Handle alpha transparency safely if your mask has it
            if wm_img.mode in ('RGBA', 'LA') or (wm_img.mode == 'P' and 'transparency' in wm_img.info):
                wm_img = wm_img.convert('RGB')
            inverted_wm = ImageOps.invert(wm_img)
            inverted_wm.save(wm_path)
        # -------------------------------------

        # Execute your untouched original desktop math script function
        success = process_image(src_path, wm_path, out_path, density)
        
        if not success:
            raise Exception("Processing function returned False")
            
        # Log the transaction securely into PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO watermarked_records (source_filename, watermark_filename, density) VALUES (%s, %s, %s);",
            (source.filename, watermark.filename, density)
        )
        conn.commit()
        cursor.close()
        conn.close()

        # Stream the finalized file back
        with open(out_path, "rb") as f:
            return StreamingResponse(io.BytesIO(f.read()), media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Core Processing Error: {str(e)}")
