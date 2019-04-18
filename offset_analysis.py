#/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import statistics
import sys
import os

ifile = sys.argv[1]

trim = .2

samples = []
sample_count = 0
with open(ifile) as input_file:  
    for line in input_file:
        # Regex is for losers. I don't have that kind of time.
        if "Short: " in line and "CFO" in line:
            line = line.split("\t")
	    try:
                cfo = float(line[0].split(" ")[1]) + float(line[1].split(" ")[1])
	    except:
                pass
            sample_count += 1
            samples.append(cfo)

print("Samples collected:\t{}".format(sample_count))
trimmed_mean = stats.trim_mean(samples, trim) # Remove (trim) percentage of outliers
print("Estimated CFO:\t\t{}".format(trimmed_mean)) # Remove (trim) percentage of outliers
print("Sample variance:\t{}".format(statistics.variance(samples)))
print("Sample mu:\t\t{}".format(statistics.stdev(samples)))

csv_file = os.path.splitext(ifile)[0] + ".csv"

x_axis = []
item_count = 0

with open(csv_file,'w') as f:
    for item in samples:
        f.write(str(item) + '\n')
        x_axis.append(item_count)
        item_count += 1
    f.write('\n')

plt.scatter(x_axis, samples)
plt.ylabel('Estimated carrier frequency offset value of a single packet')
plt.xlabel('Time')
plt.text(0, max(samples) * .9, "Estimated device CFO: " + str(trimmed_mean) + "\nTrimming: %" + str(trim*100))
plt.savefig(os.path.splitext(ifile)[0] + ".png")
plt.show()

if not os.path.isfile("./CFO_data/CFO_estimates.csv"):
    with open(csv_file,'w') as f:
        f.write("CFO,Sample size,Trim\n")

with open("./CFO_data/CFO_estimates.csv", 'a') as f:
    f.write(str(trimmed_mean) + "," + str(sample_count) + "," + str(trim) + "\n")

#os.remove(ifile)

devices = []

with open("fingerprints.csv", "r") as f:
    for line in f:
        line = line.strip().split(",")
        devices.append((line[0], float(line[1]), float(line[2])))

norms = []

for device in devices:
    norms.append(stats.norm(device[1], device[2]))

for n, function in enumerate(norms):
    print("Device: {}\tProbability: {}%".format(devices[n][0], function.pdf(trimmed_mean)*100))
