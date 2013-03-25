#!/usr/bin/env python
cutoff = 200

from sys import argv

class Literal:
  """A literal is a an atom or a negated atom"""
  def __init__(self, name, modifier):
    self.name = name
    self.modifier = modifier
  def __init__(self, string):
    if string[0] == '~':
      self.name = string[1:]
      self.modifier = False
    else:
      self.name = string
      self.modifier = True
  # These methods are for equality testing and hashing (so that we can use sets of Literals later on)
  def __eq__(self, other):
    return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)  
  def __ne__(self, other):
    return not self.__eq__(other)
  def __hash__(self):
    return hash((self.name, self.modifier))
    
def resolve(a,b):
  """Given two clauses a and b, try to resolve them.
  Returns a tuple of the form (SuccessValue, NewClause)
  where SuccessValue is a boolean
  and NewClause is the resolved clause (if SuccessValue is True; otherwise, it is None)
  In terms of implementation, a and b can be any iterables of literals, although in practice they will be frozensets of literals.
  NewClause is implemented as a frozenset of literals.
  
  """
  for lit1 in a:
    for lit2 in b:
      if lit1.name == lit2.name and lit1.modifier != lit2.modifier:
        # We have found a pair of negated literals, i.e. L ~L
        c = set(a)
        d = set(b)
        c.remove(lit1)
        d.remove(lit2)
        # Union the clauses, but after removing the negated pair
        return (True, frozenset(c.union(d)))
  return (False, None)

def nextStatement(states):
  """Iterate through the kb until a pair of statements can be resolved.
  If the resolution is novel, add it to the kb
  
  """
  for i, state1 in enumerate(states):
    for j, state2 in enumerate(states):
      if i != j:
        k = resolve(state1[0], state2[0])
        if k[0]:
          if not ( k[1] in {x[0] for x in states} ):
            states.append([k[1], set([i,j])])
            return k[1]
          
def dump(states):
  """Print out the kb in a nicer format"""
  for i, state in enumerate(states):
    print "%s.  %s  {%s}" % (i+1, ' '.join({(x.name if x.modifier else '~' + x.name) for x in state[0]}) if state[0] else False, ','.join(str(s+1) for s in state[1]))
  
usage = "usage: thm infile.in"
def end(message=usage):
  print message
  exit(0)

if len(argv) != 2:
  end()
  
filename, infile = argv

if not infile.endswith('.in'):
  end()
    
states = []
    
# read the input file
with open(infile) as infile:
  for line in infile:
    # parse the line as a set of Literals, then append to the kb
    states.append([frozenset({Literal(x) for x in line.split()}),set()])

for counter in range(cutoff):
  # If we generate false, then break
  if not nextStatement(states):
    break
dump(states)
