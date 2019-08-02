import io, sys, unittest
import darp

class TestDarp(unittest.TestCase):

  def setUp(self):
    self.ran = False
    self.stderr = sys.stderr = io.StringIO()
    
  def get_stderr(self):
    return self.stderr.getvalue().strip().split('\n')

  def test_no_args(self):
    def f():
      self.ran = True
    darp.prep(f).run('cmd.py'.split())
    self.assertTrue(self.ran)
  
  def test_arg(self):
    def f(a):
      self.assertEquals(a,'a')
      self.ran = True
    darp.prep(f).run('cmd.py a'.split())
    self.assertTrue(self.ran)
    
  def test_arg_with_type(self):
    def f(a:int):
      self.assertEquals(a,1)
      self.ran = True
    darp.prep(f).run('cmd.py 1'.split())
    self.assertTrue(self.ran)
    
  def test_kwarg(self):
    def f(a=None):
      self.assertEquals(a,'b')
      self.ran = True
    darp.prep(f).run('cmd.py --a b'.split())
    self.assertTrue(self.ran)
    
  def test_kwarg_with_type(self):
    def f(a:int=None):
      self.assertEquals(a,1)
      self.ran = True
    darp.prep(f).run('cmd.py --a 1'.split())
    self.assertTrue(self.ran)
    
  def test_arg_and_kwarg(self):
    def f(a, b=None):
      self.assertEquals(a,'a')
      self.assertEquals(b,'b')
      self.ran = True
    darp.prep(f).run('cmd.py a --b b'.split())
    self.assertTrue(self.ran)
    
  def test_arg_and_kwarg2(self):
    def f(a, b=None):
      self.assertEquals(a,'a')
      self.assertEquals(b,'b')
      self.ran = True
    darp.prep(f).run('cmd.py --b b a'.split())
    self.assertTrue(self.ran)
    
  def test_shortcut(self):
    def f(apple=None):
      self.assertEquals(apple,'banana')
      self.ran = True
    darp.prep(f, a='apple').run('cmd.py -a banana'.split())
    self.assertTrue(self.ran)

  def test_missing_arg(self):
    def f(a):
      self.ran = True
    darp.prep(f).run('cmd.py'.split())
    self.assertEquals(self.get_stderr(),[
      "f() missing 1 required positional argument: 'a'",
      'usage: python3 cmd.py <a>'
    ])
    self.assertFalse(self.ran)
    
  def test_two_missing_args(self):
    def f(a,b):
      self.ran = True
    darp.prep(f).run('cmd.py'.split())
    self.assertEquals(self.get_stderr(),[
      "f() missing 2 required positional arguments: 'a' and 'b'",
      'usage: python3 cmd.py <a> <b>'
    ])
    self.assertFalse(self.ran)
    
  def test_three_missing_args(self):
    def f(a,b,c):
      self.ran = True
    darp.prep(f).run('cmd.py'.split())
    self.assertEquals(self.get_stderr(),[
      "f() missing 3 required positional arguments: 'a', 'b', and 'c'",
      'usage: python3 cmd.py <a> <b> <c>'
    ])
    self.assertFalse(self.ran)
    
  def test_missing_arg_with_type(self):
    def f(a:int):
      self.ran = True
    darp.prep(f).run('cmd.py'.split())
    self.assertEquals(self.get_stderr(),[
      "f() missing 1 required positional argument: 'a'",
      'usage: python3 cmd.py <a:int>'
    ])
    self.assertFalse(self.ran)

  def test_missing_kwarg(self):
    def f(a=darp.REQUIRED):
      self.ran = True
    darp.prep(f).run('cmd.py'.split())
    self.assertFalse(self.ran)
    self.assertEquals(self.get_stderr(),[
      "f() missing 1 required argument: '--a'",
      'usage: python3 cmd.py --a <value>'
    ])
    
  def test_two_missing_kwargs(self):
    def f(a=darp.REQUIRED, b=darp.REQUIRED):
      self.ran = True
    darp.prep(f).run('cmd.py'.split())
    self.assertFalse(self.ran)
    self.assertEquals(self.get_stderr(),[
      "f() missing 2 required arguments: '--a' and '--b'",
      'usage: python3 cmd.py --a <value> --b <value>'
    ])
    
  def test_three_missing_kwargs(self):
    def f(a=darp.REQUIRED, b=darp.REQUIRED, c=darp.REQUIRED):
      self.ran = True
    darp.prep(f).run('cmd.py'.split())
    self.assertFalse(self.ran)
    self.assertEquals(self.get_stderr(),[
      "f() missing 3 required arguments: '--a', '--b', and '--c'",
      'usage: python3 cmd.py --a <value> --b <value> --c <value>'
    ])
    
  def test_missing_kwarg_with_shortcut(self):
    def f(apple=darp.REQUIRED):
      self.ran = True
    darp.prep(f, a='apple').run('cmd.py'.split())
    self.assertFalse(self.ran)
    self.assertEquals(self.get_stderr(),[
      "f() missing 1 required argument: '-a|--apple'",
      'usage: python3 cmd.py --apple <value>'
    ])

  def test_docstring(self):
    def f(a):
      '''This is tool F!'''
      self.ran = True
    darp.prep(f).run('cmd.py'.split())
    self.assertEquals(self.get_stderr(),[
      "This is tool F!",
      "f() missing 1 required positional argument: 'a'",
      'usage: python3 cmd.py <a>'
    ])
    self.assertFalse(self.ran)
    
  def test_exists_arg(self):
    def f(a=False):
      self.assertEquals(a,True)
      self.ran = True
    darp.prep(f).run('cmd.py --a'.split())
    self.assertTrue(self.ran)
    
  def test_shortcut_exists_arg(self):
    def f(apple=False):
      self.assertEquals(apple,True)
      self.ran = True
    darp.prep(f, a='apple').run('cmd.py -a'.split())
    self.assertTrue(self.ran)
    
  def test_multiple_shortcut_exists_arg(self):
    def f(apple=False, banana=False):
      self.assertEquals(apple,True)
      self.assertEquals(banana,True)
      self.ran = True
    darp.prep(f, a='apple', b='banana').run('cmd.py -a -b'.split())
    self.assertTrue(self.ran)
    
  def test_squashed_shortcut_exists_arg(self):
    def f(apple=False, banana=False):
      self.assertEquals(apple,True)
      self.assertEquals(banana,True)
      self.ran = True
    darp.prep(f, a='apple', b='banana').run('cmd.py -ab'.split())
    self.assertTrue(self.ran)
    
  def test_two_word_arg(self):
    def f(dry_run=False):
      self.assertEquals(dry_run,True)
      self.ran = True
    darp.prep(f).run('cmd.py --dry-run'.split())
    self.assertTrue(self.ran)
    
    
    
if __name__ == '__main__':
  unittest.main()

