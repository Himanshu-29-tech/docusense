from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os




from ocr_engine import extract_text
from entity_extractor import extract_entities
from llm_processor import analyze_document
from database import init_db, save_document, get_all_documents, check_duplicate_invoice



app = FastAPI()



# CORS — ye zaroori hai! Isse browser ko allow milta hai ki wo
# alag port (React, jo 3000 pe chalta hai) se is API (jo 8000 pe chalta hai) ko call kar sake
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


init_db()


@app.post("/api/process-document")
async def process_document(file: UploadFile = File(...)):
  # UploadFile = File(...) — FastAPI ko batata hai ki is endpoint pe ek file aayegi
    # Uploaded file ko temporarily save karo
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    # Wahi pipeline jo pehle Streamlit mein tha
    raw_text = extract_text(tmp_path)
    entities = extract_entities(raw_text)
    analysis = analyze_document(raw_text, entities)

    is_duplicate = False
    if entities.get("invoice_number"):
        is_duplicate = check_duplicate_invoice(entities["invoice_number"])

    os.unlink(tmp_path)

    # Ye poora response JSON ban ke React ke paas jayega
    return {
        "filename": file.filename,
        "raw_text": raw_text,
        "entities": entities,
        "analysis": analysis,
        "is_duplicate": is_duplicate,
    }


@app.post("/api/save-document")
# @app.post(...) — ek "decorator" hai jo bolta hai "jab koi is URL pe POST request bheje, ye function chalao"
async def save_doc(data: dict):
    save_document(
        data["filename"], data["document_type"], data["raw_text"],
        data["entities"], data["summary"], data["anomalies"]
    )
    return {"status": "saved"}


@app.get("/api/documents")
async def get_documents():
    docs = get_all_documents()
    result = []
    for doc in docs:
        result.append({
            "id": doc[0], "filename": doc[1], "document_type": doc[2],
            "summary": doc[5], "anomalies": doc[6], "processed_at": doc[7],
        })
    return result


    # return {...} — FastAPI automatically ise JSON mein convert kar deta hai, humein manually karne ki zaroorat nahi