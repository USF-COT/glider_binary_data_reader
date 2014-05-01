from glider_binary_data_reader.glider_bd_reader import GliderBDReader

import argparse
import csv
import sys
import os


def main():
    parser = argparse.ArgumentParser(
        description="Produce a dataset from targeted glider datatypes"
    )
    parser.add_argument(
        '--timestamp_field',
        help='Field to use for timestamp',
        default='m_present_time-timestamp'
    )
    parser.add_argument(
        '--all_rows',
        help=(
            'Produce a CSV file with all datapoint rows and  NaNs where data '
            'is not available.'
        ),
        dest="all_rows",
        action="store_true"
    )
    parser.set_defaults(all_rows=False)
    parser.add_argument(
        '--output_csv_path',
        help='Path for output CSV',
        default='./output.csv'
    )
    parser.add_argument(
        'glider_data_file',
        help='Path to glider data file'
    )
    parser.add_argument(
        'glider_parameters',
        nargs='+',
        help='List of parameters to export to CSV'
    )
    args = parser.parse_args()

    path = os.path.abspath(args.glider_data_file)
    (path, filename) = os.path.split(path)
    extension = filename[filename.rfind('.')+1:-1]

    reader = GliderBDReader(
        path,
        extension,
        [filename]
    )

    parameters = [args.timestamp_field]
    parameters += args.glider_parameters

    with open(args.output_csv_path, 'w') as f:
        writer = csv.DictWriter(
            f,
            parameters,
            restval='NaN',
            extrasaction='ignore'
        )

        for line in reader:
            print line
            if args.all_rows:
                writer.writerow(line)
            else:
                for parameter in args.glider_parameters:
                    if parameter in line:
                        writer.writerow(line)
                        break


if __name__ == '__main__':
    sys.exit(main())
