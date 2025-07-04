import pdfplumber
import pandas as pd
from typing import List, Optional

def extract_tables_with_continuation(
    pdf_path: str,
    output_format: str = "csv",
    min_continuation_rows: int = 1,  # Минимальное число строк для проверки продолжения
) -> List[pd.DataFrame]:
    """
    Извлекает таблицы из PDF, объединяя продолжения на следующих страницах.
    
    :param pdf_path: Путь к PDF-файлу.
    :param output_format: Формат сохранения ("csv" или "xlsx").
    :param min_continuation_rows: Сколько строк сравнивать для определения продолжения.
    :return: Список таблиц в виде DataFrame.
    """
    all_tables = []  # Готовые таблицы
    current_table = None  # Текущая таблица (может продолжаться)

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            
            for table in tables:
                if not table:
                    continue  # Пропускаем пустые
                
                # Если текущая таблица есть, проверяем продолжение
                if current_table is not None:
                    # Берём первые N строк новой таблицы и последние N текущей
                    new_table_start = table[:min_continuation_rows]
                    current_table_end = current_table[-min_continuation_rows:]
                    
                    # Если начала совпадают — это продолжение
                    if new_table_start == current_table_end:
                        current_table.extend(table[min_continuation_rows:])  # Объединяем
                    else:
                        all_tables.append(pd.DataFrame(current_table[1:], columns=current_table[0]))
                        current_table = table  # Начинаем новую таблицу
                else:
                    current_table = table  # Первая таблица
            
        # Добавляем последнюю таблицу, если она есть
        if current_table is not None:
            all_tables.append(pd.DataFrame(current_table[1:], columns=current_table[0]))

    # Сохраняем каждую таблицу в отдельный файл
    for i, df in enumerate(all_tables, 1):
        output_file = f"table_{i}.{output_format}"
        if output_format == "csv":
            df.to_csv(output_file, index=False)
        elif output_format == "xlsx":
            df.to_excel(output_file, index=False)
        print(f"Сохранено: {output_file}")

    return all_tables
