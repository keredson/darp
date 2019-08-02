import darp


# $ python3 example_squashed_existence.py -ab
# apple True
# banana True



def doit(apple=False, banana=False):
  print('apple', apple)
  print('banana', banana)
  
if __name__=='__main__':
  darp.prep(doit, a='apple', b='banana').run()
