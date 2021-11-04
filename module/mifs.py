import subprocess
import numpy
import os

###############################################################################

def ifextrm (filename):

    if os.path.isfile(filename):
        os.remove(filename)

    return 

###############################################################################

def compute_grid_mean_field (filename, step, delta, \
        probename, fixpdbin, gridbin, obabelbin, \
            mol2pdb=True, verbose=True, savekont=False):

  # generate grid 
  xmin = float("inf")
  ymin = float("inf")
  zmin = float("inf")
  xmax = float("-inf")
  ymax = float("-inf")
  zmax = float("-inf")

  fp = open(filename, "r")

  sum = 0.0
  weights = []
  mollist = []
  for l in fp:
    sl = l.split()
    if (len(sl) != 2):
      print("Error in ", filename)
      exit(1)
    
    weights.append(float(sl[1]))
    sum += float(sl[1])

    m = None
    
    if mol2pdb:
      m = carbo.mol2atomextractor(sl[0])
    else:
      m = carbo.pdbatomextractor(sl[0])

    mollist.extend(m)
  
  fp.close()

  weights = [ v/sum for v in weights]

  for conf in mollist:
    for a in conf:
      x, y, z = a.coords
      
      if x < xmin:
        xmin = x
      if y < ymin:
        ymin = y
      if z < zmin:
        zmin = z
  
      if x > xmax:
        xmax = x
      if y > ymax:
        ymax = y
      if z > zmax:
        zmax = z
  
  xmin = xmin - delta
  xmax = xmax + delta
  
  ymin = ymin - delta
  ymax = ymax + delta
  
  zmin = zmin - delta
  zmax = zmax + delta

  # to set custom ranges
  #xmin = -42.0
  #ymin = -28.0
  #zmin = -42.0

  #xmax = 42.0
  #ymax = 39.0
  #zmax = 42.

  if verbose:
    print("Grid will be used: ", xmin, ymin, zmin, xmax, ymax, zmax)
  
  if (len(mollist) != len(weights)):
    print("Dimension error ", len(mollist) , " vs " , \
      len(weights))
    exit(1)

  energy = numpy.empty([1,1,1], float)
  globalindex = 0
  fp = open(filename, "r")
  for conf in fp:

    sl = conf.split()
    
    ifextrm ("./"+str(globalindex)+".pdb")

    if mol2pdb:
      toexe = obabelbin + " -imol2 " + sl[0] + " -opdb -O " + "./"+str(globalindex)+".pdb"
      results  = subprocess.run(toexe, shell=True, check=True, \
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
        universal_newlines=True)
    else:
      from shutil import copyfile
      copyfile (sl[0], str(globalindex)+".pdb")

  
    toexe = fixpdbin + " --remove-all-H2O --unkn-residue-to-grid-types --kout-out="+ \
        str(globalindex)+".kout "+str(globalindex)+".pdb"
    results  = subprocess.run(toexe, shell=True, check=True, \
      stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
      universal_newlines=True)
    
    kontname = str(globalindex)+".kont"
  
    fg = open('grid.in','w')
    fg.write("LONT togrid.lont\n")
    fg.write("KONT "+kontname+"\n")
    fg.write("INPT "+str(globalindex)+".kout\n")
    fg.write("NPLA "+str(1.0/step)+"\n")
    fg.write("TOPX "+str(xmax)+"\n")
    fg.write("TOPY "+str(ymax)+"\n")
    fg.write("TOPZ "+str(zmax)+"\n")
    fg.write("BOTX "+str(xmin)+"\n")
    fg.write("BOTY "+str(ymin)+"\n")
    fg.write("BOTZ "+str(zmin)+"\n")
    fg.write(probename+"\n")
    fg.write("IEND\n")
    fg.close()
                                                                                                         
    results  = subprocess.run(gridbin + " grid.in", shell=True, check=True, \
      stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
      universal_newlines=True)

    ifextrm ("./"+str(globalindex)+".pdb")
    ifextrm ("./"+str(globalindex)+".kout")
    ifextrm ("./grid.in")
    ifextrm ("./togrid.lont")
  
    # read kont file
    lenergy = readkontfile(kontname)
  
    if verbose:
      print("nx: ", lenergy.shape[0], " ny: ", lenergy.shape[1], \
        " nz: ", lenergy.shape[2])
  
    if savekont:
      newname = sl[0].replace(".pdb", "") + "_" + str(globalindex) + ".kont"
      os.rename("./"+kontname, "./" + newname )
    else:
      ifextrm ("./"+kontname)
  
    if verbose:
      print("Dealing with: ", kontname, " w: ", weights[globalindex])
  
    if  globalindex == 0:
      nx = lenergy.shape[0]
      ny = lenergy.shape[1]
      nz = lenergy.shape[2]
      energy = numpy.arange(nx*ny*nz, dtype=float).reshape(nx, ny, nz)
      energy = numpy.zeros([nx,ny,nz], float)

    energy += weights[globalindex] * lenergy
  
    globalindex = globalindex + 1
  
  #energy = energy / float(globalindex)
  #energytofile (energy, "mean.kont", xmin, ymin, zmin)
  
  fp.close()

  """
  for i in range(energy.shape[0]):
    for j in range(energy.shape[1]):
      for k in range(energy.shape[2]):
        e = energy[i, j, k]
        if e != 0.0:
          print(e)
  """

  return energy, xmin, ymin, zmin

###############################################################################

def bufcount(filename):
    f = open(filename)                  
    lines = 0
    buf_size = 1024 * 1024
    read_f = f.read # loop optimization

    buf = read_f(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)

    return lines

###############################################################################

def remove_equal(input):
  output = []
  for x in input:
    if x not in output:
      output.append(x)
                        
  return output

###############################################################################

def write_to_cube (mol1, mol1field, fname, xnstep, ynstep, znstep,\
    step, xmin, ymin, zmin):

  opf = open(fname, "w")

  print("Writing final cube... ")

  zero = 0.0
  opf.write("El field\n")
  opf.write("OUTER LOOP: X, MIDDLE LOOP: Y, INNER LOOP: Z\n")
  opf.write("%4d %11.6f %11.6f %11.6f\n" % (len(mol1.atoms), CONVERTER*xmin, \
      CONVERTER*ymin, CONVERTER*zmin))
  opf.write("%4d %11.6f %11.6f %11.6f\n" % (xnstep, CONVERTER*step, zero, zero))
  opf.write("%4d %11.6f %11.6f %11.6f\n" % (ynstep, zero, CONVERTER*step, zero))
  opf.write("%4d %11.6f %11.6f %11.6f\n" % (znstep, zero, zero, CONVERTER*step))

  for atom in mol1:
    x = CONVERTER*atom.coords[0]
    y = CONVERTER*atom.coords[1]
    z = CONVERTER*atom.coords[2]
    c = atom.partialcharge
    anu = atom.atomicnum

    opf.write("%4d %11.6f %11.6f %11.6f %11.6f\n" % (anu, c, x, y, z))

  for ix in range(xnstep):
    for iy in range(ynstep):
      for iz in range(znstep):
        opf.write("%g "%mol1field[ix,iy,iz])
        if (iz % 6 == 5):
          opf.write("\n")
      opf.write("\n")

  opf.close()

###############################################################################

def return_metric (ix, x, iy, y, iz, z, xyzval_to_ixyz_map, \
  energy, minimaselection):

  count = countlower = 0
  e = 0.0

  xstr = "{:.3f}".format(x)
  ystr = "{:.3f}".format(y)
  zstr = "{:.3f}".format(z)
  xyzstr = xstr+'_'+ystr+'_'+zstr
  
  ijk = xyzval_to_ixyz_map[xyzstr].split("_")
  
  ix = int(ijk[0])
  iy = int(ijk[1])
  iz = int(ijk[2])
  
  if (energy[ix, iy, iz] < 0.0):
    count = 1
  if (energy[ix, iy, iz] < minimaselection):
    countlower = 1
  
  e = energy[ix, iy, iz] 

  return count, countlower, e

###############################################################################

def get_points(energy, STEPVAL, xmin, ymin, zmin, axis="x", \
  minimaselection=0.0):

  xsets = set()
  ysets = set()
  zsets = set()

  evalset = []

  xvals = []
  yvals = []
  zvals = []

  ixyz_to_xyzval_map = {}
  xyzval_to_ixyz_map = {}

  nx = energy.shape[0]
  ny = energy.shape[1]
  nz = energy.shape[2]

  for iz in range(0, nz):
    z = zmin + float(iz) * (STEPVAL)
    for ix in range(0, nx):
      x = xmin + float(ix) * (STEPVAL)
      for iy in range(0, ny):
        y = ymin + float(iy) * (STEPVAL)

        xsets.add(x)
        ysets.add(y)
        zsets.add(z)

        xvals.append(x)
        yvals.append(y)
        zvals.append(z)

        e = energy[ix, iy, iz]

        if not ( e in evalset):
          evalset.append(e)

        ixyzstr = str(ix)+'_'+str(iy)+'_'+str(iz)
        xstr = "{:.3f}".format(x)
        ystr = "{:.3f}".format(y)
        zstr = "{:.3f}".format(z)
        xyzstr = xstr+'_'+ystr+'_'+zstr
        #print ixyzstr , ' ==> ', xyzstr
        ixyz_to_xyzval_map.update({ixyzstr: xyzstr})
        xyzval_to_ixyz_map.update({xyzstr: ixyzstr})

  dx = sorted(xsets)[1] - sorted(xsets)[0]
  dy = sorted(ysets)[1] - sorted(ysets)[0]
  dz = sorted(zsets)[1] - sorted(zsets)[0]

  botx = min(list(xsets))
  boty = min(list(ysets))
  botz = min(list(zsets))

  topx = max(list(xsets))
  topy = max(list(ysets))
  topz = max(list(zsets))

  #print("  Box ")
  #print("           x: {:.3f}".format(botx), " {:.3f}".format(topx))
  #print("           y: {:.3f}".format(boty), " {:.3f}".format(topy))
  #print("           z: {:.3f}".format(botz), " {:.3f}".format(topz))

  #print("  field sizes: ", len(xsets), len(ysets), len(zsets))
  #print("           dx: {:.3f}".format(dx))
  #print("           dy: {:.3f}".format(dy))
  #print("           dz: {:.3f}".format(dz))

  if axis == "x":
    for ix in range(0, nx):
      x = xmin + float(ix) * (STEPVAL)
      count = 0
      sume = 0.0
      countlower = 0

      for iz in range(0, nz):
        z = zmin + float(iz) * (STEPVAL)
        for iy in range(0, ny):
          y = ymin + float(iy) * (STEPVAL)

          c, cl, e = return_metric (ix, x, iy, y, iz, z, \
            xyzval_to_ixyz_map, energy, minimaselection)
          
          count += c
          countlower += cl
          sume += e

      countd = 1
      if count > 0:
        countd = count

      print("X: %10.5f "%(x), " %5d %5d %10.5f %10.5f"%( \
        countlower, count, sume, sume/float(countd)))
  elif axis == "y":
    for iy in range(0, ny):
      y = ymin + float(iy) * (STEPVAL)
      count = 0
      sume = 0.0
      countlower = 0

      for iz in range(0, nz):
        z = zmin + float(iz) * (STEPVAL)
        for ix in range(0, nx):
          x = xmin + float(ix) * (STEPVAL)

          c, cl, e = return_metric (ix, x, iy, y, iz, z, \
            xyzval_to_ixyz_map, energy, minimaselection)
          
          count += c
          countlower += cl
          sume += e

      countd = 1
      if count > 0:
        countd = count

      print("Y: %10.5f "%(y), " %5d %5d %10.5f %10.5f"%( \
        countlower, count, sume, sume/float(countd)))
  elif axis == "z":
    for iz in range(0, nz):
      z = zmin + float(iz) * (STEPVAL)
      count = 0
      sume = 0.0
      countlower = 0

      for iy in range(0, ny):
        y = ymin + float(iy) * (STEPVAL)
        for ix in range(0, nx):
          x = xmin + float(ix) * (STEPVAL)

          c, cl, e = return_metric (ix, x, iy, y, iz, z, \
            xyzval_to_ixyz_map, energy, minimaselection)
          
          count += c
          countlower += cl
          sume += e

      countd = 1
      if count > 0:
        countd = count

      print("Z: %10.5f "%(z), " %5d %5d %10.5f %10.5f"%( \
        countlower, count, sume, sume/float(countd)))

###############################################################################
