from distutils.core import setup

setup(
    name='glider_binary_data_reader',
    version='1.0',
    author='Michael Lindemuth',
    author_email='mlindemu@usf.edu',
    packages=['glider_binary_data_reader'],
    scripts=[
        'glider_binary_data_reader/methods.py',
        'glider_binary_data_reader/glider_bd_reader.py'
    ]
)
