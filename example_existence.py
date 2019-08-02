import darp


# example run w/ no arguments...

# $ python3 example.py
# Example DArP (Derek's Argument Parser) app...
# serve() missing 1 required positional argument: 'name'
# usage: python3 example.py <name> [--port <int>]


def doit(dry_run=False):
  if dry_run:
    print('doing a dry run...')
  else:
    print('doing it for real!')
  
if __name__=='__main__':
  darp.prep(doit).run()
