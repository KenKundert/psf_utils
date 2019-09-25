from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='psf_utils',
    version='0.0.2',
    description='Cadence PSF file utilities',
    long_description=readme,
    author="Ken Kundert",
    license='GPLv3+',
    zip_safe = True,
    packages='psf_utils'.split(),
    entry_points = {'console_scripts': [
        'psf_list=psf_utils.list:list_signals',
        'psf_plot=psf_utils.plot:plot_signals',
    ]},
    install_requires='docopt inform ply quantiphy shlib'.split(),
    python_requires='>=3.6',
)
