from langchain.document_loaders import PDFMinerPDFasHTMLLoader
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

# Load the PDF
loader = PDFMinerPDFasHTMLLoader(os.getenv("DSM-PATH", "./DSM-5.pdf"))
docs = loader.load()

# Parse the HTML to extract the structure
soup = BeautifulSoup(docs[0].page_content, 'html.parser')
