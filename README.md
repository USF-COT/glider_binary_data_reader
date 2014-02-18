# Glider Binary Data Reader

Reads and merges Teledyne Webb Slocum Glider data from *bd flight and science files.

## Installation

```
git clone https://github.com/USF-COT/glider_binary_data_reader.git
sudo python setup.py install
```

## Basic Usage

```
from glider_binary_data_reader.glider_bd_reader import (
    GliderBDReader,
    MergedGliderBDReader
)

flightReader = GliderBDReader(
    '<path to data directory>',
    'sbd'
)
scienceReader = GliderBDReader(
    '<path to data directory>',
    'tbd'
)
reader = MergedGliderBDReader(flightReader, scienceReader)
for value in reader:
    print value
```

This library depends on having dbd2asc, a utility from Teledyne Webb, in your system path.
