import os

###############################################################

class atom:

  def __init__ (self, id = 0, name = "", x = 0.0, y = 0.0, z = 0.0, c = 0.0):
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
          #na.radii = mendeleev.element(a.element).vdw_radius

          mol.append(na)
          id += 1

    mols.append(mol)

  return mols

###############################################################

def mol2atomextractor (file=None, readresname= False):
  
  mols = []

  with open(file, 'r') as f:
    mol = []
    readatom = False
    while not f.tell() == os.fstat(f.fileno()).st_size:
      line = f.readline()
      wsline = "".join(line.split())
      if wsline == "@<TRIPOS>ATOM":
        readatom = True
        line = f.readline()
        mol = []

      if line.startswith("@<TRIPOS>") and \
        wsline != "@<TRIPOS>ATOM":
        if (readatom):
          mols.append(mol)
          readatom = False

      if readatom:
        sline = line.split()
        if len(sline) != 9 and len(sline) != 10 :
          raise Exception("Error in "+line+ " line is "+str(len(sline)))
        
        a = atom(int(sline[0]), sline[1], float(sline[2]), \
        float(sline[3]),float(sline[4]), float(sline[8]) )
               
        if readresname:
          a.resname = sline[7][0:3]
          a.atomname = sline[5].split(".", 1)[0]

        mol.append(a)
               
  return(mols)

###############################################################

def extractweight (file):
  weigs = []

  with open(file) as fp:
    for line in fp:
      try:
        float(line)
      except ValueError:
        raise Exception("Error "+line+ " is not a float ")
      
      weigs.append(float(line))

  return weigs

###############################################################