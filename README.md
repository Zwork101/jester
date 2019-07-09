# jester

Turning SQLite into a server is a good idea?

Maybe, maybe not. I'm not quite sure yet. I've tested and stress tested the jester server, both times is functioned without any issues. If theres a problem, *please* create an issue so that hopefully we can resolve the issue.

## Why did I make jester?

I realize that there are many articles saying exactly not to do this, but I wanted to see if this issues were truely prevelent. In addion, there are simply no good databases for small applications. If I want to create a simple login page, that only my website is going to use, along side a few other programs, I'd had to setup a huge databases like postgresSQL, MySQL, MondoDB, etc. If you like setting up databases, you do you, but I like to actual program. 

### Why not just sqlite3 by itself?

Because sqlite3 is slow, and blocking. If it was slow and non-blocking, who cares, but it isn't. jester is just as slow as sqlite3, but because all sql commands are run in a seperate process, it's non-blocking. Your program won't halt when you add an entry to a table, offering speed like other external databases. 

## How to use jester

Simply type the following command to start it, see `--help` to see extra commands.

```bash
$ python -m jester.server
```

Jester does not encrypt communications, nor does it offer any form of authentication. For that reason you should ONLY run the database locally, do not expose it and try to connect non-locally.

### How to use it client-side

Assuming you didn't change the port or IP on the server, the jester client will have the default values already in place, so all you have to do is: 

```python
from jester import JesterClient

with JesterClient() as cli:
  ...
```

### JesterClient API (Because it's short)

**connect()** | `Connect to the server. Already called when using with syntax`

**close()** | `Disconnect from the server. Already called when using with syntax`

**execute(statement: str, *args)** | `Execute an SQL command on the database`

**execute_many(statement: str, values: List[List[str]])** | `Execute the same statement over a multitude of values`

**execute_script(script: str)** | `Execute SQL script on the database`

**fetch_one()** | `Return a single value that was selected from the database`

**fetch_all()** | `Return all values selected from the database`

**fetch_many(size: int)** | `Return size amount of values from the database`

## Last Remarks

If you're still confused on how the client works, see the `test.py` file where I stress tested it. Don't use this program will use app and websites. This only shines for things like personal projects, or where people won't be interacting with the database that often. Then again if you do decide to use it large scale, please tell me how it goes! Enjoy!
