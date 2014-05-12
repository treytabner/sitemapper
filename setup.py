#!/usr/bin/env python2

"""Website crawler and sitemap generator"""

from setuptools import setup


setup(name='sitemapper',
      version='0.1',
      description=__doc__,
      long_description=open('README.md').read(),
      author='Trey Tabner',
      author_email='trey@tabner.com',
      url='http://treytabner.com',
      packages=['sitemapper', ],
      install_requires=open('requirements.txt').read().splitlines(),
      entry_points={
          'console_scripts': [
              'sitemapper = sitemapper.main:main',
          ]
      })
