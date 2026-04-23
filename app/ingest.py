from pathlib import Path
import time
import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.faiss import DistanceStrategy
from langchain_community.document_loaders import TextLoader
import pandas as pd 

load_dotenv(override=True)
time.sleep(1)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 80,
    length_function = len,
    separators = ["\n\n", "\n", " ", ""]
)

def normalize_ingredients(ingredients_text):
    """
    Converts ingredient string into clean lowercase list
    """
    if pd.isna(ingredients_text):
        return []

    return [
        item.strip().lower()
        for item in str(ingredients_text).split(",")
        if item.strip()
    ]


# -----------------------------
# Load CSV & Convert to Documents
# -----------------------------
documents = []

for csv_file in DATA_DIR.glob("*.csv"):

    print(f"Processing file: {csv_file.name}")

    df = pd.read_csv(csv_file)

    required_columns = ["RecipeName", "Ingredients", "Instructions"]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    for _, row in df.iterrows():

        recipe_name = str(row["RecipeName"]).strip()
        ingredients = str(row["Ingredients"]).strip()
        instructions = str(row["Instructions"]).strip()

        #  Preserve schema in content (VERY IMPORTANT)
        page_content = f"""
Recipe Name:
{recipe_name}

Ingredients:
{ingredients}

Instructions:
{instructions}
"""

        doc = Document(
            page_content=page_content,
            metadata={
                "recipe_name": recipe_name,
                "ingredients_raw": ingredients,
                "ingredients_list": normalize_ingredients(ingredients),
                "source_file": csv_file.name,
            }
        )

        documents.append(doc)


print(f"Total Documents Created: {len(documents)}")

# create embeddings for all the chunks and store them in vector database
embeddings_model = HuggingFaceEmbeddings(
    model_name=os.getenv("HF_EMBEDDINGS_MODEL"),
    encode_kwargs={"normalize_embeddings": True},
    model_kwargs={"token": os.getenv("HUGGING_FACE_TOKEN")},
                #   show_progress_bar=True,
)

# create FAISS vector DB
vector_db = FAISS.from_documents(
    documents=documents,
    embedding=embeddings_model,
    distance_strategy=DistanceStrategy.COSINE,
)
VECTOR_DB_DIR = BASE_DIR / "data" / "semantic-search" / "index" / "faiss"
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
# save vector DB to local directory
vector_db.save_local(folder_path=VECTOR_DB_DIR)