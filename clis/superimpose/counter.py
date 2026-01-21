import mendeleev
import sys

sys.path.append("./common")
import gridfield

###############################################################

class atom:

  def __init__ (self, id, name, x, y, z, c):
    self.id = id
    self.name = name
    self.coords = (x, y, z)
    self.partialcharge = c
    self.resname = ""
    self.atomname = ""
    self.id = 0
    self.element = ""
    self.radii = 0.0
    self.residueid = 0
  
  def __repr__ (self):
    line = "%6d %6s %6s %10.5f %10.5f %10.5f %8.5f %3s\n"%( \
      self.id, self.name, self.resname, self.coords[0], \
      self.coords[1], self.coords[2], self.partialcharge, \
      self.atomname)

    return line
  
###############################################################

def pdbatomextractor (file=None):

  from Bio.PDB.PDBParser import PDBParser
  
  parser=PDBParser(PERMISSIVE=1)
  
  structure = parser.get_structure("singelemodel", file)

  mols = []

  for model in structure:

    id = 1
    mol = []
    for chain in model:
      for residue in chain:
        for a in residue:
          coords = a.get_coord()
          #print(id, residue.get_resname(), a.get_name(), coords)
          na = atom(id, a.get_name(), coords[0], coords[1], coords[2], 0.0 )
          na.id = id
          na.resname = residue.get_resname()
          na.residueid = residue.get_id()[1]
          na.atomname = a.get_name()
          na.element = a.element
          if na.element == "ZN":
            na.element = "Zn"
          na.radii = mendeleev.element(na.element).vdw_radius

          mol.append(na)
          id += 1

    mols.append(mol)

  return mols

###############################################################


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

if energy_coords is None:
    print("Error reading kont file " + kontfilename)
    exit(1)

coords = []
radii = []

mol = pdbatomextractor(pdbfilename)[0]
for atom in mol:
    coords.append(atom.coords)
    radii.append(atom.radii)

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
