from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import httpx
import asyncio

app = FastAPI(
    title="Evidentix API",
    description="Cell ID Intelligence Fetch Engine",
    version="1.0"
)

# ✅ CORS (frontend connect karega)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔗 External API
API_URL = "https://bade-bhai-hone-ka-najaysh-fayda.vercel.app/api/cellid/"

# ⚡ Batch size (optimize)
BATCH_SIZE = 50


# ✅ Request Model (Swagger fix)
class CellRequest(BaseModel):
    cells: List[str]


# 🔹 Single API fetch
async def fetch_single(client, cid: str):
    try:
        url = f"{API_URL}{cid}"
        res = await client.get(url, timeout=10)

        if res.status_code == 200:
            data = res.json()

            if "latitude" in data and "longitude" in data:
                return cid, data

    except Exception as e:
        print(f"[ERROR] {cid}: {e}")

    return cid, None


# 🔥 MAIN API
@app.post("/fetch_cells")
async def fetch_cells(req: CellRequest):
    cells = req.cells

    if not cells:
        return {"success": False, "error": "No cells provided"}

    results: Dict[str, dict] = {}

    async with httpx.AsyncClient() as client:
        # batching
        for i in range(0, len(cells), BATCH_SIZE):
            batch = cells[i:i + BATCH_SIZE]

            tasks = [fetch_single(client, cid) for cid in batch]
            responses = await asyncio.gather(*tasks)

            for cid, data in responses:
                if data:
                    results[cid] = data

    return {
        "success": True,
        "count": len(results),
        "data": results
    }