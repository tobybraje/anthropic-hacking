import sys, os, re
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from logger import logging
from langchain.text_splitter import HTMLHeaderTextSplitter

load_dotenv()
logger = logging.getLogger('app.embedding')

# Define your top headings and common subheadings here
common_subheadings = [
    "Diagnostic Criteria",
    "Recording Procedures",
    "Diagnostic Features",
    "Prevalence",
    "Comorbidity",
    "Differential Diagnosis",
    "Gender-Related Diagnostic Issues",
    "Cuiture-Reiated Diagnostic Issues",
    "Risk and Prognostic Factors",
    "Development and Course",
    "Associated Features Supporting Diagnosis",
]


def extract_with_style(pdf_filename):
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

    return extracted_data


def pdf_to_html(pdf_filename, common_subheads=common_subheadings):
    logger.debug('Converting PDF to HTML')

    data_with_style = extract_with_style(pdf_filename)

    # Getting the unique font sizes and sorting them
    unique_font_sizes = sorted(set(size for _, size in data_with_style), reverse=True)

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
        if '----' in text:
            continue
        if size in unique_font_sizes[:2] or text in common_subheads:  # Just doing this way to avoid repeating p_text stuff
            if p_text:  # Add remaining paragraph text to div before starting new heading
                p = soup.new_tag("p")
                p.string = p_text
                div.append(p)
                p_text = ""

            if size == unique_font_sizes[0]:  # Largest font size for h1
                div = soup.new_tag("div")  # Create a new div for each h1
                h1 = soup.new_tag("h1")
                h1.string = text
                div.append(h1)  # Append h1 to div
                body.append(div)  # Append div to body
            elif size == unique_font_sizes[1]:  # Second largest font size for h2
                h2 = soup.new_tag("h2")
                h2.string = text
                div.append(h2)  # Append h2 to the current div
            else:  # If the line is a common subheading
                h3 = soup.new_tag("h3")
                h3.string = text
                div.append(h3)  # Append h3 to the current div
        else:
            re.sub(r'.+- ', '', text)
            p_text += " " + text  # Concatenate normal text lines

    # Add remaining paragraph text to div
    if p_text:
        p = soup.new_tag("p")
        p.string = p_text
        div.append(p)

    soup.append(html)
    html_str = str(soup.prettify())

    # Merge consecutive h1 tags
    html_str = re.sub(r'</h1>\s*</div>\s*<div>\s*<h1>', ' ', html_str)

    # Merge hyphenated words that span across lines
    html_str = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', html_str)

    # Merge consecutive h1 tags
    return html_str


def chunk_html(html_content):
    html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=[("h1", "Header 1"), ("h2", "Header 2"), ("h3", "Header 3")])
    chunks = html_splitter.split_text(html_content)
    return chunks


def convert_pdf_to_html(pdf_filename="DSM-5_test.pdf"):
    html_content = pdf_to_html(pdf_filename)
    out_name = f'output{"_test" if "test" in pdf_filename else ""}.html'
    with open(out_name, "w+", encoding="utf-8") as f:
        f.write(html_content)

    chunks = chunk_html(html_content)
    print(len(chunks))
    for chunk in chunks:
        print(chunk.page_content[:30])
        print(chunk.metadata)
        print("BREAK")

    logger.info('HTML content saved')


if __name__ == "__main__":
    convert_pdf_to_html()
