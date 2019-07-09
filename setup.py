from setuptools import setup


setup(
    name='jesterdb',
    version='1.0.0',
    packages=['jester'],
    url='https://github.com/Zwork101/jester',
    license='MIT',
    author='Nathan Zilora',
    author_email='zwork101@gmail.com',
    description='Turning SQLite into a server is a good idea?',
    install_requires=['gevent', 'msgpack'],
    long_description="See github for documentation and explanation"
)
