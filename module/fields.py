import numpy 
import scipy.spatial

import os
import sys 
import numpy 
import subprocess

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

def get_apbsfields (mol2name, STEPVAL, DELTAVAL, workdir, \
    verbose = False, progress = None, checkcancel = None, \
        startwith = 0, tot = 100 ):

    if progress != None:
        progress.emit(startwith)

    if verbose:
        print("Producing PQR files")

    basename = os.path.splitext(mol2name)[0]
    basename  = basename.split("/")[-1]

    result = subprocess.run("obabel -imol2 "+  mol2name + \
        " -opqr -O " + workdir + "/" + basename+".pqr -m ", shell=True, check=True, \
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,  \
                universal_newlines=True)
                
    if checkcancel != None:
        if checkcancel.was_cancelled():
            return None
    
    """
    for idx, fname in enumerate(listafp):

        basename = os.path.splitext(fname.split()[0])[0]
    
        mols = carbo.mol2atomextractor(args.file, True)
        
        print("Producing PQR files")
        result = subprocess.run("obabel -imol2 "+  basename+ ".mol2 " + \
                "-opqr -O " + basename+".pqr", shell=True, check=True, \
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,  \
                        universal_newlines=True)
    
        idx = 1
        for pqrname in glob.glob(basename+"*.pqr"):
            print("Considering ", pqrname)
            result = subprocess.run("python2 "+ psizepath + " " \
                    + pqrname, shell=True, check=True, \
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
                    universal_newlines=True)
            #Dimensions = 52.547 x 39.477 x 45.994 A
            #Center = 4.364 x 0.383 x 3.017 A
            #Lower corner = -21.910 x -19.356 x -19.980 A
            #Upper corner = 30.637 x 20.121 x 26.014 A
            #Coarse grid dims = 89.330 x 67.111 x 78.190 A
            #Fine grid dims = 72.547 x 59.477 x 65.994 A
            #Num. fine grid pts. = 161 x 129 x 129
            lines = result.stdout.split("\n")
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
    
            # generate input for APBS
            fp = open(basename + ".in","w") 
    
            fp.write("read\n")
            fp.write("   mol pqr "+ pqrname +"\n")
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
            if not args.flat:
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
            if not args.flat:
                fp.write("   temp 310.000000\n") 
            else:
                fp.write("   temp  0.100000\n") 
            fp.write("   sdens 10.000000\n")
            fp.write("   calcenergy no\n")
            fp.write("   calcforce no\n") 
            if not args.flat:
                fp.write("   write pot dx "+basename+"\n")  
            else:
                fp.write("   write pot dx "+basename+"_flat\n")  
            fp.write("end\n")
            fp.write("quit\n")
            fp.close()
    
            print("Running APBS")
            result = subprocess.run(apbspath + " " + basename + ".in" , \
                     shell=True, check=True, \
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
                    universal_newlines=True)
    
            os.remove(basename + ".in")
            os.remove(pqrname)
            os.remove("io.mc")
            idx += 1
    
    listafp.close()

    num = idx - 1
    print("Start interpolate ")
    deltamax = float("-inf")
    x1 = []
    x2 = []
    y1 = []
    y2 = []
    z1 = []
    z2 = []

    listafp = open(args.file)
    for fname in listafp:
        basename = os.path.splitext(fname.split()[0])[0]
        dxname = basename+".dx"
        g = Grid(dxname)
        m = max(g.delta)
        if m > deltamax:
            deltamax = m

        x1.append(g.origin[0])
        x2.append(g.origin[0] + (g.grid.shape[0]-1)*g.delta[0])

        y1.append(g.origin[1])
        y2.append(g.origin[1] + (g.grid.shape[1]-1)*g.delta[2])

        z1.append(g.origin[2])
        z2.append(g.origin[2] + (g.grid.shape[2]-1)*g.delta[2])

    listafp.close()

    xmin = min(x1)
    ymin = min(y1)
    zmin = min(z1)
    xmax = max(x2)
    ymax = max(y2)
    zmax = max(z2)

    if args.stepval > 0.0:
        deltamax = args.stepval

    print("New Grid %10.3f %10.3f %10.3f %10.3f %10.3f %10.3f %10.3f"%(\
        deltamax, xmin, xmax, ymin, ymax, zmin, zmax))
    XX, YY, ZZ = numpy.mgrid[xmin:xmax:deltamax, \
        ymin:ymax:deltamax, zmin:zmax:deltamax]

    print("Start to intepolate")

    alldata = {}
    allweig = {}
    shapes = None
    norig = None

    sumwei = 0.0
    listafp = open(args.file)
    for fname in listafp:
        basename = os.path.splitext(fname.split()[0])[0]
        dxname = basename+".dx"
        print("Considering ", dxname)
        g = Grid(dxname)
        norig = [XX[0][0][0], YY[0][0][0], ZZ[0][0][0]]
        #print(g.origin, norig)
        nf = g.interpolated(XX, YY, ZZ)
        ng = Grid(nf, origin=norig , \
           delta=[deltamax, deltamax, deltamax])
        alldata[dxname] = ng
        allweig[dxname] = float(fname.split()[1])
        sumwei += float(fname.split()[1])
        shapes = nf.shape

    listafp.close()

    mep = numpy.zeros(shapes)

    idx =  1
    for name in alldata:
        mep += alldata[name].grid * allweig[name]
        newname = name 
        if args.flat:
            newname = name[:-3]+"_flat.dx"
        print(newname + " %8.3f"%(allweig[name]), file=sys.stderr )
        alldata[name].export(newname)

        if tofitw != None:
          g_on = alldata[name].resample(tofitw)
          os.remove(newname)
          g_on.export(newname)

        idx += 1

    basename = os.path.splitext(args.file.split()[0])[0]

    mep = mep/sumwei
    g = Grid(mep, origin=norig, \
      delta=[deltamax, deltamax, deltamax])
    name = basename + "_mean.dx"
    if args.flat:
        name = basename + "_flat_mean.dx"
    g.export(name)

    if tofitw != None:
        g_on = g.resample(tofitw)
        os.remove(name)
        g_on.export(name)

    # python2 psize.py  test.pqr to get cage for APBS
    """