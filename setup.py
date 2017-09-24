from distutils.core import setup

setup(
    name='term_weather',
    version='0.1',
    packages=['term_weather'],
    url='',
    license='',
    requires=["xmltodict", "click"],
    author='Anders Broen',
    author_email='',
    description='Python command line tool for accessing Yr weather data',
    entry_points={
        'console_scripts': ['term_weather=term_weather.command_line:cli'],
    }
)
