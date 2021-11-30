import openbabel
import pybel
import sys

sys.path.append("./common")
import gridfield

ELIMIT = -0.5

kontfilename = ""
pdbfilename = ""

if (len(sys.argv)) == 3:
    kontfilename = sys.argv[1]
    pdbfilename = sys.argv[2]                        
else:
                                
    print(("usage :" + sys.argv[0] + " filename.kont filename.pdb "))
    exit(1)

energy, energy_coords, \
        _ , _ , _ , _ , _ , _ , _ , _ , _ , _ , _ , _  \
        = gridfield.read_kontfile(kontfilename)

coords = []
radii = []
mol = next(pybel.readfile("pdb", pdbfilename))
pt = openbabel.OBElementTable()
for atom in mol:
    coords.append(atom.coords)
    radii.append(pt.GetVdwRad(atom.OBAtom.GetAtomicNum ())) 

maxdist = 10
counter_multiple = []
energy_multiple = []
counted = []

for i in range(maxdist):
    counter_multiple.append(0)
    energy_multiple.append(0.0)

for iy in range(energy_coords.shape[1]):
    for ix in range(energy_coords.shape[0]):
        for iz in range(energy_coords.shape[2]):
            x, y, z, n = energy_coords[ix, iy, iz] 
            e = energy[ix, iy, iz]

            if e <= ELIMIT:
            
               counted = [False] * maxdist
               
               for ai in range(len(coords)):
                   ax, ay, az = coords[ai]
               
                   dist = (ax-x)**2 + (ay-y)**2 + (az-z)**2 
               
                   for i in range(maxdist):
                       if dist <= float(i+1) and (not counted[i]):
                           counter_multiple[i] += 1
                           energy_multiple[i] += e
                           counted[i] = True

sys.stdout.write (kontfilename + " " + pdbfilename + " , ")
for i, v in enumerate(counter_multiple):
    if i:
        sys.stdout.write(" , ")
    sys.stdout.write(str(v))
    sys.stdout.write(" , ")
    sys.stdout.write(" %10.5f "%(energy_multiple[i]))
sys.stdout.write("\n")
