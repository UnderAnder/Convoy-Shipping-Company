from json import dumps

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
        self.write_to_xml()

    def calculate_score(self):
        self.data['score'] = (self.data['fuel_consumption'] * 4.5) / self.data['engine_capacity']
        self.data['score'] = self.data['score'].apply(lambda x: 0 if x > 2 else 1 if x >= 1 else 2)
        self.data['score'] += self.data['fuel_consumption'].apply(lambda x: 2 if x <= 230 / 4.5 else 1)
        self.data['score'] += self.data['maximum_load'].apply(lambda x: 2 if x >= 20 else 0)

    def check_file(self):
        checked_file_name = f'{self.file_name}[CHECKED].csv'
        corrected_data = self.data.replace(to_replace='[^0-9]', value='', regex=True, inplace=False)
        mod_count = self.data.compare(corrected_data, 'index').count().sum() // 2
        self.data = corrected_data.apply(pd.to_numeric)
        self.data.to_csv(checked_file_name, index=None)
        print(f"{mod_count} cell{'s were' if mod_count != 1 else ' was'} corrected in {checked_file_name}")

    def write_to_csv(self):
        file_name = f'{self.file_name}.csv'
        self.data.to_csv(file_name, index=None)
        print(f"{self.size} line{'s were' if self.size != 1 else ' was'} added to {file_name}")

    def write_to_sql(self):
        self.calculate_score()
        with sqlite3.connect(f"{self.file_name}.s3db") as conn: 
            types = {c: 'INTEGER PRIMARY KEY' if c == 'vehicle_id' else 'INTEGER NOT NULL' for c in self.data.columns}
            self.data.to_sql('convoy', conn, index=False, dtype=types, if_exists='replace')
        print(f"{self.size} record{'s were' if self.size != 1 else ' was'} inserted into {self.file_name}.s3db")

    def write_to_json(self):
        gt_3 = self.data.loc[self.data['score'] > 3]
        gt_3.drop(columns='score', inplace=True)
        res = {'convoy': gt_3.to_dict(orient='records')}
        with open(f'{self.file_name}.json', 'w') as f:
            f.write(dumps(res))
        print(f"{gt_3.shape[0]} vehicle{'s were' if gt_3.shape[0] != 1 else ' was'} saved into {self.file_name}.json")

    def write_to_xml(self):
        def xml_row_builder(row):
            xml = ['<{0}>{1}</{0}>'.format(field, row[field]) for field in row.index]
            xml.insert(0, '<vehicle>')
            xml.append('</vehicle>')
            return '\n'.join(xml)

        lte_3 = self.data.loc[self.data['score'] <= 3]
        lte_3.drop(columns='score', inplace=True)
        with open(f'{self.file_name}.xml', 'w') as f:
            print('<convoy>', file=f)
            print('\n'.join(lte_3.apply(xml_row_builder, axis=1)), file=f)
            print('</convoy>', file=f)
        print(f"{lte_3.shape[0]} vehicle{'s were' if lte_3.shape[0] != 1 else ' was'} saved into {self.file_name}.xml")


if __name__ == '__main__':
    Convoy().controller()
