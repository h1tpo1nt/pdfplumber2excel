import pdfplumber
import pandas as pd
import os


def clean_cell(value):
    """Функция для обработки содержимого каждой ячейки"""
    if not value:
        return value

    # Убираем лишние пробелы
    value = value.strip()

    # Если значение в скобках — убираем скобки и делаем число отрицательным
    if value.startswith('(') and value.endswith(')'):
        number = value[1:-1]
        return f'-{number}'

    # Заменяем точку на запятую в десятичных числах, если нет запятой
    if '.' in value and ',' not in value:
        return value.replace('.', ',')

    return value


def extract_all_tables_to_single_csv(pdf_path):
    # Получаем имя файла без расширения
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_file = f"{base_name}.csv"  # создаём имя выходного файла

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"[INFO] Обрабатываем файл: {pdf_path}")
        print(f"[INFO] Всего страниц: {total_pages}")

        with open(output_file, 'w', encoding='utf-8') as f:
            table_count = 0

            for page_num, page in enumerate(pdf.pages, start=1):
                print(f"\n[+] Страница {page_num} из {total_pages}")
                tables = page.extract_tables()

                if not tables:
                    print("  └── Таблиц на странице не найдено")
                    continue

                print(f"  └── Найдено таблиц: {len(tables)}")

                for j, table in enumerate(tables):
                    # Добавляем маркер начала таблицы
                    f.write(f'Table Start - Page {page_num}, Table {j + 1}\n')

                    # Преобразуем в DataFrame
                    df = pd.DataFrame(table[1:], columns=table[0])

                    # Очищаем заголовки от лишних пробелов
                    df.columns = df.columns.str.strip()

                    # Применяем обработку к каждой ячейке
                    df = df.applymap(clean_cell)

                    # Сохраняем как CSV строка
                    df.to_csv(f, index=False, header=True, lineterminator='\n')

                    # Добавляем маркер конца таблицы
                    f.write(f'Table End - Page {page_num}, Table {j + 1}\n\n')
                    table_count += 1

            print(f"\n✅ Всего извлечено таблиц: {table_count}")

    print(f"[INFO] Все таблицы сохранены в: {output_file}")
    return output_file


# === Функция для обработки всех PDF-файлов в папке ===
def process_pdfs_in_folder(folder_path):
    # Создаём папку для результатов (если её нет)
    output_folder = os.path.join(folder_path, "csv_results")
    os.makedirs(output_folder, exist_ok=True)

    # Ищем все PDF-файлы в папке
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print("[INFO] В папке не найдено PDF-файлов.")
        return

    print(f"[INFO] Найдено PDF-файлов: {len(pdf_files)}")
    for i, filename in enumerate(pdf_files, 1):
        print(f"\n📁 [{i}/{len(pdf_files)}] Обработка файла: {filename}")
        pdf_path = os.path.join(folder_path, filename)
        result_file = extract_all_tables_to_single_csv(pdf_path)

        # Перемещаем результат в папку csv_results
        output_name = os.path.basename(result_file)
        new_result_path = os.path.join(output_folder, output_name)
        os.rename(result_file, new_result_path)
        print(f"[INFO] Результат перемещён в: {new_result_path}")


# === Пример использования ===
if __name__ == "__main__":
    folder = "/content/otchetnost"  # замените на путь к вашей папке
    process_pdfs_in_folder(folder)
