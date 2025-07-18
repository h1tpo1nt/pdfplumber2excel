!pip install camelot-py openpyxl

import os
import camelot
import pandas as pd

# Путь к папке с PDF-файлами
pdf_folder = "путь/к/вашей/папке"
# Путь для сохранения Excel-файлов
output_folder = "путь/к/папке/для/excel"
os.makedirs(output_folder, exist_ok=True)

# Перебор всех PDF-файлов в папке
for filename in os.listdir(pdf_folder):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, filename)
        print(f"Обработка файла: {filename}")

        # Извлечение таблиц
        tables = camelot.read_pdf(pdf_path, pages="all")

        if tables:
            # Создание ExcelWriter для записи нескольких листов
            excel_filename = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.xlsx")

            with pd.ExcelWriter(excel_filename, engine="openpyxl") as writer:
                for i, table in enumerate(tables):
                    # Преобразование в DataFrame
                    df = table.df

                    # Запись в Excel (каждая таблица на отдельный лист)
                    sheet_name = f"Таблица_{i+1}"
                    df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
                print(f"{len(tables)} таблиц записано в {excel_filename}")
        else:
            print(f"В файле {filename} таблицы не найдены")