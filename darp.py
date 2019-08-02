import inspect, os, subprocess, sys, traceback

__version__ = '1.1'

REQUIRED = object()

class prep:
  def __init__(self, f, **shortcuts):
    self.f = f
    self.sig = inspect.signature(self.f)
    self.shortcuts = shortcuts
    
  def _gen_doc(self, args):
    interpretor = sys.executable
    basename = os.path.basename(interpretor)
    full_path = subprocess.check_output(['which',basename]).decode().strip()
    if full_path==interpretor:
      interpretor = basename
    return ' '.join(['usage:', interpretor] + args[:1] + [self._desc_param(param) for param in self.sig.parameters.values()])
    
  def _desc_param(self, param):
    name = param.name
    kind = param.annotation.__name__ if param.annotation!=param.empty else ''
    if param.default==REQUIRED:
      return '--%s <%s>' % (name, kind or 'value')
    if param.default!=param.empty:
      return '[--%s <%s>]' % (name, kind or 'value')
    if kind:
      return '<%s:%s>' % (name, kind)
    else:
      return '<%s>' % name
    
  def run(self, cl_args=sys.argv):
    args = []
    kwargs = {}
    kwarg = None
    for arg in cl_args[1:]:
      if arg.startswith('-') and kwarg:
        kwargs[kwarg] = True
        kwarg = None
      if arg.startswith('--'):
        arg = arg.replace('-','_')
        kwarg = arg[2:]
      elif arg.startswith('-') and len(arg)>1:
        for char in arg[1:-1]:
          kwargs[self.shortcuts[char]] = True
        kwarg = self.shortcuts[arg[-1]]
      else:
        if kwarg:
          kwargs[kwarg] = arg
          kwarg = None
        else:
          args.append(arg)
          
    # convert types if annotations are known
    for i, param in enumerate(self.sig.parameters.values()):
      if param.annotation!=param.empty and i<len(args):
        args[i] = param.annotation(args[i])
    for k,v in list(kwargs.items()):
      param = self.sig.parameters.get(k)
      if param and param.annotation!=param.empty:
        kwargs[k] = param.annotation(v)
    
    if kwarg:
      kwargs[kwarg] = True

    # handle --help        
    if not args and kwargs=={'help':True}:
      if self.f.__doc__:
        print(self.f.__doc__, file=sys.stderr)
      print(self._gen_doc(cl_args), file=sys.stderr)
      return
        
    # check for required kwargs
    missing_kwargs = []
    for param in self.sig.parameters.values():
      if param.default==REQUIRED and param.name not in kwargs:
        missing_kwargs.append(param.name)
    if missing_kwargs:
      r_shortcuts = dict([(v,k) for k,v in self.shortcuts.items()])
      arg_desc_list = ["'%s--%s'" % ('-%s|' % r_shortcuts[s] if s in r_shortcuts else '', s) for s in missing_kwargs]
      if len(arg_desc_list) > 2:
        arg_desc_list[-1] = 'and %s' % arg_desc_list[-1]
        arg_desc = ', '.join(arg_desc_list)
      else:
        arg_desc = ' and '.join(arg_desc_list)
      if self.f.__doc__:
        print(self.f.__doc__, file=sys.stderr)
      print('%s() missing %i required argument%s: %s' % (self.f.__name__, len(missing_kwargs), 's' if len(missing_kwargs)>1 else '', arg_desc), file=sys.stderr)
      print(self._gen_doc(cl_args), file=sys.stderr)
      return

    #print('calling', self.f, args, kwargs)
    try:
      self.f(*args, **kwargs)
    except TypeError as e:
      if self.f.__doc__:
        print(self.f.__doc__, file=sys.stderr)
      print(e, file=sys.stderr)
      print(self._gen_doc(cl_args), file=sys.stderr)
      
  
  
    
