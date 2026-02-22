from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from PIL import Image
import shutil
import uuid
import os
import json

from backend.easyocr import EasyOCR
from backend.text_evaluator import extract_product_data
from backend.recommender import recommend_cheaper


app = FastAPI(
    title="E-Commerce Screenshot Analyzer API",
    description="Upload a screenshot → OCR → Extract product → Find cheaper alternatives",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("temp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# -------------------------
# Health Check
# -------------------------

@app.get("/")
def root():
    return {"message": "E-Commerce OCR API is running"}


# -------------------------
# Main Analyze Endpoint
# -------------------------

import traceback

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    try:
        print("STEP 1: file received")

        # Save file
        temp_path = UPLOAD_DIR / "debug.png"
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print("STEP 2: file saved")

        from PIL import Image
        image = Image.open(temp_path)
        width, height = image.size
        layout_type = "mobile" if height > width else "pc"

        print("STEP 3: layout detected")

        ocr_engine = EasyOCR(languages=["en", "id"])

        print("STEP 4: OCR engine created")

        # boxes = ocr_engine.get_relevant_boxes_mobile(temp_path)

        # ocr_text = "\n".join([b["text"] for b in boxes])

        boxes = ocr_engine.run(temp_path)
        print(boxes["text"])
        ocr_text = boxes["text"]

        print("STEP 5: Extracting product data")

        product_data = extract_product_data(ocr_text)

        print("STEP 6: Extraction finished")

        print(product_data)

        print("STEP 7: Recommending cheaper products")
        cheaper_products = recommend_cheaper(product_data)
        print("STEP 8: Recommendation finished")

        try:
            cheaper_products = json.loads(json.dumps(cheaper_products))
        except Exception:
            print("Could not JSON-serialize cheaper_products")
            cheaper_products = str(cheaper_products)
        return {
            "layout_type": layout_type,
            "ocr_text": ocr_text,
            "product_data": product_data,
            "cheaper_products": cheaper_products
        }

    except Exception as e:
        print("ERROR OCCURRED:")
        traceback.print_exc()
        return {"error": str(e)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))