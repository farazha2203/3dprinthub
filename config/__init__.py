"""Django project configuration package."""

import pymysql

# MySQLdb compatibility for Django on shared hosting.
pymysql.install_as_MySQLdb()
