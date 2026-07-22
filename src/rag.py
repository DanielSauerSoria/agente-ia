import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

from src.prompts import SYSTEM_PROMPT

from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    pipeline
)

from src.prompts import SYSTEM_PROMPT

class RAGAgent:

    def __init__(self):
        self.vectorstore = None
        self.retriever = None
        self.generator = None

    def build_vectorstore(self, documents):

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        )

        chunks = splitter.split_documents(documents)

        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )


        db_path = "vector_db"
        index_file = os.path.join(db_path, "index.faiss")

        if os.path.exists(index_file):

            print("Cargando base vectorial...")

            self.vectorstore = FAISS.load_local(
                db_path,
                embeddings,
                allow_dangerous_deserialization=True
            )

        else:

            print("Creando base vectorial...")

            self.vectorstore = FAISS.from_documents(
                chunks,
                embeddings
            )

            self.vectorstore.save_local(db_path)

            print("Base vectorial guardada.")

        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k":2}
        )

    def load_llm(self):

        model_name = "Qwen/Qwen2.5-1.5B-Instruct"

        tokenizer = AutoTokenizer.from_pretrained(model_name)

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,   # CPU
        )

        self.generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer
        )

    def ask(self, question):

        docs = self.retriever.invoke(question)

        context = "\n\n".join(
            doc.page_content for doc in docs
        )

        prompt = SYSTEM_PROMPT.format(
            context=context,
            question=question
        )

        response = self.generator(
            prompt,
            max_new_tokens=300,
            do_sample=False,
            return_full_text=False
        )

        fuentes = [
            {
                "archivo": doc.metadata["source"],
                "pagina": doc.metadata["page"] + 1
            }
            for doc in docs
        ]

        return {
            "respuesta": response[0]["generated_text"],
            "fuentes": fuentes
        }