from setuptools import setup, find_packages

__version_info__ = 2, 0, 1
__version__ = '.'.join(map(str, __version_info__))

setup(
    name="pycontractions",
    version=__version__,
    description="Intelligently expand and create contractions in text leveraging grammar checking and Word Mover's Distance.",
    author="Ian Beaver, Verint - Next IT",
    author_email="ian.beaver@verint.com",
    url="https://github.com/ian-beaver/pycontractions",
    license="BSD",
    packages=find_packages(),
    long_description=open("README.rst").read(),
    install_requires=["gensim>=2.0", "language-tool-python>=2.5.3", "pyemd>=0.4.4"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering',
        'Topic :: Utilities',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Software Development :: Libraries',
    ],
)
