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

# Import your exact mathematical function from decoder_app.py
from decoder_app import decode_difference

app = FastAPI(title="Watermark Decoder API")
DATABASE_URL = os.getenv("DATABASE_URL")

@app.post("/decode")
async def decode_watermark(
    multiplier: float = Form(20.0),  # Default amplification multiplier
    original: UploadFile = File(...),
    suspected: UploadFile = File(...)
):
    try:
        orig_path = f"/tmp/orig_{original.filename}"
        susp_path = f"/tmp/susp_{suspected.filename}"
        out_path = f"/tmp/extracted_{suspected.filename}"
        
        # Stream both uploaded files down to container temporary storage
        with open(orig_path, "wb") as f: f.write(await original.read())
        with open(susp_path, "wb") as f: f.write(await suspected.read())
        
        # Execute your pristine math function
        success = decode_difference(orig_path, susp_path, out_path, multiplier)
        
        if not success:
            raise Exception("decode_difference logic returned False or failed internally.")
            
        # Log the verification attempt to your PostgreSQL ledger
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO watermarked_records (source_filename, watermark_filename, density) VALUES (%s, %s, %s);",
            (f"CHECK_{suspected.filename}", f"VS_{original.filename}", multiplier)
        )
        conn.commit()
        cursor.close()
        conn.close()

        # Stream the visual delta back to your workstation browser window
        with open(out_path, "rb") as f:
            return StreamingResponse(io.BytesIO(f.read()), media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Headless Decoder Error: {str(e)}")
