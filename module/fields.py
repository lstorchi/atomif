import numpy 
import scipy.spatial

import os
import glob
import numpy 
import subprocess

from gridData import Grid

import psize

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

    #if tofitw != None:
    #    tofitw.export("test2.dx")

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

def get_apbsfields (obabelbin, apbsbin, exportdx, mol2name, \
    weightsset, STEPVAL, DELTAVAL, workdir, verbose = False, progress = None, \
    checkcancel = None, startwith = 0, tot = 100 , tofitw = None, flat = False):

    if progress != None:
        progress.emit(startwith)

    if verbose:
        print("Producing PQR files")

    basename = os.path.splitext(mol2name)[0]
    basename  = basename.split("/")[-1]

    listafnames = glob.glob(workdir+"/"+"*.pqr")
    for fname in listafnames:
        os.remove(fname)

    result = subprocess.run(obabelbin + " -imol2 "+  mol2name + \
        " -opqr -O " + workdir + "/" + basename+".pqr -m ", shell=True, check=True, \
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,  \
                universal_newlines=True)

    numoffiles = 0
    for line in result.stderr.split("\n"):
        if line.find("files output. The first is") > 0:
            numoffiles = int(line.split()[0])
                
    if checkcancel != None:
        if checkcancel.was_cancelled():
            return None, None 
    
    listafnames = glob.glob(workdir+"/"+"*.pqr")
    if len(listafnames) != numoffiles:
        return None, None 

    allfields = []

    for idx, fname in enumerate(listafnames):
        if verbose:
            print("Considering ", fname)

        if checkcancel != None:
            if checkcancel.was_cancelled():
                return None, None 
        
        if progress != None:
            where = int(startwith + ((tot - 0.05*tot) * ((idx+1)/len(listafnames))))
            progress.emit(where)

        psizeist = psize.Psize()

        psizeist.runPsize(fname)

        lines = psizeist.printResults().split("\n")

        dime = None
        cglen = None
        fglen = None
        gcent = None
        for line in lines:
            if line.find("Num. fine grid pts.") >= 0:
                sline = line.split("=")[1].replace("A", "")
                dime = [numpy.int(x) for x in sline.split("x")]
            if line.find("Coarse grid dims") >= 0:
                sline = line.split("=")[1].replace("A", "")
                cglen = [numpy.float(x) for x in sline.split("x")]
            if line.find("Fine grid dims") >= 0:
                sline = line.split("=")[1].replace("A", "")
                fglen = [numpy.float(x) for x in sline.split("x")]
            if line.find("Center") >= 0:
                sline = line.split("=")[1].replace("A", "")
                gcent = [numpy.float(x) for x in sline.split("x")]
        
        if verbose:
            print(dime, cglen, fglen, gcent)

        fp = open(workdir + "/" + basename + ".in","w") 
    
        fp.write("read\n")
        fp.write("   mol pqr "+ fname +"\n")
        fp.write("end\n")
        fp.write("elec\n")
        fp.write("   mg-auto\n")
        fp.write("   dime   %5d %5d %5d\n"%(dime[0], dime[1], dime[2]))
        fp.write("   cglen  %12.6f %12.6f %12.6f\n"%(cglen[0], cglen[1], cglen[2]))
        fp.write("   fglen  %12.6f %12.6f %12.6f\n"%(fglen[0], fglen[1], fglen[2]))
        fp.write("   cgcent %12.6f %12.6f %12.6f\n"%(gcent[0], gcent[1], gcent[2]))
        fp.write("   fgcent %12.6f %12.6f %12.6f\n"%(gcent[0], gcent[1], gcent[2]))
        fp.write("   lpbe\n")
        fp.write("   bcfl sdh\n")
        if not flat:
            fp.write("   ion charge  1 conc 0.150000 radius 2.000000\n") 
            fp.write("   ion charge -1 conc 0.150000 radius 1.800000\n")
            fp.write("   ion charge  2 conc 0.000000 radius 2.000000\n")
            fp.write("   ion charge -2 conc 0.000000 radius 2.000000\n")
            fp.write("   pdie 2.000000\n") 
            fp.write("   sdie 78.000000\n")
        else:
            fp.write("   ion charge  1 conc 0.000000 radius 2.000000\n") 
            fp.write("   ion charge -1 conc 0.000000 radius 1.800000\n")
            fp.write("   ion charge  2 conc 0.000000 radius 2.000000\n")
            fp.write("   ion charge -2 conc 0.000000 radius 2.000000\n")
            fp.write("   pdie 1.000000\n")
            fp.write("   sdie 1.000000\n")
        fp.write("   chgm spl2\n")
        fp.write("   mol 1\n")
        fp.write("   srfm smol\n")
        fp.write("   srad 1.400000\n")
        fp.write("   swin 0.3\n")
        if not flat:
            fp.write("   temp 310.000000\n") 
        else:
            fp.write("   temp  0.100000\n") 
        fp.write("   sdens 10.000000\n")
        fp.write("   calcenergy no\n")
        fp.write("   calcforce no\n") 
        dxname = ""
        if not flat:
            dxname = workdir + "/" + basename
        else:
            dxname = workdir + "/" +basename+ "_flat"

        fp.write("   write pot dx " + dxname + "\n")
        fp.write("end\n")
        fp.write("quit\n")
        fp.close()
    
        if verbose:
            print("Running APBS")

        result = subprocess.run(apbsbin + " " + workdir + "/" + basename + ".in" , \
                 shell=True, check=True, \
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
                universal_newlines=True)

        g = Grid(dxname + ".dx")
        allfields.append(g)

        os.remove(dxname + ".dx")
        os.remove(workdir + "/" + basename + ".in")
        os.remove(fname)
        os.remove("io.mc")

        if checkcancel != None:
            if checkcancel.was_cancelled():
                return None, None 

    if verbose:
        print("Start interpolate ")
    
    deltamax = float("-inf")
    x1 = []
    x2 = []
    y1 = []
    y2 = []
    z1 = []
    z2 = []

    for g in allfields:
        m = max(g.delta)
        if m > deltamax:
            deltamax = m

        x1.append(g.origin[0])
        x2.append(g.origin[0] + (g.grid.shape[0]-1)*g.delta[0])

        y1.append(g.origin[1])
        y2.append(g.origin[1] + (g.grid.shape[1]-1)*g.delta[2])

        z1.append(g.origin[2])
        z2.append(g.origin[2] + (g.grid.shape[2]-1)*g.delta[2])

    xmin = min(x1)
    ymin = min(y1)
    zmin = min(z1)
    xmax = max(x2)
    ymax = max(y2)
    zmax = max(z2)

    deltamax = STEPVAL

    if verbose:
        print("New Grid %10.3f %10.3f %10.3f %10.3f %10.3f %10.3f %10.3f"%(\
            deltamax, xmin, xmax, ymin, ymax, zmin, zmax))
    
    XX, YY, ZZ = numpy.mgrid[xmin:xmax:deltamax, \
        ymin:ymax:deltamax, zmin:zmax:deltamax]

    if checkcancel != None:
        if checkcancel.was_cancelled():
            return None, None 

    if verbose:
        print("Start to intepolate")

    shapes = None
    norig = None

    for idx, g in enumerate(allfields):
        norig = [XX[0][0][0], YY[0][0][0], ZZ[0][0][0]]
        nf = g.interpolated(XX, YY, ZZ)
        ng = Grid(nf, origin=norig , \
           delta=[deltamax, deltamax, deltamax])
        allfields[idx] = ng
        shapes = nf.shape

    if checkcancel != None:
        if checkcancel.was_cancelled():
            return None, None 

    mep = numpy.zeros(shapes)

    finalset = {}

    for idx, g in enumerate(allfields):
        mep += g.grid * weightsset[idx]

        keyname = basename + "_" + str(idx+1)

        newname =  workdir + "/" + basename + "_" + \
            str(idx+1) + ".dx"
        if flat:
            newname =  workdir + "/" + basename + "_" + \
                tr(idx+1) + "_flat.dx"
 
        if exportdx:
            g.export(newname)

        if tofitw != None:
            g_on = g.resample(tofitw)

            allfields[idx] = g_on

            if exportdx:
                g_on.export(newname)
        
        finalset[keyname] = (weightsset[idx], g)
        

    if checkcancel != None:
        if checkcancel.was_cancelled():
            return None, None 

    mep = mep
    gmean = Grid(mep, origin=norig, \
      delta=[deltamax, deltamax, deltamax])
    
    if exportdx:
        name = workdir + "/" + basename + "_mean.dx"
        if flat:
            name = workdir + "/" + basename + "_flat_mean.dx"
        gmean.export(name)

        if tofitw != None:
            g_on = gmean.resample(tofitw)
            g_on.export(name)
 
    where = startwith + tot
    progress.emit(where)

    return gmean, finalset