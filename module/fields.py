import numpy 
import scipy.spatial

import sys 
import numpy 

from gridData import Grid

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
     ddielectric=False, progress = None, checkcancel = None, \
       startwith = 0, tot = 100 ): 

    # read data of first molecule
    if progress != None:
        progress.emit(startwith)
    
    mol = mols[0]
    atomnum = len(mol)
    molcoord = numpy.zeros((atomnum, 3))
    molcharges = numpy.zeros((atomnum, 1))
    for idx, atom in enumerate(mol):
        molcoord[idx,0] = atom.coords[0]
        molcoord[idx,1] = atom.coords[1]
        molcoord[idx,2] = atom.coords[2]
        molcharges[idx,0] = atom.partialcharge
    
    if checkcancel != None:
        if checkcancel.was_cancelled():
            return None
    
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
    
        if verbose:
            print("Computing mol ", molidx+1)
      
        if progress != None:
            where = int(startwith + (tot * ((molidx+1)/len(mols))))
            progress.emit(where)
          
        if checkcancel != None:
            if checkcancel.was_cancelled():
                return None
      
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

def exporttodx (basename, cfields, weights, stepvalue, \
    ddielectric, writefiles, tofitw):

    mep = numpy.zeros(cfields[0][1].shape)
    coords = cfields[0][0]
    for i, field in enumerate(cfields):
        ep = field[1]
        mep += ep * weights[i]

    mep = mep/float(len(cfields))
    gmean = Grid(mep, origin=coords[0], \
      delta=[stepvalue, stepvalue, stepvalue])

    if writefiles:
        name = basename + "_coulomb_mean.dx"
        if ddielectric:
            name = basename + "_coulomb_ddieletric_mean.dx"
        gmean.export(name)

    allfields = {}

    if tofitw != None:
        tofitw.export("test2.dx")

    for i, field in enumerate(cfields):
        coords = field[0]
        ep = field[1]
        g = Grid(numpy.asarray(ep), origin=coords[0], \
          delta=[stepvalue, stepvalue, stepvalue])
        
        name = basename + "_%d_coulomb.dx"%(i+1)
        if ddielectric:
            name = basename + "_%d_coulomb_ddieletric.dx"%(i+1)
        #print (name + " %8.3f"%(weights[i]), file=sys.stderr)
     
        if tofitw != None:
            g_on = g.resample(tofitw)
            allfields[name] =(weights[i], g_on)
            if writefiles:
                g_on.export(name)
        else:
            allfields[name] = (weights[i], g)
            if writefiles:
                g.export(name)

    if len(cfields) == 0:
      return None, None    

    return gmean, allfields

###############################################################