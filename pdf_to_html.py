import sys
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from bs4 import BeautifulSoup

def extract_with_style(pdf_filename):
    resource_manager = PDFResourceManager()
    la_params = LAParams()
    device = PDFPageAggregator(resource_manager, laparams=la_params)
    interpreter = PDFPageInterpreter(resource_manager, device)

    extracted_data = []

    with open(pdf_filename, 'rb') as f:
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

def pdf_to_html(pdf_filename, common_subheadings):
    data_with_style = extract_with_style(pdf_filename)

    # Getting the unique font sizes and sorting them
    unique_font_sizes = sorted(set(size for _, size in data_with_style), reverse=True)

    soup = BeautifulSoup(features="html.parser")

    # Create an HTML structure
    html = soup.new_tag("html")
    head = soup.new_tag("head")
    title = soup.new_tag("title")
    title.string = "Converted PDF"
    head.append(title)
    html.append(head)
    body = soup.new_tag("body")
    html.append(body)

    # Iterate through extracted data to convert to HTML
    for text, size in data_with_style:
        if size == unique_font_sizes[0]:  # Largest font size for h1
            h1 = soup.new_tag("h1")
            h1.string = text
            body.append(h1)
        elif size == unique_font_sizes[1]:  # Second largest font size for h2
            h2 = soup.new_tag("h2")
            h2.string = text
            body.append(h2)
        elif text in common_subheadings:
            h3 = soup.new_tag("h3")
            h3.string = text
            body.append(h3)
        else:
            p = soup.new_tag("p")
            p.string = text
            body.append(p)

    soup.append(html)

    return str(soup.prettify())


if __name__ == "__main__":
    # Hardcoded PDF and HTML filenames
    pdf_filename = "/Users/aaliyamanji/anthropic/anthropic-hacking/DSM-5_test.pdf"
    html_filename = "output.html"

    # Define your top headings and common subheadings here
    common_subheadings = ['Diagnostic Criteria', 'Recording Procedures', 'Diagnostic Features', 'Prevalence', 'Comorbidity', 'Differential Diagnosis',
    'Gender-Related Diagnostic Issues', 'Cuiture-Reiated Diagnostic Issues', 'Risk and Prognostic Factors', 'Development and Course',
    'Associated Features Supporting Diagnosis']

    html_content = pdf_to_html(pdf_filename, common_subheadings)

    with open(html_filename, 'w+', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML content saved to {html_filename}")