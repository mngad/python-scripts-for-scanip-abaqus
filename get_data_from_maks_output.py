"""Combines data from the mask information output csvs."""


import sys
import pandas
import os
from xlsxwriter import Workbook


def combine_csvs(folder):
    """Combine the csvs."""
    list_of_files = os.listdir(folder)
    list_of_files.sort()
    new_file_list = []
    for file in list_of_files:
        if 'MaskStatistics.csv' in file:
            new_file_list.append(file)

    data_dict = {}
    for file in new_file_list:
        print(folder + '\\' + file)
        data = pandas.read_csv(folder + '\\' + file, header=1,)
        # print(data.iloc[0])
        data_dict[file] = data
        header = list(data.columns.values)

    # print(header)
    return data_dict, header


def select_row_of_interest(namofrow, data):
    """Select the rows that contain vb info."""
    vb_dict = {}
    for dat in data.keys():
        # print(data[dat].iloc[0])
        for i in range(0, data[dat]["Name"].count()):
            if namofrow in data[dat]["Name"][i]:
                vb_row = data[dat].loc[i].tolist()

        vb_dict[dat] = vb_row

    return vb_dict


def save_as_excel(folder, vb_dict, header):
    """Save to an Excel file."""
    wb = Workbook(folder + "/combinedcsvs.xlsx")
    ws = wb.add_worksheet("Sheety")

    print(header)
    row = 0
    col = 0

    for title in header:
        ws.write(row, col, title)
        col += 1
    row += 1
    for vb in vb_dict.keys():
        col = 0
        ws.write(row, col, vb)
        col += 1
        for i in range(1, len(vb_dict[vb])):
            ws.write(row, col, vb_dict[vb][i])
            col += 1
        row += 1
    wb.close()


if __name__ == "__main__":

    data, header = combine_csvs(sys.argv[1])
    vb_dict = select_row_of_interest('Vertebra', data)
    save_as_excel(sys.argv[1], vb_dict, header)
