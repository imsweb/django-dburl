# CHANGELOG

## 1.0.0

- Forked from https://github.com/jacobian/dj-database-url
  (see https://github.com/jacobian/dj-database-url/blob/master/CHANGELOG.md for previous changes)
- Added ability to register custom URL schemes/backends
- Added ability to pass arbitrary keys to `DATABASES` setting, such as `CONN_MAX_AGE`
- Added ability for backends to parse/handle custom querystring arguments
- Updated to test with Django 2.x/3.x and Python 3.6 to 3.10
- Use black/isort/flake8
