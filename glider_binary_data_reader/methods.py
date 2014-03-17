import subprocess

from glob import glob
from itertools import izip

import tempfile


def generate_tmpfile(processArgs):
    tmpFile = tempfile.TemporaryFile()
    process = subprocess.Popen(processArgs, stdout=tmpFile, stderr=tmpFile)
    process.wait()
    tmpFile.seek(0)

    return tmpFile, process.returncode


def process_all_of_type(path, fileType):
    processArgs = ['dbd2asc', '-c', '/tmp']

    filesWildCard = '%s/*.%s' % (path, fileType)
    processArgs.extend(glob(filesWildCard))

    tmpFile, returncode = generate_tmpfile(processArgs)

    return tmpFile


def process_file_list(path, fileType, fileNames):
    processArgs = ['dbd2asc', '-c', '/tmp']

    for fileName in fileNames:
        filePath = '%s/%s' % (path, fileName)
        processArgs.append(filePath)

    tmpFile, returncode = generate_tmpfile(processArgs)

    # Fallback in case the cache is not available
    if returncode == 1:
        # Generate cache by processing all files available of type
        process_all_of_type(path, fileType)
        # Reprocess the file list
        tmpFile, returncode = generate_tmpfile(processArgs)

    return tmpFile


def create_glider_BD_ASCII_reader(path, fileType, fileNames=None):
    """Creates a glider binary data reader

    Arguments:
    path - path to directory containing glider binary files.
    fileType - type of *bd files to process.
        Examples: 'dbd', 'ebd', 'sbd', 'tbd', 'mbd', or 'nbd'
    fileNames - optional list of files to process.
        If not specified, all files of type fileType in
        path will be processed.

    Returns a subprocess.Popen class to a dbd2asc call
    """

    if fileNames is None:
        return process_all_of_type(path, fileType)
    else:
        return process_file_list(path, fileType, fileNames)


def find_glider_BD_headers(reader):
    """Finds and returns available headers in a set of glider data files

    Arguments:
    reader - A raw glider binary data reader of type subprocess.Popen
    """

    # Bleed off extraneous headers
    # Stop when sci_m_present_time is found
    line = reader.readline()
    while len(line) > 0 and line.find('m_present_time') == -1:
        line = reader.readline()

    if line is '':
        raise EOFError('No headers found before end of file.')

    headersTemp = line.split(' ')

    unitsLine = reader.readline()
    if unitsLine is not None:
        unitsTemp = unitsLine.split(' ')
    else:
        raise EOFError('No units found before end of file.')

    headers = []
    for header, unit in izip(headersTemp, unitsTemp):
        description = {
            'name': header,
            'units': unit,
            'is_point': header.find('lat') != -1 or header.find('lon') != -1
        }
        headers.append(description)

    # Remove extraneous bytes line
    reader.readline()

    return headers


def get_decimal_degrees(lat_lon):
    """Converts glider gps coordinate ddmm.mmm to decimal degrees dd.ddd

    Arguments:
    lat_lon - A floating point latitude or longitude in the format ddmm.mmm
        where dd's are degrees and mm.mmm is decimal minutes.

    Returns decimal degrees float
    """

    if lat_lon == 0:
        return -1

    lat_lon_string = str(lat_lon)
    decimal_place = lat_lon_string.find('.')
    if decimal_place != -1:
        str_dec = lat_lon_string[0:decimal_place-2]
        str_dec_fractional = lat_lon_string[decimal_place-2:]
    elif abs(lat_lon) < 181:
        if(abs(lat_lon/100) > 100):
            str_dec = lat_lon_string[0:3]
            str_dec_fractional = lat_lon_string[3:]
        else:
            str_dec = lat_lon_string[0:2]
            str_dec_fractional = lat_lon_string[2:]
    else:
        return -1

    dec = float(str_dec)
    dec_fractional = float(str_dec_fractional)
    if dec < 0:
        dec_fractional *= -1
    return dec + dec_fractional/60


def map_line(reader, headers):
    """Maps all non-NaN values in a glider data file to a known header

    Arguments:
    reader - A subprocess.Popen with headers discovered
    headers - Headers discovered in data file already
    """

    readings = {}

    line = reader.readline()

    if len(line) == 0:
        raise EOFError('That\'s all the data!')

    line = line.rstrip()

    value_strings = line.split(' ')
    for i, string in enumerate(value_strings):
        if string != 'NaN':
            value = float(string)

            if i < len(headers):
                if headers[i]['is_point']:
                    value = get_decimal_degrees(value)
                key = headers[i]['name'] + "-" + headers[i]['units']
                readings[key] = value

    return readings
