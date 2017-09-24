import unittest
import os
from term_weather.weather import Weather
from contextlib import contextmanager
from io import StringIO
import sys

XML_ASSETS_PATH = os.path.join('assets', 'Noreg_Telemark_Sauherad_Gvarv')


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class TestWeather(unittest.TestCase):
    def test_load_from_file(self):
        weather = Weather('Noreg/Telemark/Sauherad/Gvarv', auto_load=False)
        weather.force_load_from_files(
            forecast_file=os.path.join(XML_ASSETS_PATH, 'forecast.xml'),
            precipitation_now_file=os.path.join(XML_ASSETS_PATH, 'varsel_nu.xml'))

        with captured_output() as (out, err):
            weather.now()
        output = out.getvalue()
        self.assertIn('Gvarv, Norway', output)


if __name__ == '__main__':
    unittest.main()