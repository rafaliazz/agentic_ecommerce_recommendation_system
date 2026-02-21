import streamlit as st
import requests
from PIL import Image
import json

API_URL = "http://127.0.0.1:8000/analyze"

st.set_page_config(page_title="AI E-Commerce Analyzer", layout="wide")

st.title("🛒 AI E-Commerce Screenshot Analyzer")

uploaded_file = st.file_uploader(
    "Upload Screenshot",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:

    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Screenshot", use_container_width=True)

    if st.button("Analyze Screenshot"):

        with st.spinner("Sending to backend..."):

            try:
                files = {
                    "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
                }

                response = requests.post(API_URL, files=files)

                # -------------------------
                # Check HTTP status
                # -------------------------
                if response.status_code != 200:
                    st.error("Backend returned non-200 status")
                    st.write(response.text)
                    st.stop()

                data = response.json()

                # -------------------------
                # Debug raw response
                # -------------------------
                if "error" in data:
                    st.error("Backend processing error:")
                    st.write(data["error"])
                    st.stop()

                if "detail" in data:
                    st.error("Backend detail error:")
                    st.write(data["detail"])
                    st.stop()

                st.success("Backend processing successful ✅")

                # -------------------------
                # OCR Text
                # -------------------------
                st.subheader("📄 OCR Text")
                st.text_area(
                    "Detected Text",
                    data.get("ocr_text", ""),
                    height=200
                )

                # -------------------------
                # Extracted Product
                # -------------------------
                st.subheader("📦 Extracted Product Data")
                st.json(data.get("product_data", {}))

                # -------------------------
                # Cheaper Alternatives
                # -------------------------
                st.subheader("💰 Cheaper Alternatives")

                cheaper = data.get("cheaper_products", [])

                # If returned as string, try parse
                if isinstance(cheaper, str):
                    try:
                        cheaper = json.loads(cheaper)
                    except:
                        st.write(cheaper)
                        st.stop()

                if isinstance(cheaper, list):
                    if len(cheaper) == 0:
                        st.info("No cheaper alternatives found.")
                    else:
                        for item in cheaper:
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
                                st.markdown(
                                    f"[🔗 View Product]({item.get('product_url', '#')})"
                                )
                                st.divider()
                else:
                    st.write(cheaper)

            except Exception as e:
                st.error("Request failed:")
                st.write(str(e))