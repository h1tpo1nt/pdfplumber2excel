pip install tabula-py pandas openpyxl

import os
import tabula
import pandas as pd
from openpyxl import load_workbook

# Настройки папок
pdf_folder = "/content/pdfs"
output_folder = "/content/output"
os.makedirs(output_folder, exist_ok=True)


def normalize_numbers(cell):
    """Преобразует строковые числа к нужному формату (с запятой как десятичный разделитель)."""
    if not isinstance(cell, str):
        return cell

    # Сохраняем оригинал только для возврата в крайнем случае
    cell = cell.strip()

    # === Полная очистка пробелов и спецсимволов ===
    cell = (cell
            .replace('\xa0', ' ')      # неразрывный пробел
            .replace('\u202f', ' ')     # узкий неразрывный пробел
            .replace('\u00A0', ' ')     # альтернативная форма неразрывного пробела
            .replace('\t', ' ')         # табуляция
            .replace('  ', ' ')         # замена двойных пробелов на одинарные (можно повторить при необходимости)
            .strip())

    # Удаляем символ доллара в любом месте
    cell = cell.replace('$', '')

    # Если после очистки — пусто
    if not cell:
        return ""

    # === Обработка скобок: (99), (99.5), (99,5), ( 99.5 ) → -99,5 ===
    if cell.startswith('(') and cell.endswith(')'):
        inner = cell[1:-1].strip()
        # Заменяем запятую на точку для парсинга
        inner_clean = inner.replace(',', '.').replace(' ', '').replace('\xa0', '')
        try:
            value = float(inner_clean)
            formatted = f"{-value:g}".replace('.', ',')
            return formatted
        except ValueError:
            # Если не число — возвращаем очищенную строку (без $ и пробелов)
            return cell

    # === Формат 1,234.5 → 1234,5 (американский) ===
    if ',' in cell and '.' in cell:
        if cell.rfind('.') > cell.rfind(','):  # последняя точка после последней запятой → тысячи через , десятичные через .
            cleaned = cell.replace(',', '')  # убираем разделители тысяч
            return cleaned.replace('.', ',')
        else:  # европейский формат: 1.234,5 → 1234,5
            return cell.replace('.', '')

    # === Только точка: 123.45 → 123,45 ===
    if '.' in cell and ',' not in cell:
        try:
            float(cell.replace(',', '').replace(' ', ''))
            return cell.replace('.', ',')
        except ValueError:
            pass

    # === Остальное — без изменений (включая текст, даты и т.п.) ===
    return cell


def clean_table(df):
    """Применяет нормализацию ко всем ячейкам DataFrame."""
    return df.map(normalize_numbers)


# === Основной цикл по PDF-файлам ===
for pdf_file in os.listdir(pdf_folder):
    if not pdf_file.lower().endswith('.pdf'):
        continue

    pdf_path = os.path.join(pdf_folder, pdf_file)
    print(f"Читаю файл: {pdf_file}")

    # Извлечение таблиц двумя методами
    try:
        # Для таблиц с линиями (lattice)
        tables_lattice = tabula.read_pdf(
            pdf_path,
            pages='all',
            multiple_tables=True,
            lattice=True,
            stream=False
        )

        # Для таблиц без линий (выравнивание по колонкам)
        tables_stream = tabula.read_pdf(
            pdf_path,
            pages='all',
            multiple_tables=True,
            lattice=False,
            stream=True
        )
    except Exception as e:
        print(f"Ошибка при чтении PDF {pdf_file}: {e}")
        continue

    # Проверяем, найдены ли таблицы
    if not tables_lattice and not tables_stream:
        print(f"⚠️ В файле {pdf_file} не найдено таблиц ни одним методом")
        continue

    # Подготавливаем Excel
    excel_filename = os.path.splitext(pdf_file)[0] + '.xlsx'
    excel_path = os.path.join(output_folder, excel_filename)

    # Соберём все таблицы для группировки
    all_dfs = []

    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # === Lattice Tables: сохраняем на отдельные листы (временно) ===
        for i, table in enumerate(tables_lattice):
            if table.empty or table.shape[1] == 0:
                continue
            header_row = ["Lattice Table " + str(i + 1)] + [""] * (len(table.columns) - 1)
            header_df = pd.DataFrame([header_row], columns=table.columns)
            table_with_header = pd.concat([header_df, table], ignore_index=True)
            sheet_name = f"Lattice_{i + 1}"[:31]
            table_with_header.to_excel(writer, sheet_name=sheet_name, index=False)
            all_dfs.append(('lattice', table_with_header))

        # === Stream Tables: сохраняем на отдельные листы (временно) ===
        for i, table in enumerate(tables_stream):
            if table.empty or table.shape[1] == 0:
                continue
            header_row = ["Stream Table " + str(i + 1)] + [""] * (len(table.columns) - 1)
            header_df = pd.DataFrame([header_row], columns=table.columns)
            table_with_header = pd.concat([header_df, table], ignore_index=True)
            sheet_name = f"Stream_{i + 1}"[:31]
            table_with_header.to_excel(writer, sheet_name=sheet_name, index=False)
            all_dfs.append(('stream', table_with_header))

        # === Создание листа Lattice_ALL ===
        lattice_rows = []
        for source, df in all_dfs:
            if source == 'lattice':
                df_cleaned = clean_table(df)
                rows = [df_cleaned.columns.tolist()] + df_cleaned.values.tolist()
                lattice_rows.extend(rows)
                n_cols = len(df.columns)
                lattice_rows.append([""] * n_cols)
                lattice_rows.append([""] * n_cols)

        if lattice_rows:
            max_cols = max(len(row) for row in lattice_rows)
            padded = [row + [""] * (max_cols - len(row)) for row in lattice_rows]
            df_lattice_all = pd.DataFrame(padded)
            df_lattice_all.to_excel(writer, sheet_name="Lattice_ALL", index=False, header=False)

        # === Создание листа Stream_ALL ===
        stream_rows = []
        for source, df in all_dfs:
            if source == 'stream':
                df_cleaned = clean_table(df)
                rows = [df_cleaned.columns.tolist()] + df_cleaned.values.tolist()
                stream_rows.extend(rows)
                n_cols = len(df.columns)
                stream_rows.append([""] * n_cols)
                stream_rows.append([""] * n_cols)

        if stream_rows:
            max_cols = max(len(row) for row in stream_rows)
            padded = [row + [""] * (max_cols - len(row)) for row in stream_rows]
            df_stream_all = pd.DataFrame(padded)
            df_stream_all.to_excel(writer, sheet_name="Stream_ALL", index=False, header=False)

    # === Удаление всех временных листов, кроме Lattice_ALL и Stream_ALL ===
    wb = load_workbook(excel_path)
    sheets_to_remove = [
        ws.title for ws in wb.worksheets
        if ws.title not in ["Lattice_ALL", "Stream_ALL"]
    ]
    for sheet_name in sheets_to_remove:
        del wb[sheet_name]
    wb.save(excel_path)

    print(f"✅ Сохранено: {excel_path}")
print("\n✅ Обработка всех PDF-файлов завершена!")
