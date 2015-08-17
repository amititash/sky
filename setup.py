from setuptools import setup

MAJOR_VERSION = '0'
MINOR_VERSION = '0'
MICRO_VERSION = '101'
VERSION = "{}.{}.{}".format(MAJOR_VERSION, MINOR_VERSION, MICRO_VERSION)

setup(name = 'sky',
      version = VERSION,
      description = 'AI powered scraping in Python 3',
      url = 'https://github.com/kootenpv/sky',
      author = 'Pascal van Kooten',
      author_email = 'kootenpv@gmail.com',
      license = 'MIT',
      packages = ['sky', 'sky.data'],
      install_requires = [ 
          'distribute', 'lxml', 'tldextract', 'requests', 'justext', 'langdetect', 
          'python-dateutil', 'sh', 'beautifulsoup4'
      ], 
      # optional: ZODB, zodbpickle, cloudant, elasticsearch, selenium, asciitree, nltk
      classifiers = [ 
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Customer Service',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: Microsoft',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Unix',
          'Operating System :: POSIX',
          'Programming Language :: Python', 
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Software Development', 
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: Debuggers', 
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Software Distribution', 
          'Topic :: System :: Systems Administration',
          'Topic :: Utilities'
    ], 
    package_data = {'data': ['*.json'], 'sky/data' : ['*.json']},
    package_dir = {'sky': 'sky', 'data' : 'data', 'sky/data' : 'sky/data'},
    zip_safe = False,
    platforms='any')
