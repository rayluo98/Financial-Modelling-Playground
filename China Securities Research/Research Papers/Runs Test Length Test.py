from random import random
from random import seed
import matplotlib.pyplot as plt
seed(13)
sequence = [0]*10000
for i in range(1, 10000):
    if random() > 0.5:
        sequence[i] = 1
    else:
        sequence[i] = 0

plt.figure(1)
plt.plot(sequence)
plt.axis([0, 100, 0, 2])
plt.show()


frequency = [0]*1000
run_type = sequence[0]
run_count = 0
for j in range(1,10000):
    if sequence[j] != run_type:
        frequency[run_count] += 1
        run_type = sequence[j]
        run_count = 0
    else:
        run_count += 1
plt.figure(2)
plt.plot(frequency)
plt.axis([0,15, 0, 5000])
plt.show()


plt.figure(3)
plt.axis([0,15,0, 1000])
plt.hist(frequency, range = (0, 15), bins = "auto")
plt.show()
