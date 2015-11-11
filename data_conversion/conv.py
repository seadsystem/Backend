# Reads time-series data from SEADS database
#
# data format must:
#     - be in CSV form
#     - have commas as delimiter
#     - have first row as key for collums. Must be exactly:
#
#         serial,type,data,time,device
#
# Usage: python3 conv.py input.csv [output.csv]
#
#   if no output file is specified, input-fixed.csv will be used
#
# NOTE: to change delimiter for CSV, change global variable in main
#
#
# To get data from server in this format use a command like:
#
# \copy data_raw TO '~/data_raw_dump_2014-10-28.csv' DELIMITER ',' CSV HEADER;

import csv, sys
from decimal import *


def name_out(in_filename):
    split = in_filename.rfind('.')
    return in_filename[:split] + '-fixed' + in_filename[split:]

def get_key(in_filename):
    with open(in_filename, 'r') as in_file:
        return csv.reader(in_file).__next__()

# uses Decimals instead of float to prevent miniscule changes to data
def fix_row(in_row):
    try:
        out_row = in_row
        data_val = Decimal(in_row['data'])
        # divide by propper factor for data type to get readable data
        if row['type'] == 'F':      # Frequency
            data_val = data_val / Decimal(10 ** 8)
        elif row['type'] == 'V':    # Voltage
            data_val = data_val / Decimal(10 ** 6)
        elif row['type'] == 'P':    # Power
            data_val = data_val / Decimal(10 ** 9)
        elif row['type'] == 'I':    # Current
            data_val = data_val / Decimal(10 ** 9)
        out_row['data'] = str(data_val)
        return out_row
    except KeyError:
        sys.exit('bad data key. Does you data have a fieldnames header?')


if __name__ == "__main__":
    # set delimiter
    delimiter = ','
    # parse args
    in_filename = ''
    out_filename = ''
    prog_name = sys.argv[0]
    args = sys.argv[1:]
    if len(args) == 0 or len(args) > 2:
        sys.exit('Usage: python3 ' + prog_name +
                 ' input_file [output_file]')
    else:
        in_filename = args[0]
        if len(args) == 1:
            out_filename = name_out(in_filename)
        else:
            out_filename = args[1]

    # open source and output files for operation
    data_key = get_key(in_filename)
    with open(in_filename, 'r') as in_file:
        with open (out_filename, 'w') as out_file:
            reader = csv.DictReader(in_file, delimiter=delimiter)
            writer = csv.DictWriter(out_file, fieldnames=data_key)
            for row in reader:
                writer.writerow(fix_row(row))
