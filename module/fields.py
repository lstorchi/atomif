import numpy 
import scipy.spatial

############################################################### 

def __get_seps__ (refpoint, molcoord, molcharges, coulombconst, \
  ddielectric):
            
  #print refpoint[0,0], refpoint[0,1], refpoint[0,2], 1.0
  dist = scipy.spatial.distance.cdist(molcoord,refpoint)

  sum = 0.0

  #print("TODO")
  if (dist.min() > 1.0):
    if ddielectric:
      # simplest distance-dependent dielectric constant has been implemented in lammps
      ep = coulombconst * (molcharges/(dist**2))
    else:
      ep = coulombconst * (molcharges/dist)

    sum = numpy.sum(ep) 

  return sum

###############################################################

def get_cfields (mols, STEPVAL, DELTAVAL, coulombconst, verbose = False, \
     ddielectric=False, progress = None ): 

  # read data of first molecule
  if progress != None:
    progress.setValue(1)

  mol = mols[0]
  atomnum = len(mol)
  molcoord = numpy.zeros((atomnum, 3))
  molcharges = numpy.zeros((atomnum, 1))
  for idx, atom in enumerate(mol):
    molcoord[idx,0] = atom.coords[0]
    molcoord[idx,1] = atom.coords[1]
    molcoord[idx,2] = atom.coords[2]
    molcharges[idx,0] = atom.partialcharge
  
  # generate grid 
  xmin = min(molcoord[:,0])
  ymin = min(molcoord[:,1])
  zmin = min(molcoord[:,2])
  xmax = max(molcoord[:,0])
  ymax = max(molcoord[:,1])
  zmax = max(molcoord[:,2])
  xmin = xmin - DELTAVAL
  ymin = ymin - DELTAVAL
  zmin = zmin - DELTAVAL
  xmax = xmax + DELTAVAL
  ymax = ymax + DELTAVAL
  zmax = zmax + DELTAVAL
  
  if verbose:
    print("Grid will be used: %10.5f %10.5f %10.5f %10.5f %10.5f %10.5f"%( \
      xmin, ymin, zmin, xmax, ymax, zmax))
  
  xnstep = int( ((xmax - xmin) / STEPVAL)+0.5)
  ynstep = int( ((ymax - ymin) / STEPVAL)+0.5)
  znstep = int( ((zmax - zmin) / STEPVAL)+0.5)
  
  molsfield = []
  
  if verbose:
    print("")
    print("Start main computation")
    print("")

  for molidx in range(len(mols)):

    if progress != None:
        progress.setValue((100*((molidx+1)/len(mols)))-1)
        if (progress.wasCanceled()):
            return None 

    if verbose:
      print("Computing mol ", molidx+1)
    # read coord first molecule
    atomnum = len(mols[molidx])
    molcoord = numpy.zeros((atomnum, 3))
    molcharges = numpy.zeros((atomnum, 1))
    totcharge = 0.0
    for idx, atom in enumerate(mols[molidx]):
      molcoord[idx,0] = atom.coords[0]
      molcoord[idx,1] = atom.coords[1]
      molcoord[idx,2] = atom.coords[2]
      molcharges[idx,0] = atom.partialcharge
      totcharge += atom.partialcharge
    if verbose:
      print("   totalcharge: ", totcharge)
    
    molfield = numpy.zeros((xnstep, ynstep, znstep))
    coords = []
    refpoint = numpy.zeros((1, 3))
    for ix in range(0,xnstep):
      refpoint[0,0] = xmin + ix*STEPVAL
      for iy in range(0,ynstep):
        refpoint[0,1] = ymin + iy*STEPVAL
        for iz in range(0,znstep):
          refpoint[0,2] = zmin + iz*STEPVAL
          molfield[ix,iy,iz] = __get_seps__ (refpoint, molcoord, \
            molcharges, coulombconst, ddielectric)
          coords.append((refpoint[0][0], refpoint[0][1], refpoint[0][2])) 

    molsfield.append((coords, molfield))

  return molsfield

###############################################################
