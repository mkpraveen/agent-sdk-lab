from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

def create_vector_store(store_name: str) -> str:
    vs = client.vector_stores.create(name=store_name)
    return vs.id

def upload_file(file_path: str, vector_store_id: str):
    file_resp = client.files.create(file=open(file_path, 'rb'), purpose="assistants")
    client.vector_stores.files.create(vector_store_id=vector_store_id, file_id=file_resp.id)

vs_id = create_vector_store("Fitness Knowledge Base - PMK")
upload_file("get-fit-life-book.pdf", vs_id)
