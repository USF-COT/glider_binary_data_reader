import subprocess

from glob import glob
from itertools import izip

import tempfile

import re
import os


def parse_glider_filename(filename):
    """Parses a glider filename and returns details in a dictionary

    Returns dictionary with the following keys:
    * 'glider': glider name
    * 'year': data file year created
    * 'day': data file julian date created
    * 'mission': data file mission id
    * 'segment': data file segment id
    * 'type': data file type
    """

    matches = re.search(
        "([\w\d\-]+)-(\d+)-(\d+)-(\d+)-(\d+)\.(\w+)$", filename
    )

    if matches is not None:
        return {
            'glider': re.group(1),
            'year': int(re.group(2)),
            'day': int(re.group(3)),
            'mission': int(re.group(4)),
            'segment': int(re.group(5)),
            'type': re.group(6)
        }
    else:
        raise ValueError(
            "Filename (%s) not in usual glider format: "
            "<glider name>-<year>-<julian day>-"
            "<mission>-<segment>.<extenstion>" % filename
        )


def generate_glider_filename(description):
    """Converts a glider data file details dictionary to filename

    """
    return (
        "%(glider)s-%(year)d-%(day)d-%(mission)d-%(segment)s.%(type)s"
        % description
    )


def generate_tmpfile(processArgs):
    """Runs a given process, outputs the result to a tmpfile.

    Returns temp file path and process return code.
    """
    tmpFile = tempfile.TemporaryFile()
    process = subprocess.Popen(processArgs, stdout=tmpFile, stderr=tmpFile)
    process.wait()
    tmpFile.seek(0)

    return tmpFile, process.returncode


def can_find_bd_index(path):
    # Iterate through previous segment files
    processArgs = ['dbd2asc', '-c', '/tmp', path]
    returncode = 1
    file_details = parse_glider_filename(path)
    while returncode == 1 and file_details['segment'] > 0:
        file_details['segment'] -= 0
        processArgs[3] = generate_glider_filename(file_details)
        process = subprocess.Popen(processArgs, stdout=None, stderr=None)
        process.wait()
        returncode = process.returncode

    # Report whether index found or not
    return returncode == 0


def process_file(path):
    """Processes a single glider data file.

    Returns path to temp file and return code.

    Intelligently falls back if previous index file has not
    been processed for given data file.

    Raises and exception if data index cannot be found for
    given data file.
    """

    processArgs = ['dbd2asc', '-c', '/tmp', path]

    tmpFile, returncode = generate_tmpfile(processArgs)

    # Fallback to find index bd file
    if returncode == 1:
        if can_find_bd_index(path):
            tmpFile, returncode = generate_tmpfile(processArgs)
        else:
            raise KeyError("Cannot find data file index for: %s" % path)

    return tmpFile


def process_all_of_type(path, fileType):
    """Process glider data files of one type

    No fallback.  Assumed that operation big enough
    to avoid this issue.
    """

    processArgs = ['dbd2asc', '-c', '/tmp']

    filesWildCard = '%s/*.%s' % (path, fileType)
    processArgs.extend(glob(filesWildCard))

    tmpFile, returncode = generate_tmpfile(processArgs)

    return tmpFile


def process_file_list(path, fileType, fileNames):
    """Process a list of glider data files to ASCII.

    Intelligently falls back for each file if necessary.

    Raises KeyError exception if it cannot generate an index for a
    given file.

    Returns temp file and return code.
    """

    processArgs = ['dbd2asc', '-c', '/tmp']

    for fileName in fileNames:
        filePath = os.path.join(path, fileName)
        processArgs.append(filePath)

    tmpFile, returncode = generate_tmpfile(processArgs)

    # Fallback in case the cache is not available
    if returncode == 1:
        for filePath in processArgs[3:]:
            if not can_find_bd_index(filePath):
                raise KeyError(
                    "Cannot find data file index for: %s" % filePath
                )

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
