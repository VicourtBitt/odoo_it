# This script creates a basic directory structure for a new module in Odoo.
#!/bin/bash

mkdir data
mkdir demo
mkdir i18n
mkdir models
touch models/__init__.py
mkdir controllers
touch controllers/__init__.py
mkdir readme
mkdir report
mkdir security
mkdir static/description -p
mkdir tests
mkdir views
touch __init__.py
touch __manifest__.py