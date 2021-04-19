import pandas as pd
import sqlite3


def input_file():
    while raw_input := input('Input file name\n'):
        if raw_input.endswith('xlsx'):
            return pd.read_excel(raw_input, sheet_name='Vehicles', dtype=str), raw_input.removesuffix('.xlsx'), True
        elif raw_input.endswith('csv'):
            return pd.read_csv(raw_input), raw_input.removesuffix('.csv'), False


def correct_data(data):
    corrected_data = data.replace(to_replace='[^0-9]', value='', regex=True, inplace=False)
    modification_count = data.compare(corrected_data, 'index').count().sum() // 2
    return corrected_data, modification_count


def check_file(data, file_name, xlsx):
    checked_file_name = f'{file_name}[CHECKED].csv'
    if xlsx:
        file_name = f'{file_name}.csv'
        count_line = data.shape[0]
        data.to_csv(file_name, index=None)
        print(f"{count_line} {'lines were' if count_line > 1 else 'line was'} added to {file_name}")
    corrected, corrected_count = correct_data(data)
    corrected.to_csv(checked_file_name, index=None)
    print(f"{corrected_count} {'cells were' if corrected_count > 1 else 'cell was'} corrected in {checked_file_name}")
    return corrected


def write_to_sql(data, file_name):
    conn = sqlite3.connect(f'{file_name}.s3db')
    types = {col: 'INTEGER PRIMARY KEY' if col == 'vehicle_id' else 'INTEGER NOT NULL' for col in data.columns}
    data.to_sql('convoy', conn, index=False, dtype=types)
    count_line = data.shape[0]
    print(f"{count_line} {'records were' if count_line > 1 else 'record was'} inserted into {file_name}.s3db")


def main():
    data, file_name, xlsx = input_file()
    if not file_name.endswith('[CHECKED]'):
        data = check_file(data, file_name, xlsx)
    write_to_sql(data, file_name.removesuffix('[CHECKED]'))


if __name__ == '__main__':
    main()
