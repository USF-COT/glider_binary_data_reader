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
        '--timestamp_file',
        help='Field to use for timestamp',
        default='m_present_time-timestamp'
    )
    parser.add_argument(
        'glider_data_file',
        help='Path to glider data file'
    )
    parser.add_argument(
        'output_csv_path',
        help='Path for output CSV'
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

    parameters = [args.timestamp_file]
    parameters += args.glider_parameters

    with open(args.output_csv_path, 'w') as f:
        writer = csv.DictWriter(
            f,
            parameters,
            restval='',
            extrasaction='ignore'
        )

        for line in reader:
            for parameter in args.glider_parameters:
                if parameter in line:
                    writer.writerow(line)
                    break


if __name__ == '__main__':
    sys.exit(main())
