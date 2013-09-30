import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'requests',
]

setup(name='Coop-Gateway',
      version='0.0',
      description='An application to interface two Django-Coop instances',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP",
      ],
      author='Antoine Cezar',
      author_email='antoine.cezar@makina-corpus.com',
      url='https://github.com/makinacorpus/coop-gateway',
      keywords='django-coop',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='coop_gateway',
      install_requires=requires,
      )