#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304. C0411
# This script will simulate the ouput of the Elegoo and Nano portions

# Encoder testing data reference:
# PWM     50              100             150
# L Encd  69.75429568	  130.0175577     203.0123211
# R Encd  68.46070675	  123.2839752	  194.4117992
# % Diff   1.88953488       5.4618473	    4.4238683

k = 5.46 # $ diff from encoder testing Left/Right at 100 PWM
r_encd = 1
l_encd = k * r_encd


import json
import socket


def main_function():
    pass


if __name__ == "__main__":
    main_function()