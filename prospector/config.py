from aumbry import Attr, YamlConfig


class DatabaseConfig(YamlConfig):
    """
    Map the database connection to our application
    from the YAML config file
    """
    __mapping__ = {
        'connection': Attr('connection', str),
    }

    connection = ''


class AppConfig(YamlConfig):
    """
    Add mapping for our application config
    """
    __mapping__ = {
        'db': Attr('db', DatabaseConfig),
        'gunicorn': Attr('gunicorn', dict)
    }

    def __init__(self):
        self.db = DatabaseConfig()
        self.gunicorn = {}
