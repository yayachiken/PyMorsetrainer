from setuptools import setup, find_packages
setup(
    name="pymorsetrainer",
    version="0.0.1.dev1",
    packages=find_packages(),
    entry_points={
        'gui_scripts': ['pymorsetrainer = pymorsetrainer.__main__:main']
    },

    install_requires=['PyQt5>=5.0', 'numpy>=1.10', 'pyaudio>=0.2.0'],

    package_data={
    },

    author="David Kolossa",
    author_email="pymorsetrainer@yayachiken.net",
    description="A simple morse training application inspired by lcwo.net",
    license="GPLv3+",
    keywords="morse code cw trainer koch farnsworth method",
    url="https://github.com/yayachiken/PyMorsetrainer",

    classifiers=[
        'Development Status :: 2 - Pre Alpha',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Communications :: Ham Radio',
    ],
)

