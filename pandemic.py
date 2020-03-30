#!/usr/bin/env python

import copy
import readline
import sys
import re

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

  def __init__(self, cities_file, state_filename='state.txt'):
    self.cities = []
    self.stack = []
    self.cards_drawn = []
    self.state_filename = state_filename
    self.level = 2
    self.setup(cities_file)

  def setup(self, cities_file):
    self.read_cities(cities_file)
    self.stack = [copy.copy(self.cities)]
    # Register the completer function and bind tab
    options = copy.copy(self.cities)
    options = sorted(set(options), key=options.index)
    options.append('READ')
    options.append('EPIDEMIC')
    readline.set_completer(SimpleCompleter(options).complete)
    readline.parse_and_bind('tab: complete')

  def set_level(self):
    question = 'Set infection level to? '
    impossible = 'Invalid input! Please enter a number.'
    line = input(question)
    while not re.match('^\d+$', line):
      print(impossible)
      line = input(question)
    self.level = int(line)

  def read_cities(self, filename):
    # Read input file with city names.
    self.cities = []
    with open(filename, 'r') as f:
      for line in f:
        line = line.strip('\n')
        if not line or line.startswith('#'):
          continue
        if '*' in line:
          n, city = line.split('*')
          self.cities += int(n) * [city]
        else:
          self.cities += [line]

  def draw_card(self, line):
    # Draw card from the top of the stack and add it to the discard pile.
    self.cards_drawn.append(line)
    assert(self.stack[-1])
    self.stack[-1].remove(line)
    if not self.stack[-1]:
      self.stack.pop()

  def epidemic(self):
    question = 'Which city was drawn from the bottom in the Epidemic? '
    impossible = 'This is impossible!'
    # Draw card from front of the stack ("the bottom")
    line = input(question)
    assert(self.stack)
    front_pile = self.stack[0]
    while not line in front_pile:
      print(impossible)
      line = input(question)
    self.cards_drawn.append(line)
    # Remove card from front pile and remove it from the stack if it is now empty.
    front_pile.remove(line)
    if not front_pile:
      del self.stack[0]
    # Push discard pile on stack and reset it.
    self.stack.append(sorted(self.cards_drawn))
    self.cards_drawn = []

  def print_state(self, f=sys.stdout):
    # Print the draw deck with sections
    i = 0
    print('', file=f)
    print('############################', file=f)
    print('###       The Deck       ###', file=f)
    for x in self.stack:
      for city in sorted(set(x), key=lambda v: x.count(v), reverse=True):
        print('%d * %s' % (x.count(city), city), file=f)
      i += 1
      if i != len(self.stack):
        print('----------------------------', file=f)
    print('############################', file=f)
    # Print the discard pile
    print('', file=f)
    print('############################', file=f)
    print('###       Discard        ###', file=f)
    for city in sorted(set(self.cards_drawn), key=lambda v: self.cards_drawn.count(v), reverse=True):
      print('%d * %s' % (self.cards_drawn.count(city), city), file=f)
    print('############################', file=f)

  def write_state(self):
    # Write the current state to disk
    with open(self.state_filename, 'a') as f:
      self.print_state(f=f)

  def read_state(self):
    # Read the current state from disk
    self.stack = []
    self.cards_drawn = []
    phase = ''
    with open(self.state_filename, 'r') as f:
      for line in f:
        line = line.strip('\n')
        if 'The Deck' in line:
          self.stack = [[]]
          self.cards_drawn = []
          phase = 'deck'
        elif 'Discard' in line:
          phase = 'discard'
        if phase == 'deck' and line.startswith('-----'):
          self.stack.append([])
        if not re.search('^\d+ \* \w+$', line):
          continue
        occurences, _, city = line.split(' ')
        for k in range(int(occurences)):
          if phase == 'deck':
            self.stack[-1].append(city)
          elif phase == 'discard':
            self.cards_drawn.append(city)
          else:
            assert(False)

  def calculate_probability(self, city, N):
    # Calculate the probability to draw city at least once in N draws.
    toy_stack = copy.deepcopy(self.stack)
    N_cards = sum([len(x) for x in toy_stack])
    N = min(N, N_cards)
    total_prob = 0.0
    toy_pile = toy_stack.pop()
    for i in range(N):
      if not toy_pile:
        assert(toy_stack)
        toy_pile = toy_stack.pop()
      total = len(toy_pile)
      assert(total > 0)
      count = toy_pile.count(city)
      probability = count / total
      total_prob += (1.0 - total_prob) * probability
      if total_prob == 1.0:
        return total_prob
      for x in toy_pile:
        if x != city:
          toy_pile.remove(x)
          break
      else:
        assert(False)
    return total_prob

  def print_all_probabilities(self, f=sys.stdout):
    # Print probabilities
    print('', file=f)
    print('%-15s %11d %11d %11d %11d %11d' % ('Name', 1, 2, 3, 4, 5), file=f)
    print('---------------------------------------------------------------------------', file=f)
    for x in sorted(set(self.cities), key=self.cities.index):
      line = '%-15s ' % x
      for n in range(1,6):
        p = self.calculate_probability(x, n)
        line += "%10.1f%% " % (100.0 * p)
      print(line, file=f)

  def print_probabilities(self, f=sys.stdout):
    # Print probabilities
    print('', file=f)
    print('%-15s %6s' % ('Name', 'N=%d'% self.level), file=f)
    print('----------------------', file=f)
    probabilities = [ (x, self.calculate_probability(x, self.level)) for x in set(self.cities) ]
    for x, p in sorted(probabilities, key=lambda x: x[1], reverse=True):
      line = '%-15s ' % x
      line += "%5.1f%%" % (100.0 * p)
      print(line, file=f)

  def write_probabilities(self):
    # Write the current state to disk
    with open(self.state_filename, 'a') as f:
      self.print_probabilities(f=f)

  def write_all_probabilities(self):
    # Write the current state to disk
    with open(self.state_filename, 'a') as f:
      self.print_all_probabilities(f=f)

  def run(self):
    # The main input loop
    question = 'Please enter the name of the city which was drawn or "EPIDEMIC/READ": '
    impossible = 'This is impossible!'
    while True:
      # Get new input
      print()
      line = input(question)
      while line not in ['EPIDEMIC', 'READ', 'LEVEL'] and not line in self.stack[-1]:
        print(impossible)
        line = input(question)
      # Process
      if line == 'LEVEL':
        self.set_level()
      elif line == 'READ':
        self.read_state()
      elif line == 'EPIDEMIC':
        self.epidemic()
      else:
        self.draw_card(line)
      # Print current state and probabilities, write state to disk
      self.print_state()
      self.print_probabilities()
      self.write_state()
      self.write_probabilities()

# Start the input loop
cities_file = sys.argv[1]
output_file = sys.argv[2] if len(sys.argv) > 2 else 'state.txt'
p = PandemicInfections(cities_file=cities_file, state_filename=output_file)
p.run()
