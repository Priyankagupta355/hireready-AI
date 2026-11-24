import re
from pypdf import PdfReader

def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extracts text from all pages of an uploaded PDF 
     file object in Streamlit, cleans up extra whitespace, and returns it.
    """
    try:
        reader = PdfReader(uploaded_file)
        raw_text = []

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                raw_text.append(page_text)

        full_text = "\n".join(raw_text)

        cleaned_text = re.sub(r'\s+',' ', full_text).strip()

        if not cleaned_text:
            raise ValueError("No text could be found in the PDF. Please upload a text-based PDF instead of an image-based scan.")

        return cleaned_text

    except Exception as e:
        raise Exception(f"To read the PDF,this error shows: {str(e)}")        