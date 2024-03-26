# pdf_handler.py
import PyPDF2

def extract_text_from_pdf(pdf_file):
    # Open the PDF file
    with open(pdf_file, 'rb') as file:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(file)
        # Extract text from each page
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text