import PyPDF2
import os
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import Config
from io import BytesIO

# OCR dependencies
try:
    from pdf2image import convert_from_bytes
    from PIL import Image
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
        )

    def extract_text_from_pdf_bytes(self, pdf_bytes: BytesIO) -> str:
        """Extract text from PDF file-like object (in-memory), with OCR fallback for scanned/image-based PDFs."""
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_bytes)
            print(f"PDF has {len(pdf_reader.pages)} pages (in-memory)")
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = ""
                try:
                    page_text = page.extract_text()
                except Exception as e:
                    print(f"Error extracting text from page {page_num + 1}: {e}")
                if not page_text or not page_text.strip():
                    print(f"Page {page_num + 1} appears to be empty or image-based. Trying OCR...")
                    if HAS_OCR:
                        try:
                            # Convert the specific page to image and OCR
                            images = convert_from_bytes(pdf_bytes.getvalue(), first_page=page_num+1, last_page=page_num+1)
                            ocr_text = ""
                            for img in images:
                                ocr_text += pytesseract.image_to_string(img)
                            if ocr_text.strip():
                                page_text = ocr_text
                                print(f"OCR extracted {len(ocr_text)} characters from page {page_num + 1}")
                            else:
                                print(f"OCR failed to extract text from page {page_num + 1}")
                        except Exception as ocr_e:
                            print(f"OCR error on page {page_num + 1}: {ocr_e}")
                    else:
                        print("OCR dependencies not installed. Skipping OCR.")
                if page_text and page_text.strip():
                    text += f"\n--- Page {page_num + 1} ---\n"
                    text += page_text
                else:
                    print(f"No text extracted from page {page_num + 1}")
            print(f"Total extracted text length: {len(text)} characters (in-memory)")
            if not text.strip():
                raise Exception("No text could be extracted from any page of the PDF (in-memory)")
            sample_text = text[:500] + "..." if len(text) > 500 else text
            print(f"Sample extracted text: {sample_text}")
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF (in-memory): {str(e)}")

    def process_pdf_bytes(self, pdf_bytes: BytesIO) -> List[str]:
        text = self.extract_text_from_pdf_bytes(pdf_bytes)
        if not text.strip():
            raise Exception("No text could be extracted from the PDF (in-memory)")
        chunks = self.text_splitter.split_text(text)
        print(f"Split text into {len(chunks)} chunks (in-memory)")
        filtered_chunks = [chunk for chunk in chunks if len(chunk.strip()) > 50]
        print(f"After filtering short chunks: {len(filtered_chunks)} chunks remain (in-memory)")
        if not filtered_chunks:
            raise Exception("No meaningful text chunks could be created from the PDF (in-memory)")
        for i, chunk in enumerate(filtered_chunks[:3]):
            print(f"Chunk {i+1} sample: {chunk[:200]}... (in-memory)")
        return filtered_chunks

    def save_uploaded_file(self, uploaded_file, filename: str) -> str:
        """Save uploaded file to disk"""
        try:
            os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
            file_path = os.path.join(Config.UPLOAD_DIR, filename)

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Verify file was saved
            if not os.path.exists(file_path):
                raise Exception(f"Failed to save file to {file_path}")

            file_size = os.path.getsize(file_path)
            print(f"Saved file: {file_path} ({file_size} bytes)")

            return file_path

        except Exception as e:
            raise Exception(f"Error saving uploaded file: {str(e)}")