from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='jmstvcamp',
      version=version,
      description="Website for PythonCamp Cologne",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Christian Scholz',
      author_email='cs@comlounge.net',
      url='http://pythoncamp.de',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        "logbook",
        "werkzeug",
        "routes",
        "jinja2",
        "pymongo",
        "quantumcore.storages",
        "quantumcore.exceptions",
        "formencode",
        "pwtools"
      ],
      entry_points="""
        [paste.app_factory]
        frontend = jmstvcamp.main:frontend_factory
      """,
      )
