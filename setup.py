"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

from cptpy import __version__
from setuptools import setup, find_packages
with open("README.md", encoding="utf8") as f:
    long_description = f.read()

setup(
    name='cptpy',
    version=__version__,
    description='A Python package for processing Cone Penetration Test (CPT) data.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jpvantassel/cptpy',
    author='Joseph P. Vantassel',
    author_email='joseph.p.vantassel@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='',
    packages=find_packages(),
    python_requires = '>=3.6, <3.9',
    install_requires=['numpy'],
    extras_require={
        'dev': [],
    },
    package_data={
    },
    data_files=[
        ],
    entry_points={
    },
    project_urls={ 
        'Bug Reports': 'https://github.com/jpvantassel/cptpy/issues',
        'Source': 'https://github.com/jpvantassel/cptpy',
    },
)