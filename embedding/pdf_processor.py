from PyPDF2 import PdfReader
import openai
import os

class PDFProcessor:
    def __init__(self, azure_endpoint, azure_api_key, api_version, embedding_model):
        """
        Initialize PDF Processor for Azure OpenAI embeddings
        """
        # Set Azure OpenAI environment variables
        os.environ["OPENAI_API_TYPE"] = "azure"
        os.environ["OPENAI_API_BASE"] = azure_endpoint
        os.environ["OPENAI_API_VERSION"] = api_version
        os.environ["OPENAI_API_KEY"] = azure_api_key

        self.embedding_model = embedding_model
        self.client = openai.OpenAI()  # v1.0+ client

    def process_pdf(self, pdf_path, chunk_size=1000, overlap=100):
        reader = PdfReader(pdf_path)
        documents = []

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue

            chunks = self._chunk_text(text, chunk_size, overlap)
            for idx, chunk in enumerate(chunks):
                embedding = self._get_embedding(chunk)
                documents.append({
                    "content": chunk,
                    "embedding": embedding,
                    "source": str(pdf_path),
                    "page": page_num + 1,
                    "chunk_index": idx
                })

        return documents

    def _chunk_text(self, text, chunk_size, overlap):
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks

    def _get_embedding(self, text):
        """
        Generate embedding using Azure OpenAI
        """
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding
