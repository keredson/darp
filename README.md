Derek's Argument Parser
=======================

[![Build Status](https://travis-ci.org/keredson/darp.svg?branch=master)](https://travis-ci.org/keredson/darp)

This is a Pythonic argument parser.  It automatically converts your sys.argv to `*args, **kwargs` and passes them to whatever function you wish.  It also automatically generates usage messages and handles python type checking / conversions.

For example, if you have the following program:
```python
import darp

def serve(name, port:int=8888):
  '''Example DArP (Derek's Argument Parser) app...'''
  print('running', name, 'on', port)
  
if __name__=='__main__':
  darp.prep(serve).run()
```
And run it with arguments, you'll get the following output:

```
$ python3 example.py
Example DArP (Derek's Argument Parser) app...
serve() missing 1 required positional argument: 'name'
usage: python3 example.py <name> [--port <int>]
```

Required Parameters
-------------------

`*arg` parameters are always required.  Keyword parameters (like `--port`) can be marked as required like this:
```python
def serve(name, port:int=darp.REQUIRED):
  print('running', name, 'on', port)
  
if __name__=='__main__':
  darp.prep(serve, p='port').run()
```
If run without the required argument this error is printed:

```
$ python3 example_required.py 
serve() missing 1 required argument: '-p|--port'
usage: python3 example_required.py <name> --port <int>
```


Shortcut Parameters
-------------------
Keyword parameters are prefixed with `--` (like `--port`).  A shortcut parameter is when you want your script to respond to `-p 7777` as if the user typed `--port 7777`.  You specify this relationship via arguments to `darp.prep` like:

```python
if __name__=='__main__':
  darp.prep(serve, p='port').run()
```

Example:
```
$ python3 example.py server -p 7777
running server on 7777
```

Existence Parameters
--------------------
Keyword parameters without values are considered `True` if present.  For example:

```python
def doit(dry_run=False):
  if dry_run:
    print('doing a dry run...')
  else:
    print('doing it for real!')
  
if __name__=='__main__':
  darp.prep(doit).run()
```

Example run:
```
$ python3 example_existence.py --dry-run
doing a dry run...
```

Notice that `--dry-run` is mapped to the `dry_run` kwarg.

Existence params can be combined if using shortcuts.  See:

```python
def doit(apple=False, banana=False):
  print('apple', apple)
  print('banana', banana)
  
if __name__=='__main__':
  darp.prep(doit, a='apple', b='banana').run()
```

Example run:

```
$ python3 example_squashed_existence.py -ab
apple True
banana True
```

How to Install
--------------

```bash
$ pip3 install darp
```
