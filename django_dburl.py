import os
import urllib.parse as urlparse

__version__ = "1.0.0"
__version_info__ = tuple(map(int, __version__.split(".")))


ENGINE_SCHEMES = {}


class Engine:
    def __init__(self, backend, postprocess=lambda config: None):
        self.backend = backend
        self.postprocess = postprocess


def register(backend, schemes=None):
    engine = Engine(backend)
    schemes = schemes or [backend.rsplit(".")[-1]]
    schemes = [schemes] if isinstance(schemes, str) else schemes
    for scheme in schemes:
        urlparse.uses_netloc.append(scheme)
        ENGINE_SCHEMES[scheme] = engine

    def inner(func):
        engine.postprocess = func
        return func

    return inner


register("django.contrib.gis.db.backends.spatialite")
register("django.contrib.gis.db.backends.mysql", "mysqlgis")
register("django.contrib.gis.db.backends.oracle", "oraclegis")
register("django.db.backends.sqlite3", "sqlite")


@register("django.db.backends.oracle")
def stringify_port(config):
    config["PORT"] = str(config["PORT"])


@register("django.db.backends.mysql")
def apply_ssl_ca(config):
    options = config["OPTIONS"]
    ca = options.pop("ssl-ca", None)
    if ca:
        options["ssl"] = {"ca": ca}


@register("django.db.backends.postgresql", ("postgres", "postgresql", "pgsql"))
@register("django.contrib.gis.db.backends.postgis")
def apply_current_schema(config):
    options = config["OPTIONS"]
    schema = options.pop("currentSchema", None)
    if schema:
        options["options"] = f"-c search_path={schema}"


def config(env="DATABASE_URL", default=None, **settings):
    """
    Gets a database URL from environmental variable named as 'env' value and parses it.
    """
    s = os.environ.get(env, default)
    return parse(s, **settings) if s else {}


def parse(url, **settings):
    """Parses a database URL and returns configured DATABASE dictionary."""

    if url == "sqlite://:memory:":
        # this is a special case, because if we pass this URL into
        # urlparse, urlparse will choke trying to interpret "memory"
        # as a port number
        return {"ENGINE": ENGINE_SCHEMES["sqlite"].backend, "NAME": ":memory:"}
        # note: no other settings are required for sqlite

    url = urlparse.urlparse(url)
    engine = ENGINE_SCHEMES[url.scheme]

    path = url.path[1:]
    # If we are using sqlite and we have no path, then assume we
    # want an in-memory database (this is the behaviour of sqlalchemy)
    if url.scheme == "sqlite" and path == "":
        path = ":memory:"

    query = urlparse.parse_qs(url.query)
    options = {k: v[-1] for k, v in query.items()}

    config = {
        "ENGINE": engine.backend,
        "NAME": urlparse.unquote(path or ""),
        "USER": urlparse.unquote(url.username or ""),
        "PASSWORD": urlparse.unquote(url.password or ""),
        "HOST": urlparse.unquote(url.hostname or ""),
        "PORT": url.port or "",
        "OPTIONS": options,
    }
    engine.postprocess(config)

    # Update the final config with any settings passed in explicitly.
    config["OPTIONS"].update(settings.pop("OPTIONS", {}))
    config.update(**settings)

    if not config["OPTIONS"]:
        config.pop("OPTIONS")
    return config
