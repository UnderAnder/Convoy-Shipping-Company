import json

import pandas as pd
import sqlite3


def input_file():
    while raw_input := input('Input file name\n'):
        if raw_input.endswith('xlsx'):
            return pd.read_excel(raw_input, sheet_name='Vehicles', dtype=str), raw_input.removesuffix('.xlsx'), True
        elif raw_input.endswith('csv'):
            return pd.read_csv(raw_input), raw_input.removesuffix('.csv'), False
        elif raw_input.endswith('s3db'):
            conn = sqlite3.connect(raw_input)
            return pd.read_sql('SELECT * FROM convoy', conn), raw_input, False


def correct_data(data):
    corrected_data = data.replace(to_replace='[^0-9]', value='', regex=True, inplace=False)
    modification_count = data.compare(corrected_data, 'index').count().sum() // 2
    return corrected_data, modification_count


def check_file(data, file_name, xlsx):
    checked_file_name = f'{file_name}[CHECKED].csv'
    if xlsx:
        file_name = f'{file_name}.csv'
        data.to_csv(file_name, index=None)
        print(f"{data.shape[0]} {'lines were' if data.shape[0] > 1 else 'line was'} added to {file_name}")
    corrected, corrected_count = correct_data(data)
    corrected.to_csv(checked_file_name, index=None)
    print(f"{corrected_count} {'cells were' if corrected_count > 1 else 'cell was'} corrected in {checked_file_name}")
    return corrected


def write_to_sql(data, file_name):
    conn = sqlite3.connect(f"{file_name}.s3db")
    types = {col: 'INTEGER PRIMARY KEY' if col == 'vehicle_id' else 'INTEGER NOT NULL' for col in data.columns}
    data.to_sql('convoy', conn, index=False, dtype=types)
    print(f"{data.shape[0]} {'records were' if data.shape[0] > 1 else 'record was'} inserted into {file_name}.s3db")
    conn.close()

def write_to_json(data, file_name):
    # data.to_json(path_or_buf=f'{file_name}.json', orient='records') # array 'convoy' needed for tests
    res = {'convoy': data.to_dict(orient='records')}
    with open(f'{file_name}.json', 'w') as f:
        f.write(json.dumps(res))
    print(f"{data.shape[0]} {'vehicles were' if data.shape[0] > 1 else 'vehicle was'} saved into {file_name}.json")


def main():
    data, file_name, xlsx = input_file()
    if not file_name.endswith('s3db'):
        if not file_name.endswith('[CHECKED]'):
            data = check_file(data, file_name, xlsx)
        file_name = file_name.removesuffix('[CHECKED]')
        write_to_sql(data, file_name)
    write_to_json(data, file_name.removesuffix('.s3db'))


if __name__ == '__main__':
    main()
