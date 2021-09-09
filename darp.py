import inspect, os, subprocess, sys, traceback, types

__version__ = '1.3.1'

REQUIRED = object()

TYPE_MAP = {
  'list': list,
  'set': set,
  'int': int,
  'float': float,
  'str': str,
}

class prep:
  def __init__(self, f, **shortcuts):
    self.f = f
    self.sig = inspect.signature(self.f)
    self.actual_defaults = {}
    self.shortcuts = shortcuts
    for param in self.sig.parameters.values():
      self._find_alts_and_hints(param)
    self.r_shortcuts = dict([(v,k) for k,v in shortcuts.items()])

  def _find_alts_and_hints(self, param):
    default = param.default
    while isinstance(default, alt):
      self.shortcuts[default.c] = param.name
      self.actual_defaults[param.name] = default.default
      default = default.default
    
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
      return '[%s--%s <%s>]' % ('-%s|' % self.r_shortcuts[name] if name in self.r_shortcuts else '', name, kind or 'value')
    if kind:
      return '<%s:%s>' % (name, kind)
    else:
      return '<%s>' % name
    
  def run(self, cl_args=sys.argv):
    args = []
    kwargs = self.actual_defaults.copy()
    kwarg = None
    for arg in cl_args[1:]:
      if arg.startswith('-') and kwarg:
        kwargs[kwarg] = True
        kwarg = None
      if arg.startswith('--'):
        kwarg = arg.replace('-','_')[2:]
        if '=' in kwarg:
          kwargs[kwarg.split('=')[0]] = kwarg.split('=')[1]
          kwarg = None
      elif arg.startswith('-') and len(arg)>1:
        for char in arg[1:]:
          if char not in self.shortcuts:
            if self.f.__doc__:
              print(self.f.__doc__, file=sys.stderr)
            print('%s() unknown argument: -%s' % (self.f.__name__, char), file=sys.stderr)
            print(self._gen_doc(cl_args), file=sys.stderr)
            return
          kwarg = self.shortcuts[char]
          kwargs[self.shortcuts[char]] = True
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
        if param.annotation == list:
          kwargs[k] = v.split(',')
        elif isinstance(param.annotation, types.GenericAlias):
          t1 = str(param.annotation).split('[')[0]
          t2 = str(param.annotation).split('[')[1].strip(']')
          if t1 in TYPE_MAP: t1 = TYPE_MAP[t1]
          else: raise Exception('unknown GenericAlias type', t1)
          if t2 in TYPE_MAP: t2 = TYPE_MAP[t2]
          else: raise Exception('unknown GenericAlias subtype', t2)
          kwargs[k] = t1([t2(x) for x in v.split(',')])
        else:
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
      arg_desc_list = ["'%s--%s'" % ('-%s|' % self.r_shortcuts[s] if s in self.r_shortcuts else '', s) for s in missing_kwargs]
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
      return self.f(*args, **kwargs)
    except TypeError as e:
      if self.f.__doc__:
        print(self.f.__doc__, file=sys.stderr)
      print(e, file=sys.stderr)
      print(self._gen_doc(cl_args), file=sys.stderr)
      
  
  
    
class alt:
  def __init__(self, c:str, default=None):
    if len(c)!=1: raise Exception('alts must be a single character:', c)
    self.c = c
    self.default = default

  def __add__(self, o):
    return alt(o.c, default=self)

  def __radd__(self, o):
    return alt(self.c, default=o)

  def __repr__(self) -> str:
      return '<alt c=%s default=%s>' % (self.c, repr(self.default))
