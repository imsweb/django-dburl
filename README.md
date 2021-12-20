# django-dburl

[![CI](https://github.com/imsweb/django-dburl/actions/workflows/test.yml/badge.svg)](https://github.com/imsweb/django-dburl/actions/workflows/test.yml)

**NOTE**: This library is a fork of [dj-database-url](https://github.com/jacobian/dj-database-url),
updated to allow for registering custom backends, passing `DATABASES` keys as
configuration, and tested on more modern versions of Python and Django.

This simple Django utility allows you to utilize the
[12factor](http://www.12factor.net/backing-services) inspired `DATABASE_URL` environment
variable to configure your Django application.

## Installation

```sh
pip install django-dburl
```

## Usage

The `django_dburl.config()` method returns a Django database connection dictionary,
populated with all the data specified in your `DATABASE_URL` environment variable:

```python
import django_dburl

DATABASES = {
    "default": django_dburl.config(),
    # arbitrary environment variable can be used
    "replica": django_dburl.config("REPLICA_URL"),
}
```
Given the following environment variables are defined:

```sh
export DATABASE_URL="postgres://user:password@ec2-107-21-253-135.compute-1.amazonaws.com:5431/db-name"
# All the characters which are reserved in URL as per RFC 3986 should be urllib.parse.quote()'ed.
export REPLICA_URL="postgres://%23user:%23password@replica-host.com/db-name?timeout=20"
```

The aforementioned code will result in:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "USER": "user",
        "PASSWORD": "password",
        "HOST": "ec2-107-21-253-135.compute-1.amazonaws.com",
        "PORT": 5431,
        "NAME": "db-name",
    },
    "replica": {
        "ENGINE": "django.db.backends.postgresql",
        "USER": "#user",
        "PASSWORD": "#password",
        "HOST": "replica-host.com",
        "PORT": "",
        "NAME": "db-name",
        # Any querystring parameters are automatically parsed and added to `OPTIONS`.
        "OPTIONS": {
            "timeout": "20",
        },
    },
}
```

A default value can be provided which will be used when the environment variable is not set:

```python
DATABASES["default"] = django_dburl.config(default="sqlite://")
```

If you'd rather not use an environment variable, you can pass a URL directly into `django_dburl.parse()`:

```python
DATABASES["default"] = django_dburl.parse("postgres://...")
```

You can also pass in any keyword argument that Django's
[`DATABASES`](https://docs.djangoproject.com/en/stable/ref/settings/#databases) setting accepts,
such as [`CONN_MAX_AGE`](https://docs.djangoproject.com/en/stable/ref/settings/#conn-max-age)
or [`OPTIONS`](https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-OPTIONS):

```python
django_dburl.config(CONN_MAX_AGE=600, TEST={"NAME": "mytestdatabase"})
# results in:
{
    "ENGINE": "django.db.backends.postgresql",
    # ...
    "NAME": "db-name",
    "CONN_MAX_AGE": 600,
    "TEST": {
        "NAME": "mytestdatabase",
    },
}

# such usage is also possible:
django_dburl.parse("postgres://...", **{
    "CONN_MAX_AGE": 600,
    "TEST": {
        "NAME": "mytestdatabase",
    },
    "OPTIONS": {
        "isolation_level": psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE,
    },
})
```

`OPTIONS` will be properly merged with the parameters coming from querystring
(keyword argument has higher priority than querystring).


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

## Supported Databases

All built-in Django database backends are supported. If you want to use some non-default backends,
you need to register them first:

```python
import django_dburl
# registration should be performed only once
django_dburl.register("mysql.connector.django", "mysql-connector")

assert django_dburl.parse("mysql-connector://user:password@host:port/db-name") == {
    "ENGINE": "mysql.connector.django",
    # ...other connection params
}
```

Some backends need further config adjustments (e.g. oracle and mssql expect `PORT` to be a string).
For such cases you can provide a post-processing function to `register()`
(note that `register()` is used as a **decorator(!)** in this case):

```python
import django_dburl

@django_dburl.register("sql_server.pyodbc", "mssql")
def stringify_port(config):
    config["PORT"] = str(config["PORT"])

@django_dburl.register("django_redshift_backend", "redshift")
def apply_current_schema(config):
    options = config["OPTIONS"]
    schema = options.pop("currentSchema", None)
    if schema:
        options["options"] = f"-c search_path={schema}"

@django_dburl.register("django_snowflake", "snowflake")
def adjust_snowflake_config(config):
    config.pop("PORT", None)
    config["ACCOUNT"] = config.pop("HOST")
    name, _, schema = config["NAME"].partition("/")
    if schema:
        config["SCHEMA"] = schema
        config["NAME"] = name
    options = config.get("OPTIONS", {})
    warehouse = options.pop("warehouse", None)
    if warehouse:
        config["WAREHOUSE"] = warehouse
    role = options.pop("role", None)
    if role:
        config["ROLE"] = role
```
