from tkinter import *
import time
import webcolors


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
    return actual_name, closest_name

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

def main():
    ifile = sys.argv[1]
    spectrum = sys.argv[2][0]
    if int(spectrum) < 4000:
        offsetRangeHalf = 120
    else:
        offsetRangeHalf = 200
    sample_count = 0
    MASTER = Tk()
    MASTER.geometry("500x500")
    colorStr = StringVar()
    label = Label(MASTER, textvariable=colorStr)
    cmin = -1 * offsetRangeHalf
    cmax = offsetRangeHalf
    with open(ifile) as f:
        sum = 0
        for line in f.readlines():
            try:
                cfo = float(line.strip())
                sample_count += 1
                sum = sum + cfo
                Liveaverage = sum / sample_count
                time.sleep(.05)
                colorHex = strRgb(Liveaverage, cmin, cmax)
                print(str(colorHex) + " " + str(Liveaverage))
                rgbColor = rgb(Liveaverage, cmin, cmax)
                actual_name, closest_name = get_colour_name(rgbColor)
                print(" Offset:", Liveaverage, ", closest colour name:", closest_name)
                colorStr.set(colorHex + "   " + str(Liveaverage) + "   " + closest_name)
                label.pack()
                MASTER.configure(background=colorHex)
                MASTER.update()
            except:
                continue
        label.configure(font=(95))
        label.pack()
        MASTER.update()
    # used to test out the range of colors in the current spectrum
    # offset = -1 * offsetRangeHalf
    # cmin = -1 * offsetRangeHalf
    # cmax = offsetRangeHalf
    # while offset < (offsetRangeHalf)+1:
    #     break
    #     #offset = offset + offsetRangeHalf
    #     rgbColor = rgb(offset, cmin, cmax)
    #     actual_name, closest_name = get_colour_name(rgbColor)
    #     #print(str(rgbColor) + " " + closest_name)
    #     colorStr.set(strRgb(offset, cmin, cmax) + "   " + str(offset) + "   " + closest_name)
    #     print(" Offset:", offset, ", closest colour name:", closest_name+str(offset))
    #     label.pack()
    #     MASTER.configure(background=strRgb(offset, cmin, cmax))
    #     MASTER.update()
    #     offset = offset + 1
    input()

main()
