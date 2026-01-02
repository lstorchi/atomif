from openbabel import openbabel
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
obconversion = openbabel.OBConversion()
obconversion.SetInFormat("pdb")
mol = openbabel.OBMol()
obconversion.ReadFile(mol, pdbfilename)

vdw_radii = {
    1: 1.20,  # H
    6: 1.70,  # C
    7: 1.55,  # N
    8: 1.52,  # O
    9: 1.47,  # F
    15: 1.80, # P
    16: 1.80, # S
    17: 1.75, # Cl
    # Add others as needed. Default fallback usually ~1.5 or 2.0
}

for atom in openbabel.OBMolAtomIter(mol):
    coords.append((atom.GetX(), atom.GetY(), atom.GetZ()))
    
    # 2. Look up the radius using the atomic number
    atomic_num = atom.GetAtomicNum()
    # .get(key, default) prevents crashes for unknown elements
    radii.append(vdw_radii.get(atomic_num, 2.0))

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
