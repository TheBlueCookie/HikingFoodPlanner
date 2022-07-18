import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='PyHikingPlanner',
    version='0.0.1',
    author='Elias Ankerhold',
    author_email='elias.ankerhold@gmail.com',
    description='Testing installation of Package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/TheBlueCookie/HikingFoodPlanner.git',
    license='GPL-3.0-or-later',
    packages=setuptools.find_packages(),
    install_requires=['numpy>=1.21.1', 'pandas>=1.3.1', 'PyQt5>=5.15.7', 'pyqtgraph>=0.12.4'],
)