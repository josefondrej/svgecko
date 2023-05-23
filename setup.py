from setuptools import setup, find_packages

setup(
    name='svg-transform',
    version='0.1.0',
    author='Josef Ondrej',
    author_email='josef.ondrej@outlook.com',
    description='Lightweight library for arbitrary geometric SVG transformations',
    long_description='Lightweight library for arbitrary geometric SVG transformations',
    long_description_content_type='text/markdown',
    packages=find_packages(),
    package_data={'svg_transform': ['resources/*.svg']},
    install_requires=[
        'lxml',
        'pillow',
        'cairosvg',
        'pytest',
        'numpy'
    ]
)
