import pandas as pd


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


def main():
    data, file_name, exel = input_file()
    checked_file_name = f'{file_name}[CHECKED].csv'
    file_name = f'{file_name}.csv'

    count_line = data.shape[0]
    data.to_csv(file_name, index=None)

    corrected, corrected_count = correct_data(data)
    corrected.to_csv(checked_file_name, index=None)

    print(f"{count_line} {'lines were' if count_line > 1 else 'line was'} added to {file_name}") if exel else None
    print(f"{corrected_count} {'cells were' if corrected_count > 1 else 'cell was'} corrected in {checked_file_name}")


if __name__ == '__main__':
    main()
