# django-dburl

[![CI](https://github.com/imsweb/django-dburl/actions/workflows/test.yml/badge.svg)](https://github.com/imsweb/django-dburl/actions/workflows/test.yml)

**NOTE**: This library is a fork of [dj-database-url](https://github.com/jacobian/dj-database-url),
updated to allow for registering custom backends, passing `DATABASES` keys as
configuration, and tested on more modern versions of Python and Django.

This simple Django utility allows you to utilize the
[12factor](http://www.12factor.net/backing-services) inspired `DATABASE_URL` environment
variable to configure your Django application.

The `django_dburl.config` method returns a Django database connection dictionary,
populated with all the data specified in your URL. You can also pass in any keyword
argument that Django's
[`DATABASES`](https://docs.djangoproject.com/en/3.2/ref/settings/#std:setting-OPTIONS)
setting accepts, such as [`CONN_MAX_AGE`](https://docs.djangoproject.com/en/3.2/ref/settings/#conn-max-age)
or [`OPTIONS`](https://docs.djangoproject.com/en/3.2/ref/settings/#std:setting-OPTIONS).
Any querystring parameters (such as `?timeout=20`) will automatically be parsed and
added to `OPTIONS` (`OPTIONS["timeout"] = 20` in this case).

If you'd rather not use an environment variable, you can pass a URL in directly
instead to `django_dburl.parse`.

## Supported Databases

All built-in Django database backends are supported. See below for more details.

## Installation

```
pip install django-dburl
```

## Usage

Configure your database in `settings.py` from `DATABASE_URL`:

```python
import django_dburl
DATABASES["default"] = django_dburl.config(CONN_MAX_AGE=600)
```

Provide a default:

```python
DATABASES['default'] = django_dburl.config(default='postgres://...')
```

Parse an arbitrary Database URL:

```python
DATABASES['default'] = django_dburl.parse('postgres://...', CONN_MAX_AGE=600)
```

The `CONN_MAX_AGE` option is the lifetime of a database connection in seconds
and is available in Django 1.6+. If you do not set a value, it will default to `0`
which is Django's historical behavior of using a new database connection on each
request. Use `None` for unlimited persistent connections.

## URL schemes

| Database     | Django Backend                              | URL                                        |
| ------------ | ------------------------------------------- | ------------------------------------------ |
| PostgreSQL   | `django.db.backends.postgresql`             | `postgres://USER:PASSWORD@HOST:PORT/NAME`  |
| PostGIS      | `django.contrib.gis.db.backends.postgis`    | `postgis://USER:PASSWORD@HOST:PORT/NAME`   |
| MySQL        | `django.db.backends.mysql`                  | `mysql://USER:PASSWORD@HOST:PORT/NAME`     |
| MySQL (GIS)  | `django.contrib.gis.db.backends.mysql`      | `mysqlgis://USER:PASSWORD@HOST:PORT/NAME`  |
| SQLite       | `django.db.backends.sqlite3`                | `sqlite:///PATH`                           |
| SpatiaLite   | `django.contrib.gis.db.backends.spatialite` | `spatialite:///PATH`                       |
| Oracle       | `django.db.backends.oracle`                 | `oracle://USER:PASSWORD@HOST:PORT/NAME`    |
| Oracle (GIS) | `django.contrib.gis.db.backends.oracle`     | `oraclegis://USER:PASSWORD@HOST:PORT/NAME` |

## Registering custom schemes

```python
import django_dburl

# These were supported out of the box in dj-database-url.
django_dburl.register("mysql.connector.django", "mysql-connector")
django_dburl.register("sql_server.pyodbc", "mssql", string_ports=True)
django_dburl.register(
    "django_redshift_backend",
    "redshift",
    options={
        "currentSchema": lambda values: {
            "options": "-c search_path={}".format(values[-1])
        },
    },
)
```
