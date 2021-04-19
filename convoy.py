import pandas as pd


def main():
    input_file_name = input('Input file name\n')
    csv_file_name = f"{input_file_name.split('.')[0]}.csv"
    data = pd.read_excel(input_file_name, sheet_name='Vehicles', dtype=str)
    data.to_csv(csv_file_name, index=None)
    count_line = data.shape[0]
    print(f"{count_line} {'lines were' if count_line > 1 else 'line was'} imported to {csv_file_name}")


if __name__ == '__main__':
    main()
