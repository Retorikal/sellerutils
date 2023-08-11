import itertools
from time import time

l1 = list(range(1000))
l2 = list(range(1000))

print('Alternative 1. Itertools')
t = time()
for j in range(10000):
  s = 0
  for i in itertools.chain(l1, l2):
    s += i
print(time() - t)

print('Alternative 2. Naive')
t = time()
for j in range(10000):
  s = 0
  for i in [*l1, *l2]:
    s += i
print(time() - t)

print('Alternative 3. Yield')


def chain(*ls):
  for l in ls:
    for k in l:
      yield k


t = time()
for j in range(10000):
  s = 0
  for i in chain(l1, l2):
    s += i
print(time() - t)
