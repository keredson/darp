import darp


# example run w/ no arguments...

# $ python3 example.py
# Example DArP (Derek's Argument Parser) app...
# serve() missing 1 required positional argument: 'name'
# usage: python3 example.py <name> [--port <int>]


def serve(name, port:int=darp.REQUIRED):
  '''Example DArP (Derek's Argument Parser) app...'''
  print('running', name, 'on', port)
  
if __name__=='__main__':
  darp.prep(serve, p='port').run()
