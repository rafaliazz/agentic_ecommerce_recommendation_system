import os
import json
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"

SYSTEM_PROMPT = """
You are a product data extractor.

The input is OCR text from e-commerce screenshots.

Extract and return STRICT JSON:

{
  "product_name": "",
  "price": "",
  "rating": "",
}
RULES:- 
- Currency is IDR so look for Rp for the price, convert the price just to integer (no decimal/comma seperators)
- Look for lines where it's likely to be the product name 
If missing, return null.
No explanation. JSON only.
"""

def extract_product_data(ocr_text: str):
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0,
        google_api_key=os.getenv("GEMINI_API_KEY"),
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=ocr_text),
    ]

    response = llm.invoke(messages)
    raw = response.content.strip()

    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    return json.loads(raw)
