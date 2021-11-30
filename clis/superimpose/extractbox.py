import numpy
import scipy
import sys

sys.path.append("./common")
import gridfield

kontfilename1 = ""

if (len(sys.argv)) == 2:
    kontfilename1 = sys.argv[1]
else:
    print(("usage :" + sys.argv[0] + " filename1.kont "))
    exit(1)

energy1, energy1_coords, \
        botx, boty, botz, topx, topy, topz, dx, dy, dz, nx, ny, nz \
        = gridfield.read_kontfile(kontfilename1)


print(str(botx)+";"+str(topx)+";"+str(boty)+";"+str(topy)+";"+str(botz)+";"+str(topz))
