!pip install pytesseract pillow pdfplumber pandas openpyxl fpdf2 pymupdf

import pytesseract
from PIL import Image
import fitz  # PyMuPDF
from fpdf import FPDF
import pdfplumber
import pandas as pd
import os

# -----------------------------
# Шаг 1: OCR и создание нового PDF
# -----------------------------

def pdf_to_ocr_and_create_new_pdf(input_pdf_path, output_pdf_path):
    doc = fitz.open(input_pdf_path)
    ocr_text_pages = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=200)  # Высокое качество для OCR
        img_path = f"page_{page_num}.png"
        pix.save(img_path)

        # OCR через Tesseract
        text = pytesseract.image_to_string(Image.open(img_path))
        ocr_text_pages.append(text)

        os.remove(img_path)  # Очистка временных файлов

    doc.close()

    # Создание нового PDF с распознанным текстом
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for page_text in ocr_text_pages:
        pdf.add_page()
        pdf.multi_cell(0, 10, txt=page_text)

    pdf.output(output_pdf_path)
    print(f"Новый PDF создан с OCR: {output_pdf_path}")

# -----------------------------
# Шаг 2: Извлечение таблиц из нового PDF
# -----------------------------

def extract_tables_from_pdf(pdf_path):
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            found_tables = page.extract_tables()
            for table in found_tables:
                df = pd.DataFrame(table[1:], columns=table[0])
                df = df.map(clean_cell)
                tables.append(df)
    return tables

# -----------------------------
# Шаг 3: Функция очистки ячеек
# -----------------------------

def clean_cell(value):
    if isinstance(value, str):
        value = value.strip()
        # Меняем точки на запятые
        value = value.replace('.', ',')
        # Меняем формат (123) → -123
        if value.startswith('(') and value.endswith(')'):
            value = '-' + value[1:-1]
        return value
    return value

# -----------------------------
# Шаг 4: Сохранение всех таблиц в один лист Excel
# -----------------------------

def save_all_tables_in_one_sheet(tables, excel_path):
    combined_df = pd.concat(tables, ignore_index=True)
    combined_df.to_excel(excel_path, index=False, sheet_name='All_Tables')
    print(f"Все таблицы объединены и сохранены в: {excel_path}")

# -----------------------------
# Шаг 5: Основной процесс
# -----------------------------

if __name__ == "__main__":
    input_pdf = "mosaic Q1 2020.pdf"     # Исходный PDF (возможно, без текстового слоя)
    ocr_pdf = "ocr_output.pdf"           # Новый PDF после OCR
    output_excel = "output_all_tables.xlsx"  # Целевой Excel-файл

    # Шаг 1: OCR и создание нового PDF
    pdf_to_ocr_and_create_new_pdf(input_pdf, ocr_pdf)

    # Шаг 2: Извлечение таблиц
    tables = extract_tables_from_pdf(ocr_pdf)

    # Шаг 3: Сохранение в Excel
    save_all_tables_in_one_sheet(tables, output_excel)
