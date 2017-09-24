import click
from term_weather.config import install_default_config, \
    list_places, get_default_config, add_location, set_default_location, get_config
from term_weather.weather import Weather


@click.group()
def cli():
    """Command line tool to show the Now forecast from Yr"""
    pass


@cli.command()
def list():
    """List the installed locations"""
    list_places()


@cli.command()
@click.option('--name', default=None, help='Show weather now for [name]')
@click.option('--location', default=None, help='Show weather now for Yr location string ie (Telemark/Sauherad/Gvarv)')
def now(name, location):
    """The weather now"""
    if location:
        Weather(location).now()
    else:
        if name:
            config = get_config(name)
        else:
            config = get_default_config()

        Weather(location = config['location'], language=config["language"]).now()


@cli.command()
@click.argument('name')
@click.argument('location')
@click.option('--language', default='en', help='en, nb or nn')
@click.option('--language', default='en', help='en, nb or nn')
def init(name, location, language):
    """Initialize with name and location string"""
    install_default_config(name, location, language=language)


@cli.command()
@click.argument('name')
@click.argument('location')
@click.option('--default', default="False", help='Set this entry as default')
def add(name, location, default):
    """Add a new location"""
    add_location(name, location, default)


@cli.command()
@click.argument('name')
def default(name):
    """Set a location as default"""
    set_default_location(name)


if __name__ == '__main__':
    cli()
