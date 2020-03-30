#!/usr/bin/env python

import copy
import readline

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

stack = []
current_pile = copy.copy(cities)
cards_drawn = []

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

def draw_card(line):
  global cards_drawn, current_pile
  cards_drawn.append(line)
  assert(len(current_pile) > 0)
  current_pile.remove(line)
  if not current_pile:
    current_pile = stack.pop()

def epidemic():
  global stack, current_pile, cards_drawn
  question = 'Which city was drawn from the bottom in the Epidemic? '
  impossible = 'This is impossible!'
  line = input(question)
  if len(stack) > 0:
    front_pile = stack[0]
    stack.remove(front_pile)
    while not line in front_pile:
      print(impossible)
      line = input(question)
    front_pile.remove(line)
    cards_drawn.append(line)
    if len(front_pile) > 0:
      stack.insert(0, front_pile)
  else:
    while not line in current_pile:
      print(impossible)
      line = input(question)
    current_pile.remove(line)
    cards_drawn.append(line)
  if len(current_pile) > 0:
    stack.append(current_pile)
  stack.append(sorted(cards_drawn))
  current_pile = stack.pop()
  cards_drawn = []

def calculate_probability(city, N):
  global stack, current_pile
  toy_stack = copy.deepcopy(stack)
  toy_pile = copy.deepcopy(current_pile)

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
    if len(toy_pile) == 0:
      toy_pile = toy_stack.pop()
  return total_prob

def print_state():
  global stack, current_pile, cards_drawn
  i = 0
  print()
  print('############################')
  print('###       The Deck       ###')
  for x in stack:
    for city in x:
      print(i, city)
    print('----------------------------')
    i += 1
  for city in current_pile:
    print('c', city)
  print('############################')
  print()
  print('############################')
  print('###       Discard        ###')
  for city in cards_drawn:
    print('d', city)
  print('############################')

def write():
  global stack, current_pile, cards_drawn
  i = 0
  with open('state.txt', 'w') as f:
    print('############################', file=f)
    print('###       The Deck       ###', file=f)
    for x in stack:
      for city in x:
        print(i, city, file=f)
      print('----------------------------', file=f)
      i += 1
    for city in current_pile:
      print('c', city, file=f)
    print('############################', file=f)
    print('', file=f)
    print('############################', file=f)
    print('###       Discard        ###', file=f)
    for city in cards_drawn:
      print('d', city, file=f)
    print('############################', file=f)

def read():
  global stack, current_pile, cards_drawn
  stack = []
  current_pile = []
  cards_drawn = []

  prev_cat = 0
  temp = []
  with open('state.txt', 'r') as f:
    for line in f:
      line = line.strip('\n')
      if line.startswith('#') or line.startswith('-') or not line:
        continue
      cat, city = line.split(' ')
      print(cat, city)
      if cat == 'c':
        current_pile.append(city)
      elif cat == 'd':
        cards_drawn.append(city)
      else:
        if cat == prev_cat:
          temp.append(city)
        else:
          stack.append(temp)
          temp = []
          temp.append(city)
          prev_cat = cat

def print_probabilities():
  global cities
  print()
  print('%-15s %6d %6d %6d %6d %6d' % ('Name', 1, 2, 3, 4, 5))
  for x in sorted(set(cities)):
    line = '%-15s ' % x
    for n in range(1,6):
      p = calculate_probability(x, n)
      line += "%5.1f%% " % (100.0 * p)
    print(line)
  print()

def input_loop():
  global stack, current_pile, cards_drawn
  question = 'Please enter the name of the city which was drawn or "Epidemic": '
  impossible = 'This is impossible!'
  line = ''
  while True:

    # Get new input
    line = input(question)
    while line != 'Epidemic' and line != 'Read' and not line in current_pile:
      print(impossible)
      line = input(question)

    # Process
    if line == 'Read':
      read()
    elif line == 'Epidemic':
      epidemic()
    else:
      draw_card(line)

    # Print current state
    print_state()
    write()
    print_probabilities()

# Register the completer function and bind tab
options = copy.copy(cities)
options.append('Read')
options.append('Epidemic')
options = sorted(set(options))
readline.set_completer(SimpleCompleter(options).complete)
readline.parse_and_bind('tab: complete')

# Start the input loop
input_loop()
