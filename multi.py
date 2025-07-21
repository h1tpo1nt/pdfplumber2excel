pip install pandas tabula-py

import os
import pandas as pd
import tabula

pdf_folder = "pdfs"
output_folder = "output_tables"
os.makedirs(output_folder, exist_ok=True)

for pdf_file in os.listdir(pdf_folder):
    if pdf_file.lower().endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, pdf_file)
        print(f"Читаю файл: {pdf_file}")

        tables = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True)

        if tables:
            excel_path = os.path.join(output_folder, f"{os.path.splitext(pdf_file)[0]}.xlsx")
            with pd.ExcelWriter(excel_path) as writer:
                for i, table in enumerate(tables):
                    sheet_name = f"Table_{i + 1}"
                    table.to_excel(writer, sheet_name=sheet_name[:31], index=False)
            print(f"Сохранено: {excel_path}")
        else:
            print(f"В файле {pdf_file} не найдены таблицы")
