#!/usr/bin/env python

import copy
import readline
import sys

class SimpleCompleter(object):

  def __init__(self, options):
    self.options = sorted(options)
    return

  def complete(self, text, state):
    response = None
    if state == 0:
      # This is the first time for this text, so build a match list.
      if text:
        self.matches = [s for s in self.options if s and s.startswith(text)]
      else:
        self.matches = self.options[:]

    # Return the state'th item from the match list, if we have that many.
    try:
      response = self.matches[state]
    except IndexError:
      response = None
    return response

class PandemicInfections(object):

  def __init__(self, cities):
    self.cities = cities
    self.stack = [copy.copy(cities)]
    self.cards_drawn = []
    self.current_pile = self.stack[-1]

  def draw_card(self, line):
    self.cards_drawn.append(line)
    assert(self.current_pile)
    self.current_pile.remove(line)
    if not self.current_pile:
      self.current_pile = self.stack.pop()

  def epidemic(self):
    question = 'Which city was drawn from the bottom in the Epidemic? '
    impossible = 'This is impossible!'
    line = input(question)
    assert(self.stack)
    front_pile = self.stack[0]
    self.stack.remove(front_pile)
    while not line in front_pile:
      print(impossible)
      line = input(question)
    front_pile.remove(line)
    self.cards_drawn.append(line)
    if front_pile:
      self.stack.insert(0, front_pile)
    self.stack.append(sorted(self.cards_drawn))
    self.cards_drawn = []

  def print_state(self, f=sys.stdout):
    i = 0
    print('', file=f)
    print('############################', file=f)
    print('###       The Deck       ###', file=f)
    for x in self.stack:
      for city in x:
        print(i, city, file=f)
      print('----------------------------', file=f)
      i += 1
    print('############################', file=f)
    print('', file=f)
    print('############################', file=f)
    print('###       Discard        ###', file=f)
    for city in self.cards_drawn:
      print('d', city, file=f)
    print('############################', file=f)

  def write_state(self):
    with open('state.txt', 'w') as f:
      self.print_state(f=f)

  def read_state(self):
    self.stack = []
    self.cards_drawn = []

    prev_level = 0
    temp = []
    with open('state.txt', 'r') as f:
      for line in f:
        line = line.strip('\n')
        if line.startswith('#') or line.startswith('-') or not line:
          continue
        level, city = line.split(' ')
        if level == 'd':
          self.cards_drawn.append(city)
        else:
          if level == prev_level:
            temp.append(city)
          else:
            if temp:
              self.stack.append(temp)
            temp = []
            temp.append(city)
            prev_level = level
      if temp:
        self.stack.append(temp)

  def calculate_probability(self, city, N):
    toy_stack = copy.deepcopy(self.stack)
    toy_pile = toy_stack.pop()

    total_prob = 0.0
    for i in range(N):
      total = len(toy_pile)
      count = toy_pile.count(city)
      probability = count/total
      total_prob += (1.0 - total_prob) * probability
      if total_prob == 1.0:
        return total_prob
      for x in toy_pile:
        if x != city:
          toy_pile.remove(x)
          break
      else:
        assert(False)
      if not toy_pile:
        toy_pile = toy_stack.pop()
    return total_prob

  def print_probabilities(self):
    print()
    print('%-15s %6d %6d %6d %6d %6d' % ('Name', 1, 2, 3, 4, 5))
    for x in sorted(set(self.cities)):
      line = '%-15s ' % x
      for n in range(1,6):
        p = self.calculate_probability(x, n)
        line += "%5.1f%% " % (100.0 * p)
      print(line)
    print()

  def input_loop(self):
    question = 'Please enter the name of the city which was drawn or "Epidemic": '
    impossible = 'This is impossible!'
    line = ''
    while True:

      # Get new input
      line = input(question)
      while line != 'Epidemic' and line != 'Read' and not line in self.current_pile:
        print(impossible)
        line = input(question)

      # Process
      if line == 'Read':
        self.read_state()
      elif line == 'Epidemic':
        self.epidemic()
      else:
        self.draw_card(line)

      # Print current state
      self.print_state()
      self.write_state()
      self.print_probabilities()

cities = []

# Black
cities += 3*['Kairo']
cities += 3*['Istanbul']
cities += 3*['Tripolis']

# Blue
cities += 3*['London']
cities += 3*['NewYork']
cities += 3*['Washington']

# Yellow
cities += 3*['Jacksonville']
cities += 3*['SaoPaolo']
cities += 3*['Lagos']

# Register the completer function and bind tab
options = copy.copy(cities)
options.append('Read')
options.append('Epidemic')
options = sorted(set(options))
readline.set_completer(SimpleCompleter(options).complete)
readline.parse_and_bind('tab: complete')

# Start the input loop
p = PandemicInfections(cities=cities)
p.input_loop()
