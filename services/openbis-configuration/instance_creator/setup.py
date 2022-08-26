from setuptools import find_packages, setup  # or find_namespace_packages
setup(name='instance-creator',
      version='1.0',
      py_modules=find_packages(where='.'),
      scripts=['instance_creator/make_instance.py'],
      requires=['pybis', 'pydantic']
      )