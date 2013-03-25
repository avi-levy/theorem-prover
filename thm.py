#!/usr/bin/env python
cutoff = 200

from sys import argv
import heapq # for the priority queue we use to sort the knowledge base
from operator import itemgetter # for the re-sort we use while dumping out the knowledge base at the end

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
  for m in a:
    for n in b:
      if m.name == n.name and m.modifier != n.modifier:
        # We have found a pair of negated literals, i.e. L ~L
        c = set(a)
        d = set(b)
        c.remove(m)
        d.remove(n)
        # Union the clauses, but after removing the negated pair
        return (True, frozenset(c.union(d)))
  return (False, None)

def nextStatement(states):
  """Iterate through the kb until a pair of statements can be resolved.
  If the resolution is novel, add it to the kb
  
  """
  global t
  for l1, c1, p1, t1 in states:
    for l2, c2, p2, t2 in states:
      if t1 != t2:
        success, clause = resolve(c1, c2)
        if success:
          if not (clause in map(itemgetter(1), states)):
            t += 1
            heapq.heappush(states, (len(clause), clause, [t1,t2], t))
            return clause
  # We got stuck
  return False
          
def dump(states):
  """Print out the kb in a nicer format"""
  for l, clause, parents, t in sorted(states, key = itemgetter(3)):
    print "%s.  %s  {%s}" % (t, # print the theorem number, but using 1-based indexing
      ' '.join(
        {(x.name if x.modifier else '~' + x.name) for x in clause} # write out an abbreviated string representing the clause
        ) if clause else False,
      ','.join(map(str,parents))) # again, use 1-based indexing
  
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
t = 0
# read the input file
with open(infile) as infile:
  for line in infile:
    # increment the time parameter
    t += 1
    # parse the line as a set of Literals
    literals = line.split()
    # then append to the kb, which is actually a heap sorted on clause length
    heapq.heappush(states, (len(literals), frozenset({Literal(x) for x in literals}), [], t))
    # the tuple values are: 1. length of clause 2. set of literals 3. parent clauses that we were derived from

for counter in range(cutoff):
  # If we generate false, then break
  if not nextStatement(states):
    break
dump(states)
