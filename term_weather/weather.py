import xmltodict
import datetime
import os
from term_weather.concurrent_download import concurrent_download
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


class OutOfDateError(Exception):
    pass


class CacheMissError(Exception):
    pass


class Weather:
    BASE_URLS = {'nb': "https://www.yr.no/sted/",
                 'nn': "https://www.yr.no/stad/",
                 'en': "https://www.yr.no/place/"}
    FORECAST_FILE_NAME = 'forecast.xml'
    PRECIPITATION_NOW_FILE_NAME = 'varsel_nu.xml'
    DEGREES_SYMBOL = '°'
    PRECIPITATION_TIME_STAMPS_ROW = [' 0', ' ', "'", ' ', '30', ' ', "'", ' ', '60', ' ', "'", ' ', '90']
    PRECIPITATION_MAX = 5

    def __init__(self, location, auto_load=True, language='en', cache_dir='/tmp/term_weather'):
        """
        Create a interface to the Yr weather xml api http://om.yr.no/verdata/xml/
        :param place: String on the format as inside brackets: yr.no/stad/[Noreg/Telemark/Sauherad/Gvarv]
        :param language: language, possible are [en, nb, nn], default en
        :param cache_dir: path to cache location

        >>> Weather("Noreg/Telemark/Sauherad/")


        """
        self.cache_dir = cache_dir
        self.location = location
        self.current_cache_dir = os.path.join(self.cache_dir, self.place_to_dir_name(self.location))
        self.base_server_url = self.BASE_URLS[language]
        self.forecast_data = None
        self.precipitation_now_data = None

        if auto_load:
            self._load_forecast_data()

    def now(self, show_precipitation_now=True, show_forecast_row=True, bar_height=5, bar_width=5):
        """
        Print out a <nice> representation of the forecast around now
        :param show_precipitation_now:
        :param show_forecast_row:
        :param bar_height:
        :param bar_width:
        :return:
        """
        if show_forecast_row:
            self._print_forecast()
        if show_precipitation_now:
            self._plot_precipitation(bar_height, bar_width)
        self._print_credit()

    def force_load_from_files(self, forecast_file, precipitation_now_file):
        with open(forecast_file) as f:
            forecast_xml_data = f.read()
            self.forecast_data = xmltodict.parse(forecast_xml_data)
        with open(precipitation_now_file) as f:
            precipitation_xml_data = f.read()
            self.precipitation_now_data = xmltodict.parse(precipitation_xml_data)

        self._parse_forecast()
        self._parse_precipitation_now_forecast()

    def _load_forecast_data(self):
        if not os.path.exists(self.current_cache_dir):
            os.makedirs(self.current_cache_dir)

        # To comply with http://om.yr.no/verdata/vilkar/ we have to try to load from cache first
        try:
            self._load_from_cache()
        except OutOfDateError:
            self._load_from_server()
        except CacheMissError:
            self._load_from_server()

    def _load_from_cache(self):
        """
        Try to load from cache, if the forecast has expired or we do not have anything in the cache we
        raise CacheMissError or OutOfDateError
        :return:
        """
        try:
            with open(os.path.join(self.current_cache_dir, self.FORECAST_FILE_NAME)) as f:
                forecast_xml_data = f.read()
                self.forecast_data = xmltodict.parse(forecast_xml_data)
            with open(os.path.join(self.current_cache_dir, self.PRECIPITATION_NOW_FILE_NAME)) as f:
                precipitation_xml_data = f.read()
                self.precipitation_now_data = xmltodict.parse(precipitation_xml_data)
        except FileNotFoundError:
            raise CacheMissError()
        self._parse_forecast()
        self._parse_precipitation_now_forecast()
        if self.next_update < datetime.datetime.now():
            raise OutOfDateError()

    def _load_from_server(self):
        """
        Load the data from server. Try to do this in a concurrent way since we want two files
        :return:
        """
        url_dict = {'forecast': os.path.join(self.base_server_url, self.location, self.FORECAST_FILE_NAME),
                    'now': os.path.join(self.base_server_url, self.location, self.PRECIPITATION_NOW_FILE_NAME)}
        content_dict = concurrent_download(url_dict)

        with open(os.path.join(self.current_cache_dir, self.FORECAST_FILE_NAME), 'w') as f:
            f.write(content_dict['forecast'])
        with open(os.path.join(self.current_cache_dir, self.PRECIPITATION_NOW_FILE_NAME), 'w') as f:
            f.write(content_dict['now'])

        self.forecast_data = xmltodict.parse(content_dict['forecast'])
        self.precipitation_now_data = xmltodict.parse(content_dict['now'])
        self._parse_forecast()
        self._parse_precipitation_now_forecast()

    def _parse_forecast(self):
        """
        Parse the forecast dictionary and save internally
        :return:
        """
        first_forecast = dict(self.forecast_data["weatherdata"]["forecast"]["tabular"]["time"][0])
        self.location_name = self.forecast_data["weatherdata"]["location"]["name"]
        self.location_country = self.forecast_data["weatherdata"]["location"]["country"]
        self.time_from = datetime.datetime.strptime(first_forecast['@from'], DATE_FORMAT)
        self.time_to = datetime.datetime.strptime(first_forecast['@to'], DATE_FORMAT)
        self.precipitation = float(first_forecast['precipitation']["@value"])

        # Seems like if precipitation == 0, then min and max are not present
        try:
            self.precipitation_min = float(first_forecast['precipitation']["@minvalue"])
        except KeyError:
            self.precipitation_min = self.precipitation
        try:
            self.precipitation_max = float(first_forecast['precipitation']["@maxvalue"])
        except KeyError:
            self.precipitation_max = self.precipitation

        self.temperature = float(first_forecast['temperature']['@value'])
        self.temperature_unit = first_forecast['temperature']['@unit']
        self.pressure = float(first_forecast['pressure']['@value'])
        self.pressure_unit = first_forecast['pressure']['@unit']
        self.wind_speed = float(first_forecast['windSpeed']['@mps'])
        self.wind_speed_name = first_forecast['windSpeed']['@name']
        self.wind_direction = float(first_forecast['windDirection']['@deg'])
        self.wind_direction_code = first_forecast['windDirection']['@code']
        self.wind_direction_name = first_forecast['windDirection']['@name']
        self.symbol_number = int(first_forecast['symbol']['@number'])
        self.symbol_name = first_forecast['symbol']['@name']
        self.credit_text = self.forecast_data["weatherdata"]['credit']['link']['@text']
        self.credit_url = self.forecast_data["weatherdata"]['credit']['link']['@url']

    def _parse_precipitation_now_forecast(self):
        self.precipitation_now_forecast = []
        for forecast in self.precipitation_now_data["weatherdata"]["forecast"]["time"]:
            self.precipitation_now_forecast.append(float(forecast["precipitation"]["@value"]))

        self.last_update = datetime.datetime.strptime(
            self.precipitation_now_data["weatherdata"]["meta"]["lastupdate"], DATE_FORMAT)
        self.next_update = datetime.datetime.strptime(
            self.precipitation_now_data["weatherdata"]["meta"]["nextupdate"], DATE_FORMAT)

    def _print_forecast(self):
        print(self.location_name + ', ' + self.location_country, end=': ')
        print("{:02d}:{:02d}-{:02d}:{:02d} | {}{} | {}-{}mm | {}m/s {} | {}{}".format(
            self.time_from.hour, self.time_from.minute,
            self.time_to.hour, self.time_to.minute,
            self.temperature, self.DEGREES_SYMBOL,
            self.precipitation_min, self.precipitation_max,
            self.wind_speed, self.wind_speed_name,
            self.pressure, self.pressure_unit))

    def _plot_precipitation(self, bar_height, bar_width):
        if bar_height == 1:
            for p in self.precipitation_now_forecast:
                if p > 2.5:
                    print('^^', end='')
                elif p > 1:
                    print('~~', end='')
                elif p > 0.3:
                    print(',,', end='')
                else:
                    print('__', end='')
            print()
        else:
            for idx, i in enumerate(
                    self.equal_spaced(self.PRECIPITATION_MAX, -self.PRECIPITATION_MAX / bar_height, bar_height)):
                print('{0:.1f} |'.format(i), end='')
                for p in self.precipitation_now_forecast:
                    if p > i:
                        print('|' * bar_width, end='')
                    else:
                        print(' ' * bar_width, end='')
                print()
            _format = '{:^' + str(bar_width) + '}'

            x_axis = [_format.format(i) for i in self.PRECIPITATION_TIME_STAMPS_ROW]
            print('     ' + ''.join(x_axis))

    def _print_credit(self):
        print(self.credit_text)
        print(self.credit_url)

    @staticmethod
    def equal_spaced(lower, upper, length):
        for x in range(length):
            yield lower + x * (upper - lower) / length

    @staticmethod
    def place_to_dir_name(place):
        return place.replace('/', '_')

    def __repr__(self):
        return "Weather({})".format(self.location)