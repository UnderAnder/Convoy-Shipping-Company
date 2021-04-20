import json

import pandas as pd
import sqlite3


class Convoy:
    def __init__(self):
        self.data, self.file_name, self.file_type = self.input_file()
        self.size = self.data.shape[0]

    @staticmethod
    def input_file():
        while raw_input := input('Input file name\n'):
            if raw_input.endswith('xlsx'):
                return pd.read_excel(raw_input, sheet_name='Vehicles', dtype=str), raw_input.removesuffix('.xlsx'), 'xlsx'
            elif raw_input.endswith('csv'):
                file_type = 'csv' if raw_input.find('[CHECKED]') == -1 else 'checked'
                return pd.read_csv(raw_input), raw_input.removesuffix('.csv').removesuffix('[CHECKED]'), file_type
            elif raw_input.endswith('s3db'):
                with sqlite3.connect(raw_input) as conn:
                    return pd.read_sql('SELECT * FROM convoy', conn), raw_input.removesuffix('.s3db'), 's3db'

    def controller(self):
        if self.file_type == 'checked':
            self.write_to_sql()
        elif self.file_type == 'csv':
            self.check_file()
            self.write_to_sql()
        elif self.file_type == 'xlsx':
            self.write_to_csv()
            self.check_file()
            self.write_to_sql()
        self.write_to_json()
        
    def check_file(self):
        checked_file_name = f'{self.file_name}[CHECKED].csv'
        corrected_data = self.data.replace(to_replace='[^0-9]', value='', regex=True, inplace=False)
        mod_count = self.data.compare(corrected_data, 'index').count().sum() // 2
        self.data = corrected_data
        self.data.to_csv(checked_file_name, index=None)
        print(f"{mod_count} cell{'s were' if mod_count > 1 else ' was'} corrected in {checked_file_name}")

    def write_to_csv(self):
        file_name = f'{self.file_name}.csv'
        self.data.to_csv(file_name, index=None)
        print(f"{self.size} line{'s were' if self.size > 1 else ' was'} added to {file_name}")

    def write_to_sql(self):
        with sqlite3.connect(f"{self.file_name}.s3db") as conn: 
            types = {c: 'INTEGER PRIMARY KEY' if c == 'vehicle_id' else 'INTEGER NOT NULL' for c in self.data.columns}
            self.data.to_sql('convoy', conn, index=False, dtype=types, if_exists='replace')
        print(f"{self.size} record{'s were' if self.size > 1 else ' was'} inserted into {self.file_name}.s3db")

    def write_to_json(self):
        # data.to_json(path_or_buf=f'{file_name}.json', orient='records') # array 'convoy' needed for tests
        res = {'convoy': self.data.to_dict(orient='records')}
        with open(f'{self.file_name}.json', 'w') as f:
            f.write(json.dumps(res))
        print(f"{self.size} vehicle{'s were' if self.size > 1 else ' was'} saved into {self.file_name}.json")


if __name__ == '__main__':
    Convoy().controller()
