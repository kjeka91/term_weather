# term_weather

Command line tool based on Click for forecast to terminal from Yr which currently only works in Norway.

# Installation

Clone and use pip. This will install the command line tool term_weather as well as the python package term_weather.

```sh
$ git clone https://github.com/kjeka91/term_weather.git
$ cd term_weather
$ pip install --user .
```

# Usage


Locate an area you want to get forecast from at yr.no, for oslo it is https://www.yr.no/sted/Norge/Oslo/Oslo/Oslo/
Here the location string is everything after "https://www.yr.no/sted/" again for Oslo: Norge/Oslo/Oslo/Oslo/

Initialize the program by setting a chosen name and the yr location
```sh
$ term_weather init Oslo Norge/Oslo/Oslo/Oslo/
```

This will create a configuration file named config under ~/.config/term_weather.
Later you can get a nice representation of the 90 minutes precipitation forecast.

```sh
$ term_weather now
Oslo, Norway: 01:00-06:00 | 13.0° | 0.0-0.3mm | 2.1m/s Light breeze | 1028.7hPa
5.0 |
3.8 |
2.6 |
1.4 |
0.2 |
       0         '        30         '        60         '        90
Weather forecast from Yr, delivered by the Norwegian Meteorological Institute and the NRK
http://www.yr.no/place/Norway/Oslo/Oslo/Oslo/
```

This command will download the forecast.xml and varsel_nu.xml file from yr.no at the specified location. The files are saved to a temporary folder in /tmp/term_weather. On the next run of the program the previously downloaded xml files are loaded, and the "nextupdate" field is checked to see if the forecast is outdated and should be updated.


# Credit
Weather forecast from Yr, delivered by the Norwegian Meteorological Institute and NRK