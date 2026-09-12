import spacy
import re

nlp = spacy.load("en_core_web_sm")

def extract_entities(text: str) -> dict:
    doc = nlp(text)
    
    entities = {
        "organizations": [],
        "dates": [],
        "money": [],
    }
    
    for ent in doc.ents:
        if ent.label_ == "ORG":
            entities["organizations"].append(ent.text)
        elif ent.label_ == "DATE":
            entities["dates"].append(ent.text)
        elif ent.label_ == "MONEY":
            entities["money"].append(ent.text)
    
    invoice_number = re.search(r"(?:invoice|inv)\s*#?\s*:?\s*([A-Z0-9\-]+)", text, re.IGNORECASE)
    entities["invoice_number"] = invoice_number.group(1) if invoice_number else None
    
    amounts = re.findall(r"[₹$]\s?[\d,]+\.?\d*", text)
    entities["amounts_found"] = amounts
    
    return entities