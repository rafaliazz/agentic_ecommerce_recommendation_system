import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent

from ddgs import DDGS

load_dotenv()


# -------------------------
# TOOL
# -------------------------
@tool
def ecommerce_search_ddg(query: str):
    """Search internet for products in Indonesia (DDG/Brave Search)."""
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query + " Indonesian Ecommerce", max_results=8):
            results.append({
                "title": r.get("title"),
                "snippet": r.get("body"),
                "link": r.get("href"),
            })
    return results

from serpapi import GoogleSearch
from langchain.tools import tool
import os

@tool
def ecommerce_search_serp(query: str):
    """Search Indonesian ecommerce products using SerpAPI (Google)."""
    
    params = {
        "engine": "google_shopping",
        "q": query,
        "hl": "id",
        "gl": "id",
        "api_key": os.environ["SERPAPI_KEY"]
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    products = []

    for item in results.get("shopping_results", []):
        products.append({
            "title": item.get("title"),
            "price": item.get("price"),
            "link": item.get("link"),
            "source": item.get("source"),
            "thumbnail": item.get("thumbnail")
        })

    return products


# -------------------------
# AGENT SETUP
# -------------------------
def get_recommender_agent(search_engine = "SERP"):

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=os.getenv("GEMINI_API_KEY"),
    )

    system_prompt = """
You are an Indonesian e-commerce expert.

Use the ecommerce_search tool to find products.

You must return EXACTLY 3 preferably cheaper alternatives.

Return ONLY valid JSON array:
[
  {
    "name": string,
    "price_idr": number,
    "store": string,
    "product_url": string
  }
]

Rules:
- price_idr preferably lower than original
- No duplicates
- No explanations
- No markdown
- Must return JSON only
- Must return something cannot be empty 
- Don't hallucinate, if you cannot find price, input price as null 
- Give actual links in product_url row, they must exist and cannot be empty 
"""
    if search_engine == "SERP":
        tools = [ecommerce_search_serp]
    elif search_engine == "DDG":
        tools = [ecommerce_search_ddg]

    agent = create_agent(model=llm, tools=tools, system_prompt=system_prompt)

    return agent


# -------------------------
# MAIN FUNCTION
# -------------------------
def recommend_cheaper(product_data: Dict[str, Any]):

    agent = get_recommender_agent()

    input_text = (
        f"Find alternatives for {product_data['product_name']} "
        f"with price preferably below {product_data['price']} IDR."
    )

    response = agent.invoke({"messages": [{"role": "user", "content": input_text}]})
    return response["messages"][-1].content

# -------------------------
# TEST
# -------------------------
if __name__ == "__main__":
    product = {
        "product_name": "Headphone X55 Bluetooth Gaming",
        "price": 18750,
        "rating": 4.8
    }

    print(recommend_cheaper(product))