#/usr/bin/env python

from scipy import stats
from tkinter import *
import webcolors
import statistics
import sys
import time
import re
import os

def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)

        actual_name = None
    switcher = {
        "yellowgreen": "Yellow Green",
        "lightgreen": "Light Green",
        "greenyellow": "Green Yellow",
        "darkblue": "Dark Blue",
        "deepskyblue": "Deep Sky Blue",
        "darkorange": "Dark Orange",
        "dodgerblue": "Dodger Blue",
        "mediumaquamarine": "Medium Aqua Marine",
        "firebrick": "Fire Brick",
        "orangered": "Orange Red",
        "mediumblue": "Medium Blue",
        "darkred": "Dark Red",
    }
    closest_name = switcher.get(closest_name, closest_name)
    return closest_name

#https://www.oreilly.com/library/view/python-cookbook/0596001673/ch09s11.html
def floatRgb(mag, cmin, cmax):
    """ Return a tuple of floats between 0 and 1 for R, G, and B. """
    # Normalize to 0-1
    try: x = float(mag-cmin)/(cmax-cmin)
    except ZeroDivisionError: x = 0.5 # cmax == cmin
    r = min(max(0, 1.5 - abs(1 - 4 * (x - 0.5))), 1)
    g = min(max(0, 1.5 - abs(1 - 4 * (x - 0.25))), 1)
    b = min(max(0, 1.5 - abs(1 - 4 * x)), 1)
    return r,g,b

def rgb(mag, cmin, cmax):
    """ Return a tuple of integers, as used in AWT/Java plots. """
    red, green, blue = floatRgb(mag, cmin, cmax)
    return int(red*255), int(green*255), int(blue*255)

def strRgb(mag, cmin, cmax):
    """ Return a hex string, as used in Tk plots. """
    return "#%02x%02x%02x" % rgb(mag, cmin, cmax)


if int(sys.argv[2]) < 4000:
    offsetRangeHalf = 120
else:
    offsetRangeHalf = 200

MASTER = Tk()
MASTER.title('Color Mapping...')
simage = PhotoImage(file="./ritimg.png")
sanvas = Canvas(MASTER, width=500, height=625)
sanvas.create_image(250, 400, image=simage, anchor=CENTER)
sanvas.create_text(110, 450, text="Your fingerprint color:",font=('Helvetica', '16'),fill='white' )
dataStr = StringVar()
datalabel = Label(MASTER, justify=LEFT, textvariable=dataStr, bg='#303030', anchor='s', font=("verdana",24))
datalabel.place(relx=0.01,rely=0.732)
dataStr.set("Calculating initial estimate")
sanvas.pack()
MASTER.update()

cmin = -1 * offsetRangeHalf
cmax = offsetRangeHalf
cum_sum = 0

sys.stdout.write("Samples taken: 0%\r")
sys.stdout.flush()

time.sleep(5)

trim = .2

sample_means = []

samples = []
sample_count = 0


for line in sys.stdin:
    # Regex is for losers. I don't have that kind of time.
    if re.match("^Short: [0-9]+.[0-9]+\tLong: [0-9]+.[0-9]+\tTotal CFO: [0-9]+.[0-9]+", line):
        line = line.split("\t")
        cfo = float(line[0].split(" ")[1]) + float(line[1].split(" ")[1])
        sample_count += 1
        samples.append(cfo)
        cum_sum += cfo
        if sample_count % 100 == 0:
            Liveaverage = cum_sum / sample_count
            try:
                colorHex = strRgb(Liveaverage, cmin, cmax)
                sanvas.configure(background=colorHex)
                rgbColor = rgb(Liveaverage, cmin, cmax)
                closest_name = get_colour_name(rgbColor)
                dataStr.set(closest_name.capitalize())
                datalabel.configure(fg=colorHex)
                MASTER.update()
            except:
                pass
        if sample_count % 1000 == 0:
            sample_means.append(stats.trim_mean(samples, trim)) # Remove (trim) percentage of outliers
            samples = []
            sys.stdout.write("Samples taken: {}\r".format(sample_count))
            sys.stdout.flush()
            if len(sample_means) == 3:
                break

sanvas.create_text(118, 558, text="Hex Color Code: "+ str(colorHex) + "\nAveraged CFO: "+ str(round(Liveaverage,5))+ " kHz",font=('Helvetica', '13'),fill='white')
MASTER.title('Color Mapped!')
MASTER.update()

print()

if len(sample_means) == 0:
    print("Error communicating with device.")
    exit(1)

print("Samples collected:\t{}".format(sample_count))
mean_estimator = statistics.mean(sample_means)
print("Estimated CFO:\t\t{}".format(statistics.mean(sample_means))) # Remove (trim) percentage of outliers
stdev_estimator = statistics.stdev(sample_means)
print("Std deviation:\t\t{}".format(statistics.stdev(sample_means)))

devices = []

if not os.path.isfile("seen_devices.csv"): 
    print("No database to search. Have a nice day.")
    exit(0)

with open("seen_devices.csv", "r") as f:
    for line in f:
        line = line.strip().split(",")
        devices.append((line[0], float(line[1]), float(line[2])))

norms = []

for device in devices:
    norms.append(stats.norm(device[1], device[2]))

largest = 0

total_value = 0
values = []
for n, function in enumerate(norms):
    value = function.pdf(mean_estimator)
    if largest < value:
        largest = value
        top_dog = devices[n][0]
    total_value += value
    values.append(value)


for n, percentage in enumerate(norms):
    print("Device: {}\tProbability: {} %".format(devices[n][0], round(values[n] / total_value * 100, 10)))

try: # maybe I forget to define the real device or I don't know.
    if top_dog == sys.argv[1]:
        print("\n\033[94mDevice matched successfully.\033[0m\n")
    else:
        print("\n\033[91mGuessed device: {}\tReal device: {}\033[0m\n".format(top_dog, sys.argv[1]))
except IndexError:
    pass

input()

exit(0)
