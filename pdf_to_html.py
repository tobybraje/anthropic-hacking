import os, re, json
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
import nltk
from nltk.corpus import words
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from logger import logging
from langchain.text_splitter import HTMLHeaderTextSplitter
import string
import pickle
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from settings import settings

# # Define your top headings and common subheadings here
# common_subheadings = (
#     "Diagnostic Criteria",
#     "Recording Procedures",
#     "Diagnostic Features",
#     "Prevalence",
#     "Comorbidity",
#     "Differential Diagnosis",
#     "Gender-Related Diagnostic Issues",
#     "Cuiture-Reiated Diagnostic Issues",
#     "Risk and Prognostic Factors",
#     "Development and Course",
#     "Associated Features Supporting Diagnosis",
# )

# Defines font size thresholds for selecting header / text type
font_thresholds = {
    "ignore": float(os.getenv('THRESH_IGNORE', 35.0)), 
    "h1": float(os.getenv('THRESH_H1', 19.4)), 
    "h2": float(os.getenv('THRESH_H2', 14.5)), 
    "h3": float(os.getenv('THRESH_H3', 10.5)), 
    "rest": float(os.getenv('THRESH_REST', 0))
    }

load_dotenv()
logger = logging.getLogger('app.embedding')
EMBEDDINGS = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Load in NLTK words if needed
nltk.download('words')
word_list = set(words.words())
allowed_letters = {'a', 'i'} # "Real" single letter words
blacklist_words = {'jo',}

def check_gibberish(text_block, threshold=int(os.getenv('GIB_THRESH', 3))) -> bool: # Return true if all words ARE gibberish
    words = text_block.split()
    # Adjust threshold to text size if needed
    real_thresh = min(threshold, len(words)//2) # Need //2 as checking from both ends
    
    # Check first and last threshold number of words (if enough words) are all "real" words
    for word in words[:real_thresh]+words[-real_thresh:]:
        word = word.translate(str.maketrans('', '', string.punctuation)) # Strips out punctuation (which should be allowed)
        if word.lower() in blacklist_words: # Manual blacklist
            return True
        if len(word) == 1 and word.lower() not in allowed_letters: # (NLTK allows single letters)
            return True
        if word.lower() not in word_list and not re.match(r"\(\w+\d+\)", word): # If word is not real / is an allowed struct (F90), then it isnt gibberish
            return True
    return False

def extract_with_style(pdf_filename): # FIXME this is taking the bulk of the time
    logger.debug('Extracting data from PDF')

    resource_manager = PDFResourceManager()
    la_params = LAParams()
    device = PDFPageAggregator(resource_manager, laparams=la_params)
    interpreter = PDFPageInterpreter(resource_manager, device)

    extracted_data = []

    with open(pdf_filename, "rb") as f:
        for page in PDFPage.get_pages(f):
            interpreter.process_page(page)
            layout = device.get_result()
            for obj in layout:
                if isinstance(obj, LTTextBox):
                    for line in obj:
                        text = line.get_text().strip()
                        size = line.height  # Use height as a proxy for font size
                        extracted_data.append((text, size))

    # Pickle the output data for future use
    if os.getenv("PICKLE_EXTRACT", 'false').lower() in ('t', 'true', 'y', 'yes'):
        with open('extracted_data.pkl', 'wb') as f:
            pickle.dump(extracted_data, f)

    return extracted_data

def pdf_to_html(pdf_filename):
    logger.info(f'Converting PDF to HTML: {pdf_filename}')


    # Use the pickle file to load the extracted data with style
    if os.getenv("PICKLE_EXTRACT", 'false').lower() in ('t', 'true', 'y', 'yes'):
        with open('extracted_data.pkl', 'rb') as f:
            data_with_style = pickle.load(f)
    else:
        data_with_style = extract_with_style(pdf_filename)

    logger.debug('Converting to HTML')
    # Getting the unique font sizes and sorting them
    unique_font_sizes = sorted(set(size for _, size in data_with_style), reverse=True)

    # Manual Correction mapper
    with open('clean.json', 'r') as f:
        clean_mapper = json.load(f)
    incorrects = re.compile(r'\b(' + '|'.join(re.escape(key) for key in clean_mapper.keys()) + r')\b')

    soup = BeautifulSoup(features="html.parser")

    # Create an HTML structure
    html = soup.new_tag("html")
    head = soup.new_tag("head")
    title = soup.new_tag("title")
    title.string = "DSM-5 HTML"
    head.append(title)
    html.append(head)
    body = soup.new_tag("body")
    html.append(body)

    div = soup.new_tag("div")  # Initialize div
    p_text = ""  # Initialize paragraph text

    # Iterate through extracted data to convert to HTML
    for text, size in data_with_style:
        # Cleaning text (replacing misread words, double whitespace)
        text =  incorrects.sub(lambda match: clean_mapper.get(match.group(0), match.group(0)), text) # Clean incorrect words
        text = text.replace('  ', ' ') # Clean double whitespace

        if '------' in text: #or check_gibberish(text): # If start/end words are gibberish or ----
            continue

        if font_thresholds["ignore"] > size >= font_thresholds["h3"]: #or text in common_subheads:  # Just doing this way to avoid repeating p_text stuff
            if p_text:  # Add remaining paragraph text to div before starting new heading
                # if not check_gibberish(p_text):
                p = soup.new_tag("p")
                p.string = p_text
                div.append(p)
                p_text = ""

            if font_thresholds["ignore"] > size >= font_thresholds["h1"]:  # Largest font size for h1
                div = soup.new_tag("div")  # Create a new div for each h1
                h1 = soup.new_tag("h1")
                h1.string = text
                div.append(h1)  # Append h1 to div
                body.append(div)  # Append div to body
            elif font_thresholds["h1"] > size >= font_thresholds["h2"]:  # Second largest font size for h2
                h2 = soup.new_tag("h2")
                h2.string = text
                div.append(h2)  # Append h2 to the current div
            elif font_thresholds["h2"] > size >= font_thresholds["h3"]: # Either subsub titles or unique codes 
                if re.search(r'^\d+', text): # If its a disorder code
                    h = soup.new_tag("h4")
                else:
                    h = soup.new_tag("h3")
                h.string = text
                div.append(h)  # Append h3 to the current div
        elif font_thresholds["h3"] > size >= font_thresholds["rest"]:
            p_text += " " + text  # Concatenate normal text lines

    # Add remaining paragraph text to div
    if p_text:
        p = soup.new_tag("p")
        p.string = p_text
        div.append(p)

    soup.append(html)
    html_str = str(soup.prettify())

    # Merge consecutive header tags
    html_str = re.sub(r'</h1>\s*</div>\s*<div>\s*<h1>', ' ', html_str)
    html_str = re.sub(r'</h2>\s*<h2>', ' ', html_str)
    html_str = re.sub(r'</h3>\s*<h3>', ' ', html_str)
    html_str = re.sub(r'</h4>\s*<h4>', ' ', html_str)

    # Merge hyphenated words that span across lines (couldnt figure out doing it inside loop)
    html_str = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', html_str)

    # Merge consecutive h1 tags
    return html_str


def chunk_html(html_content):
    logger.debug('Chunking HTML')
    html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=[("h1", "Disorder"), ("h2", "Sub-Disorder"), ("h3", "Subject"), ("h4", "Identifier Code")])
    chunks = html_splitter.split_text(html_content)
    return chunks


def convert_pdf_to_html(pdf_filename=settings.DSM_PATH):
    html_content = pdf_to_html(pdf_filename)
    out_name = f'output{"_test" if "test" in pdf_filename else ""}.html'
    with open(out_name, "w+", encoding="utf-8") as f:
        f.write(html_content)
    logger.debug(f'Wrote HTML out to {out_name}')

    exit()

    chunks = chunk_html(html_content)
    logger.debug(f'Created {len(chunks)} chunks')
    for chunk in chunks:
        if not chunk.metadata:
            chunks.remove(chunk)

    db = Chroma.from_documents(chunks, EMBEDDINGS, persist_directory="./chroma_db")

    logger.info('HTML content saved')


if __name__ == "__main__":
    convert_pdf_to_html()
