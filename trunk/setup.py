#!/usr/bin/env python

from distutils.core import setup

setup(name='vertica.pyodbc',
      version='1.0',
      description='Django Vertica backends using pyodbc',
      author='Shy Halsband',
      url='http://code.google.com/p/django-vertica',
      packages=['vertica', 'vertica.pyodbc', 'vertica.extra'],
     )
