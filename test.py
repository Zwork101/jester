from random import randint

from jester.client import JesterClient


with JesterClient() as cli:
    cli.execute("CREATE TABLE test (val real)")

for _ in range(1000):
    with JesterClient() as cli:
        cli.execute("INSERT INTO test VALUES (?)", randint(-100, 100))

with JesterClient() as cli:
    cli.execute("SELECT * FROM test")
    print(cli.fetch_all())
