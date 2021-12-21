import os
import mendeleev

###############################################################

mol2typetoatom = \
{
   "H"  : "H" ,
   "He" : "He",
   "Li" : "Li",
   "Be" : "Be",
   "B"  : "B" ,
   "C"  : "C" ,
   "C.3"   : "C",
   "C.2"   : "C",
   "C.1"   : "C",
   "C.ar"  : "C",
   "C.cat" : "C",
   "N"  : "N",
   "N.3" : "N",
   "N.2" : "N",
   "N.1" : "N",
   "N.ar" : "N",
   "N.am" : "N",
   "N.pl3" : "N",
   "N.4" : "N",
   "O"  : "O" ,
   "O.3" : "O" ,
   "O.2" : "O" ,
   "O.co2" : "O" ,
   "F"  : "F" ,
   "Ne" : "Ne",
   "Na" : "Na",
   "Mg" : "Mg",
   "Al" : "Al", 
   "Si" : "Si", 
   "P"  : "P" ,  
   "P.3" : "P",
   "S"  : "S" ,  
   "S.3"  : "S" ,
   "S.2"  : "S" ,
   "S.o"  : "S" ,
   "S.o2"  : "S" ,
   "Cl" : "Cl", 
   "Ar" : "Ar", 
   "K"  : "K" ,
   "Ca" : "Ca",
   "Sc" : "Sc",
   "Ti" : "Ti",
   "Ti.th" : "Ti", 
   "Ti.oh" : "Ti",
   "V"  : "V" ,
   "Cr" : "Cr",
   "Cr.th" : "Cr",
   "Cr.oh" : "Cr",
   "Mn" : "Mn",
   "Fe" : "Fe",
   "Co" : "Co",
   "Co.oh" : "Co",
   "Ni" : "Ni",
   "Cu" : "Cu",
   "Zn" : "Zn",
   "Ga" : "Ga",
   "Ge" : "Ge",
   "As" : "As",
   "Se" : "Se",
   "Br" : "Br",
   "Kr" : "Kr",
   "Rb" : "Rb",
   "Sr" : "Sr",
   "Y"  : "Y" ,
   "Zr" : "Zr",
   "Nb" : "Nb",
   "Mo" : "Mo",
   "Tc" : "Tc",
   "Ru" : "Ru",
   "Ru.oh" : "Ru",
   "Rh" : "Rh",
   "Pd" : "Pd",
   "Ag" : "Ag",
   "Cd" : "Cd",
   "In" : "In",
   "Sn" : "Sn",
   "Sb" : "Sb",
   "Te" : "Te",
   "I"  : "I" ,
   "Xe" : "Xe",
   "Cs" : "Cs",
   "Ba" : "Ba",
   "La" : "La",
   "Ce" : "Ce",
   "Pr" : "Pr",
   "Nd" : "Nd",
   "Pm" : "Pm",
   "Sm" : "Sm",
   "Eu" : "Eu",
   "Gd" : "Gd",
   "Tb" : "Tb",
   "Dy" : "Dy",
   "Ho" : "Ho",
   "Er" : "Er",
   "Tm" : "Tm",
   "Yb" : "Yb",
   "Lu" : "Lu",
   "Hf" : "Hf",
   "Ta" : "Ta",
   "W"  : "W" ,
   "Re" : "Re",
   "Os" : "Os",
   "Ir" : "Ir",
   "Pt" : "Pt",
   "Au" : "Au",
   "Hg" : "Hg",
   "Tl" : "Tl",
   "Pb" : "Pb",
   "Bi" : "Bi",
   "Po" : "Po",
   "At" : "At",
   "Rn" : "Rn",
   "Fr" : "Fr",
   "Ra" : "Ra",
   "Ac" : "Ac",
   "Th" : "Th",
   "Pa" : "Pa",
   "U"  : "U" ,
   "Np" : "Np",
   "Pu" : "Pu",
   "Am" : "Am",
   "Cm" : "Cm",
   "Bk" : "Bk",
   "Cf" : "Cf",
   "Es" : "Es",
   "Fm" : "Fm",
   "Md" : "Md",
   "No" : "No",
   "Lr" : "Lr",
   "Rf" : "Rf",
   "Db" : "Db",
   "Sg" : "Sg",
   "Bh" : "Bh",
   "Hs" : "Hs",
   "Mt" : "Mt"
}


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

def mol2atomextractor (file=None, readresname= False, \
  setradii=False):
  
  mols = []

  elementtoradii = {}

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

        if setradii:
          element = mol2typetoatom[sline[5]]
          if element not in elementtoradii:
            elementtoradii[element] = mendeleev.element(element).vdw_radius
          #print(element)
          a.radii = elementtoradii[element]
               
        if readresname:
          a.resname = sline[7][0:3]
          a.atomname = sline[5].split(".", 1)[0]

        mol.append(a)
               
  return(mols)

###############################################################

def extractweight (file):
  weigs = []

  sum = 0.0

  with open(file) as fp:
    for line in fp:
      try:
        float(line)
      except ValueError:
        raise Exception("Error "+line+ " is not a float ")

      val = float(line)
      
      weigs.append(val)
      sum += val

  return [x / sum for x in weigs]

###############################################################

