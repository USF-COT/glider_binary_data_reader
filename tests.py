import unittest

from glider_binary_data_reader.methods import (
    create_glider_BD_ASCII_reader,
    find_glider_BD_headers,
    get_decimal_degrees
)

from glider_binary_data_reader.glider_bd_reader import (
    GliderBDReader,
    MergedGliderBDReader
)


class TestASCIIReader(unittest.TestCase):

    def setUp(self):
        self.reader = create_glider_BD_ASCII_reader(
            'test_data',
            'sbd'
        )

    def test_single_read(self):
        line = self.reader.readline()
        self.assertEqual(
            line,
            'dbd_label: DBD_ASC(dinkum_binary_data_ascii)file\n'
        )

    def test_find_headers(self):
        headers = find_glider_BD_headers(self.reader)
        self.assertEqual(
            'c_heading',
            headers[0]['name']
        )


class TestUtility(unittest.TestCase):
    def test_decimal_degrees(self):
        decimal_degrees = get_decimal_degrees(-8330.567)
        self.assertEqual(
            decimal_degrees,
            -83.50945
        )


class TestBDReader(unittest.TestCase):

    def setUp(self):
        self.reader = GliderBDReader(
            'test_data',
            'tbd'
        )

    def test_iteration(self):
        for value in self.reader:
            self.assertIn(
                'sci_m_present_secs_into_mission-sec',
                value
            )


class TestMergedGliderDataReader(unittest.TestCase):

    def setUp(self):
        flightReader = GliderBDReader(
            'test_data',
            'sbd'
        )
        scienceReader = GliderBDReader(
            'test_data',
            'tbd'
        )
        self.reader = MergedGliderBDReader(flightReader, scienceReader)

    def test_iteration(self):
        for value in self.reader:
            print value
            time_present = (
                'sci_m_present_secs_into_mission-sec' in value
                or 'm_present_secs_into_mission-sec' in value
            )
            self.assertTrue(time_present)


if __name__ == '__main__':
    unittest.main()
