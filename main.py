from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from typing import List
from Similar_Case_Finder import generate
from summary import process_uploaded_texts, rag_chain
from ner import run_ner_on_uploaded_file
import os
import json

# FastAPI app setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

EXTRACTED_TEXT_FILE = "extracted_text.json"  # File to store the extracted text

# Route: Home
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



@app.post("/upload")
async def upload_files(preamble_file: UploadFile = File(...), judgment_file: UploadFile = File(...)):
    file_names = [preamble_file.filename, judgment_file.filename]

    # Save uploaded files
    for file in [preamble_file, judgment_file]:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

    # 🧠 Step 1: Store extracted text in a file for future access
    try:
        with open(os.path.join(UPLOAD_FOLDER, preamble_file.filename), 'r') as f:
            preamble = f.read()

        with open(os.path.join(UPLOAD_FOLDER, judgment_file.filename), 'r') as f:
            judgment = f.read()

        save_extracted_text(preamble, judgment)

    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

    # 🧠 Step 2: Process the files (e.g., vector DB creation)
    process_uploaded_texts()  # Ensure this comes after saving files

    return JSONResponse(content={"message": "Files received successfully."})




# Save extracted text to a JSON file
def save_extracted_text(preamble: str, judgment: str):
    extracted_text = {
        "preamble": preamble,
        "judgment": judgment
    }
    with open(EXTRACTED_TEXT_FILE, 'w') as f:
        json.dump(extracted_text, f)

# Load extracted text from the saved JSON file
def load_extracted_text():
    if os.path.exists(EXTRACTED_TEXT_FILE):
        with open(EXTRACTED_TEXT_FILE, 'r') as f:
            return json.load(f)
    return None

# Route: Summary Page
@app.get("/summary", response_class=HTMLResponse)
async def summary(request: Request):
    # Load preamble and judgment text from the file
    extracted_text = load_extracted_text()

    if not extracted_text or not extracted_text.get("preamble") or not extracted_text.get("judgment"):
        return templates.TemplateResponse("summary.html", {
            "request": request,
            "error": "No preamble and judgment found. Please upload a file first."
        })
    
    preamble = extracted_text["preamble"]
    judgment = extracted_text["judgment"]

    # Send preamble and judgment text to the template for display
    return templates.TemplateResponse("summary.html", {
        "request": request,
        "preamble": preamble,
        "judgment": judgment
    })

# Route: Ask a Summary Question
@app.post("/summary")
async def ask_summary(request: Request):
    form_data = await request.form()
    question = form_data.get("question")

    if not question:
        return templates.TemplateResponse("summary.html", {"request": request, "error": "Please enter a question."})

    try:
        response = rag_chain.invoke(question)
        return templates.TemplateResponse("summary.html", {"request": request, "question": question, "response": response})
    except Exception as e:
        return templates.TemplateResponse("summary.html", {"request": request, "error": str(e)})

# Route: Similar Cases Page
@app.get("/similar", response_class=HTMLResponse)
async def similar(request: Request):
    return templates.TemplateResponse("similar.html", {"request": request})

# Route: NER Page
@app.get("/ner", response_class=HTMLResponse)
async def ner(request: Request):
    return templates.TemplateResponse("ner.html", {"request": request})

# Route: Generate Similar Case
@app.post("/generate_case")
async def generate_case(request: Request):
    body = await request.json()
    query = body.get("query")

    if not query:
        return JSONResponse(status_code=400, content={"error": "No query provided"})

    try:
        result = generate(query)
        return JSONResponse(content={"output": result})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/run_ner")
async def run_ner(type: str):
    try:
        if type.lower() == "preamble":
            filename = next(f for f in os.listdir("uploads") if "preamble" in f.lower())
        elif type.lower() == "judgement":
            filename = next(f for f in os.listdir("uploads") if "judgement" in f.lower())
        else:
            return JSONResponse(status_code=400, content={"error": "Invalid type."})

        filepath = os.path.join("uploads", filename)
        with open(filepath, "r") as f:
            text = f.read()

        ner_output = run_ner_on_uploaded_file(filename)  # List of entities

        transformed_entities = [
            {
                "start": ent["start"],
                "end": ent["end"],
                "label": ent["entity_group"].upper()
            }
            for ent in ner_output
        ]

        return JSONResponse(content={
            "text": text,
            "entities": transformed_entities
        })

    except StopIteration:
        return JSONResponse(status_code=404, content={"error": f"No file found for type '{type}'."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
