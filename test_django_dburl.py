import pathlib
from unittest.mock import patch

import pytest
import yaml

import django_dburl

# These were supported out of the box in dj-database-url.
django_dburl.register("mysql.connector.django", "mysql-connector")
django_dburl.register("django_cockroachdb", "cockroach")
django_dburl.register("sql_server.pyodbc", "mssql")(django_dburl.stringify_port)
django_dburl.register("mssql", "mssqlms")(django_dburl.stringify_port)
django_dburl.register("django_redshift_backend", "redshift")(
    django_dburl.apply_current_schema
)


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


URL = "postgres://user:password@localhost/db-name"

cases_file = pathlib.Path(__file__).parent.joinpath("test_cases.yml")
cases = yaml.safe_load(cases_file.open())


@pytest.mark.parametrize("url,expected", cases)
def test_successful_parsing(url, expected):
    assert django_dburl.parse(url) == expected


def test_credentials_unquoted__raise_value_error():
    expected_message = (
        "This string is not a valid url, possibly because some of its parts "
        r"is not properly urllib.parse.quote\(\)'ed."
    )
    with pytest.raises(ValueError, match=expected_message):
        django_dburl.parse("postgres://user:passw#ord!@localhost/foobar")


def test_credentials_quoted__ok():
    config = django_dburl.parse("postgres://user%40domain:p%23ssword!@localhost/foobar")
    assert config["USER"] == "user@domain"
    assert config["PASSWORD"] == "p#ssword!"


def test_unknown_scheme__raise_value_error():
    expected_message = "Scheme 'unknown-scheme://' is unknown. Did you forget to register custom backend?"
    with pytest.raises(ValueError, match=expected_message):
        django_dburl.parse("unknown-scheme://user:password@localhost/foobar")


def test_provide_test_settings__add_them_to_final_config():
    settings = {
        "TEST": {
            "NAME": "mytestdatabase",
        },
    }
    config = django_dburl.parse(URL, **settings)
    assert config["TEST"] == {"NAME": "mytestdatabase"}


def test_provide_options__add_them_to_final_config():
    options = {"options": "-c search_path=other_schema"}
    config = django_dburl.parse(URL, OPTIONS=options)
    assert config["OPTIONS"] == options


def test_provide_clashing_options__use_options_from_kwargs():
    options = {"reconnect": "false"}
    config = django_dburl.parse(f"{URL}?reconnect=true", OPTIONS=options)
    assert config["OPTIONS"]["reconnect"] == "false"


def test_provide_custom_engine__use_it_in_final_config():
    engine = "django_mysqlpool.backends.mysqlpool"
    config = django_dburl.parse(URL, ENGINE=engine)
    assert config["ENGINE"] == engine


def test_provide_conn_max_age__use_it_in_final_config():
    config = django_dburl.parse(URL, CONN_MAX_AGE=600)
    assert config["CONN_MAX_AGE"] == 600


@patch.dict("os.environ", DATABASE_URL=URL)
@patch.object(django_dburl, "parse", return_value="RV")
def test_call_config__pass_env_var_value_to_parse(mock_method):
    assert django_dburl.config() == "RV"
    mock_method.assert_called_once_with(URL)


@patch.object(django_dburl, "parse", return_value="RV")
def test_call_config_no_var_set__return_empty(mock_method):
    assert django_dburl.config() == {}
    mock_method.assert_not_called()


@patch.object(django_dburl, "parse", return_value="RV")
def test_call_config_no_var_set_provide_default__pass_default_to_parse(mock_method):
    fallback_url = "sqlite://"
    assert django_dburl.config(default=fallback_url) == "RV"
    mock_method.assert_called_once_with(fallback_url)


@patch.dict("os.environ", CUSTOM_DATABASE_URL=URL)
@patch.object(django_dburl, "parse", return_value="RV")
def test_call_config_custom_env_var__pass_var_value_to_parse(mock_method):
    assert django_dburl.config("CUSTOM_DATABASE_URL") == "RV"
    mock_method.assert_called_once_with(URL)


@patch.dict("os.environ", CUSTOM_DATABASE_URL=URL)
@patch.object(django_dburl, "parse", return_value="RV")
def test_provide_settings_to_config__pass_them_to_parse(mock_method):
    settings = {
        "CONN_MAX_AGE": 600,
        "ENGINE": "django_mysqlpool.backends.mysqlpool",
        "OPTIONS": {"options": "-c search_path=other_schema"},
    }

    rv = django_dburl.config("CUSTOM_DATABASE_URL", **settings)

    assert rv == "RV"
    mock_method.assert_called_once_with(URL, **settings)
