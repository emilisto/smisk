# encoding: utf-8
'''Introspection
'''
import inspect
try:
  import reprlib
except ImportError:
  import repr as reprlib
from smisk.util.type import *
from smisk.util.cache import callable_cache_key
from smisk.util.frozen import frozendict

__all__ = ['introspect', 'repr2']

class introspect(object):    
  VARARGS = 4
  KWARGS = 8
  
  _repr = reprlib.Repr()
  _repr.maxlong = 100
  _repr.maxstring = 200
  _repr.maxother = 200
  
  _info_cache = {}
  
  @classmethod
  def callable_info(cls, f):
    '''Info about a callable.
    
    The results are cached for efficiency.
    
    :param f:
    :type  f: callable
    :rtype: frozendict
    '''
    if not callable(f):
      return None
    
    if isinstance(f, FunctionType):
      # in case of ensure_va_kwa
      try:
        f = f.wrapped_func
      except AttributeError:
        pass
    
    cache_key = callable_cache_key(f)
    
    try:
      return cls._info_cache[cache_key]
    except KeyError:
      pass
    
    is_method, args, varargs, varkw, defaults = cls.getargspec(f)
    
    _args = []
    args_len = len(args)
    defaults_len = 0
    
    if defaults is not None:
      defaults_len = len(defaults)
    
    for i,n in enumerate(args):
      default_index = i-(args_len-defaults_len)
      v = Undefined
      if default_index > -1:
        v = defaults[default_index]
      _args.append((n, v))
    
    info = frozendict({
      'name':f.func_name,
      'args':tuple(_args),
      'varargs':bool(varargs),
      'varkw':bool(varkw),
      'method':is_method
    })
    
    cls._info_cache[cache_key] = info
    return info
  
  @classmethod
  def getargspec(cls, f):
    '''Returns a tuple of 5 objects: bool is_method, list args, string varargs, 
    string varkw, list defaults
    
    :rtype: tuple
    '''
    if not isinstance(f, (MethodType, FunctionType)):
      f = f.__call__
    
    is_method = False
    args, varargs, varkw, defaults = inspect.getargspec(f)
    
    if isinstance(f, MethodType):
      # Remove self
      args = args[1:]
      is_method = True
    
    return is_method, args, varargs, varkw, defaults
  
  @classmethod
  def format_members(cls, o, colorize=False):
    s = []
    items = []
    longest_k = 0
    types = {}
    type_i = 0
    color = 0
    
    for k in dir(o):
      v = getattr(o,k)
      if len(k) > longest_k:
        longest_k = len(k)
      if colorize:
        t = str(type(v))
        if t not in types:
          types[t] = type_i
          type_i += 1
        color = 31 + (types[t] % 5)
      items.append((k,v,color))
    
    if colorize:
      pat = '\033[1;%%dm%%-%ds\033[m = \033[1;%%dm%%s\033[m' % longest_k
    else:
      pat = '%%-%ds = %%s' % longest_k
    
    for k,v,color in items:
      v = cls._repr.repr(v)
      if colorize:
        s.append(pat % (color, k, color, v))
      else:
        s.append(pat % (k, v))
    
    return '\n'.join(s)
  
  
  @classmethod
  def ensure_va_kwa(cls, f, parent=None):
    '''Ensures `f` accepts both ``*varargs`` and ``**kwargs``.
    
    If `f` does not support ``*args``, it will be wrapped with a
    function which cuts away extra arguments in ``*args``.
    
    If `f` does not support ``*args``, it will be wrapped with a
    function which discards the ``**kwargs``.
    
    :param f:
    :type  f:       callable
    :param parent:  The parent on which `f` is defined. If specified, we will perform
                    ``parent.<name of f> = wrapper`` in the case we needed to wrap `f`.
    :type  parent:  object
    :returns: A callable which is guaranteed to accept both ``*args`` and ``**kwargs``.
    :rtype: callable
    '''
    is_method, args, varargs, varkw, defaults = cls.getargspec(f)
    va_kwa_wrapper = None
    
    if varargs is None and varkw is None:
      if args:
        def va_kwa_wrapper(*va, **kw):
          kws = kw.copy()
          for k in kw:
            if k not in args:
              del kws[k]
          return f(*va[:len(args)], **kws)
      else:
        def va_kwa_wrapper(*va, **kw):
          return f()
    elif varargs is None:
      if args:
        def va_kwa_wrapper(*va, **kw):
          return f(*va[:len(args)], **kw)
      else:
        def va_kwa_wrapper(*va, **kw):
          return f(**kw)
    elif varkw is None:
      if args:
        def va_kwa_wrapper(*va, **kw):
          kws = kw.copy()
          for k in kw:
            if k not in args:
              del kws[k]
          return f(*va, **kw)
      else:
        def va_kwa_wrapper(*va, **kw):
          return f(*va)
    
    if va_kwa_wrapper:
      va_kwa_wrapper.info = frozendict(cls.callable_info(f).update({
        'varargs': True,
        'varkw': True
      }))
      cls._info_cache[callable_cache_key(f)] = va_kwa_wrapper.info
      va_kwa_wrapper.wrapped_func = f
      va_kwa_wrapper.im_func = f
      va_kwa_wrapper.__name__ = f.__name__
      try:
        va_kwa_wrapper.im_class = f.im_class
      except AttributeError:
        pass
      for k in dir(f):
        if k[0] != '_' or k in ('__name__'):
          setattr(va_kwa_wrapper, k, getattr(f, k))
      if parent is not None:
        setattr(parent, info['name'], va_kwa_wrapper)
      return va_kwa_wrapper
    return f
  


repr2 = introspect._repr.repr
'''Limited ``repr``, only printing up to 4-6 levels and 100 chars per entry.

:type: repr.Repr
'''
