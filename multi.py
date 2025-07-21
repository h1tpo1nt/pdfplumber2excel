pip install pandas tabula-py

import os
import tabula
import pandas as pd

pdf_folder = "pdfs"
output_folder = "output_excel"
os.makedirs(output_folder, exist_ok=True)

# Перебираем все PDF-файлы
for pdf_file in os.listdir(pdf_folder):
    if pdf_file.lower().endswith('.pdf'):
        pdf_path = os.path.join(pdf_folder, pdf_file)
        print(f"Читаю файл: {pdf_file}")

        # Извлечение таблиц
        tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)

        if tables:
            excel_filename = os.path.splitext(pdf_file)[0] + '.xlsx'
            excel_path = os.path.join(output_folder, excel_filename)

            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                for i, table in enumerate(tables):
                    sheet_name = f"Table_{i + 1}"[:31]  # Ограничение Excel: максимум 31 символ
                    # Добавляем заголовок как первую строку
                    header_df = pd.DataFrame([["Table " + str(i + 1)] + [""] * (len(table.columns) - 1)], columns=table.columns)
                    table_with_header = pd.concat([header_df, table], ignore_index=True)
                    # Сохраняем в Excel
                    table_with_header.to_excel(writer, sheet_name=sheet_name, index=False)

            print(f"Сохранено: {excel_filename}")
        else:
            print(f"В файле {pdf_file} не найдено таблиц")
