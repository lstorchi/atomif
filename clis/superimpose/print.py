import openbabel
import pybel
import sys

sys.path.append("./common")
import gridfield

kontfilename = ""

if (len(sys.argv)) == 2:
    kontfilename = sys.argv[1]
else:
                                
    print("usage :", sys.argv[0] , " filename.kont filename.pdb ")
    exit(1)

energy, energy_coords, \
        botx, boty, botz, topx, topy, topz, dx, dy, dz, nx, ny, nz, \
        = gridfield.read_kontfile(kontfilename)

print(botx,";",topx,";",boty,";",topy,";",botz,";",topz)


