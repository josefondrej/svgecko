from setuptools import setup, find_packages

setup(
    name='svgecko',
    version='0.3.2',
    author='Josef Ondrej',
    author_email='josef.ondrej@outlook.com',
    description='Lightweight library for arbitrary geometric SVG transformations',
    long_description='Lightweight library for arbitrary geometric SVG transformations',
    long_description_content_type='text/markdown',
    packages=find_packages(),
    package_data={'svgecko': ['resources/*.svg']},
    install_requires=[
        'lxml',
        'pillow',
        'cairosvg',
        'pytest',
        'numpy'
    ]
)
