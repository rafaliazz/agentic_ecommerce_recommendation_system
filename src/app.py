import streamlit as st
import json
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image

from backend.easyocr import EasyOCR
from backend.text_evaluator import extract_product_data
from backend.recommender import recommend_cheaper

load_dotenv()

def detect_layout(width, height):
    return "mobile" if height > width else "pc"

st.set_page_config(page_title="E-Commerce OCR Recommender", layout="wide")

st.title("🛒 AI E-Commerce Screenshot Analyzer")

uploaded_file = st.file_uploader("Upload Screenshot", type=["png", "jpg", "jpeg"])

# Initialize session state
if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = None

if "product_data" not in st.session_state:
    st.session_state.product_data = None

if "cheaper_products" not in st.session_state:
    st.session_state.cheaper_products = None


if uploaded_file:

    image = Image.open(uploaded_file)
    width, height = image.size
    layout_type = detect_layout(width, height)

    temp_path = Path("temp_upload.png")
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.image(image, caption="Uploaded Screenshot", use_container_width=True)

    # -------------------------
    # OCR (auto-run once)
    # -------------------------
    if st.session_state.ocr_text is None:
        with st.spinner("Running OCR..."):
            ocr_engine = EasyOCR(languages=["en", "id"])

            if layout_type == "mobile":
                boxes = ocr_engine.get_relevant_boxes_mobile(temp_path)
            else:
                boxes = ocr_engine.get_relevant_boxes_pc(temp_path)

            st.session_state.ocr_text = "\n".join([b["text"] for b in boxes])

    st.subheader("📄 OCR Text")
    st.text_area("Detected Text", st.session_state.ocr_text, height=200)

    # -------------------------
    # Extract Product Data
    # -------------------------
    if st.button("Extract Product Info"):
        with st.spinner("Extracting product data..."):
            st.session_state.product_data = extract_product_data(
                st.session_state.ocr_text
            )

    if st.session_state.product_data:
        st.subheader("📦 Extracted Product Data")
        st.json(st.session_state.product_data)

        # -------------------------
        # Recommend Cheaper
        # -------------------------
        if st.button("Find Cheaper Alternatives"):
            with st.spinner("Searching cheaper alternatives..."):
                st.session_state.cheaper_products = recommend_cheaper(
                    st.session_state.product_data
                )
        print(st.session_state.cheaper_products)
    if st.session_state.cheaper_products is not None:

        st.subheader("💰 Cheaper Alternatives")

        st.write("Raw Response:")
        st.write(st.session_state.cheaper_products)

        try:
            # If it's already a list/dict, don't parse
            if isinstance(st.session_state.cheaper_products, str):
                parsed = json.loads(st.session_state.cheaper_products)
            else:
                parsed = st.session_state.cheaper_products
            products = []

            # Case 1: parsed is already a list of product dicts
            if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):

                # If it's Gemini-style wrapper
                if "text" in parsed[0]:
                    try:
                        inner = parsed[0]["text"]

                        # If inner is string → parse it
                        if isinstance(inner, str):
                            products = json.loads(inner)
                        else:
                            products = inner

                    except Exception:
                        products = []
                else:
                    # It's already actual products
                    products = parsed

            # Case 2: parsed is a string (raw JSON)
            elif isinstance(parsed, str):
                try:
                    products = json.loads(parsed)
                except:
                    products = []

            # -------------------------
            # Now safely render
            # -------------------------

            for item in products:
                if not isinstance(item, dict):
                    continue

                with st.container():
                    st.markdown(f"### {item.get('name', 'Unknown')}")

                    price = item.get("price_idr", 0)
                    try:
                        price = int(price)
                    except:
                        price = 0

                    st.write(f"💵 Price: Rp {price:,}")
                    st.write(f"🏪 Store: {item.get('store', 'Unknown')}")
                    st.markdown(f"[🔗 View Product]({item.get('product_url', '#')})")
                    st.divider()

        except Exception as e:
            st.error("Parsing error:")
            st.write(e)