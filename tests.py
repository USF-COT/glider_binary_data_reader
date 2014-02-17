import unittest

from glider_binary_data_reader.bd_reader import (
    create_glider_BD_ASCII_reader,
    find_glider_BD_headers,
    get_decimal_degrees
)


class TestASCIIReader(unittest.TestCase):

    def setUp(self):
        self.reader = create_glider_BD_ASCII_reader(
            '/home/localuser/glider_binary_data_reader/test_data',
            'tbd'
        )

    def test_single_read(self):
        line = self.reader.stdout.readline()
        self.assertEqual(
            line,
            'dbd_label: DBD_ASC(dinkum_binary_data_ascii)file\n'
        )

    def test_find_headers(self):
        headers = find_glider_BD_headers(self.reader)
        self.assertEqual(
            headers[0]['name'],
            'sci_m_present_secs_into_mission'
        )


class TestUtility(unittest.TestCase):
    def test_decimal_degrees(self):
        decimal_degrees = get_decimal_degrees(-8330.567)
        self.assertEqual(
            decimal_degrees,
            -83.50945
        )


if __name__ == '__main__':
    unittest.main()
