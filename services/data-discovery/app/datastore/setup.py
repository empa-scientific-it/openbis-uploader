from setuptools import find_packages, setup  # or find_namespace_packages
setup(name='datastore',
      version='1.0',
      py_modules=find_packages(where='.'),
      )