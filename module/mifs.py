import subprocess
import numpy
import glob
import os
import re

###############################################################################

def ifextrm (filename):

    if os.path.isfile(filename):
        os.remove(filename)

    return 

###############################################################################

def energytofile (energy, name, botx, boty, botz, STEPVAL, verbose):

  ifextrm(name)

  opf = open(name, "w")

  nx = energy.shape[0]
  ny = energy.shape[1]
  nz = energy.shape[2]

  if verbose:
    print("Writing final kont... ")
    print("nx: ", nx, " ny: ", ny, " nz: ", nz)

  counter = 1
  for i in range(0, nz):
    z = botz + i * (1.0/STEPVAL)
    for j in range(0, nx):
      x = botx + j * (1.0/STEPVAL)
      for k in range(0, ny):
        y = boty + k * (1.0/STEPVAL)
        opf.write(str(counter) + " " + str(x) +  " " + \
            str(y) + " " + str(z) + "\n")
        counter = counter + 1
  
  opf.write("Probe: XXX\n")
  
  for i in range(0, nz):
    for j in range(0, nx):
      for k in range(0, ny):
        opf.write(str(energy[j, k, i]) + "\n")

  opf.close()

###############################################################################

def readkontfile (kontname):

  lineamnt = bufcount(kontname)
  
  dim = (lineamnt - 1)/2

  energy = numpy.empty([1,1,1], float)

  if ((dim * 2) + 1) != lineamnt :
    print("Maybe invalid kont file")
    exit(1)

  fk = open(kontname)

  xsets = set()
  ysets = set()
  zsets = set()
  switchtofieldm = False

  nx = ny = nz = 0
  ix = iy = iz = 0
  for l in fk:

    if (l[:5] == "Probe"):
      switchtofieldm = True 
      nx = len(xsets)
      ny = len(ysets)
      nz = len(zsets)
      energy = numpy.arange(nx*ny*nz, dtype=float).reshape(nx, ny, nz)

    else:
      if switchtofieldm:
        p = re.compile(r'\s+')
        line = p.sub(' ', l)
        line = line.lstrip()
        line = line.rstrip()

        e = float(line)
        energy[ix, iy, iz] = e
        #if e != 0.0:
        #  print (ix, iy, iz, e)

        # seguo la logica con cui sono scritti i kont ascii senza fare deduzioni
        # ovviamente va migliorato
        iy = iy + 1
        if (iy == ny):
          iy = 0
          ix = ix + 1
        
        if (ix == nx):
          ix = 0
          iy = 0
          iz = iz + 1

        if (iz == nz):
          ix = 0
          iy = 0
          iz = 0

      else:
        p = re.compile(r'\s+')
        line = p.sub(' ', l)
        line = line.lstrip()
        line = line.rstrip()
        n, x, y, z = line.split(" ")

        xsets.add(float(x))
        ysets.add(float(y))
        zsets.add(float(z))

  fk.close()

  return energy

###############################################################################

def compute_grid_mean_field (mollist, weights, filename, step, delta, \
        probename, fixpdbin, gridbin, obabelbin, workdirin, \
        progress = None, checkcancel = None, startwith = 0, tot = 100, \
        verbose=True, savekont=False):

  workdir = workdirin + "/"

  if progress != None:
    progress.emit(startwith)

  # generate grid 
  xmin = float("inf")
  ymin = float("inf")
  zmin = float("inf")
  xmax = float("-inf")
  ymax = float("-inf")
  zmax = float("-inf")

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

  if verbose:
    print("Grid will be used: ", xmin, ymin, zmin, xmax, ymax, zmax)
  
  if (len(mollist) != len(weights)):
    print("Dimension error ", len(mollist) , " vs " , \
      len(weights))
    exit(1)

  energy = numpy.empty([1,1,1], float)
  globalindex = 0

  basename = os.path.splitext(filename)[0].split("/")[-1]
  namelist = glob.glob(workdir + "/"+basename+"*.pdb")

  for name in namelist :
    ifextrm (name)

  toexe = obabelbin + " -imol2 " + filename + " -opdb -O " + workdir + "/"+basename+".pdb -m"
  results  = subprocess.run(toexe, shell=True, check=True, \
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
    universal_newlines=True)

  namelist = glob.glob(workdir + "/"+basename+"*.pdb")
  
  globalindex = 0
  for i, name in enumerate(namelist):

    if checkcancel != None:
      if checkcancel.was_cancelled():
          return None, xmin, ymin, zmin

    if verbose:
      print("Running : ", name)

    basename = os.path.splitext(name)[0].split("/")[-1]
  
    toexe = fixpdbin + " --remove-all-H2O --unkn-residue-to-grid-types --kout-out="+ \
        workdir + "/" + basename +".kout "+ name
    results  = subprocess.run(toexe, shell=True, check=True, \
      stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
      universal_newlines=True)
    
    kontname = basename +".kont"
  
    fg = open(workdir + 'grid.in','w')
    fg.write("LONT "+workdir+"togrid.lont\n")
    fg.write("KONT "+workdir+kontname+"\n")
    fg.write("INPT "+workdir+basename+".kout\n")
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
                                                                                                         
    results  = subprocess.run(gridbin + " " + workdir + "grid.in", \
      shell=True, check=True, \
      stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
      universal_newlines=True)

    ifextrm (workdir+basename+".pdb")
    ifextrm (workdir+basename+".kout")
    ifextrm (workdir + "grid.in")
    ifextrm (workdir + "togrid.lont")
  
    # read kont file
    lenergy = readkontfile(workdir + kontname)
  
    if verbose:
      print("nx: ", lenergy.shape[0], " ny: ", lenergy.shape[1], \
        " nz: ", lenergy.shape[2])
  
    if not savekont:
      ifextrm (workdir + kontname)
  
    if verbose:
      print("Dealing with: ", kontname, " w: ", weights[i])
  
    if  i == 0:
      nx = lenergy.shape[0]
      ny = lenergy.shape[1]
      nz = lenergy.shape[2]
      energy = numpy.arange(nx*ny*nz, dtype=float).reshape(nx, ny, nz)
      energy = numpy.zeros([nx,ny,nz], float)

    globalindex += 1
    energy += weights[i] * lenergy

    if checkcancel != None:
      if checkcancel.was_cancelled():
          return None, xmin, ymin, zmin

    if progress != None:
      where = int(startwith + (tot * ((i+1)/len(namelist))))
      progress.emit(where)
  
  energy = energy / float(globalindex)
  if savekont:
    basename = os.path.splitext(filename)[0].split("/")[-1]
    energytofile (energy, workdir + basename + "_mean.kont", xmin, ymin, zmin, \
      step, verbose)
  
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
    step, xmin, ymin, zmin, CONVERTER):

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
  minimaselection=0.0, verbose=False):

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

  results = []

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

      results.append((x, countlower, count, sume, sume/float(countd)))

      if verbose:
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

      results.append((y, countlower, count, sume, sume/float(countd)))

      if verbose:
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

      results.append((z, countlower, count, sume, sume/float(countd)))

      if verbose:
        print("Z: %10.5f "%(z), " %5d %5d %10.5f %10.5f"%( \
          countlower, count, sume, sume/float(countd)))

  return results

###############################################################################

def read_kontfile_and_coords (kontname):

  lineamnt = bufcount(kontname)
 
  dim = (lineamnt - 1)/2
 
  if ((dim * 2) + 1) != lineamnt :
    print("Maybe invalid kont file")
    exit(1)
 
  fk = open(kontname)
 
  xsets = set()
  ysets = set()
  zsets = set()
  switchtofieldm = False

  energy = numpy.empty([1,1,1], float)
 
  nx = ny = nz = 0
  ix = iy = iz = 0
  for l in fk:

    if "Probe:" in l:
      switchtofieldm = True 
      nx = len(xsets)
      ny = len(ysets)
      nz = len(zsets)
      energy = numpy.arange(nx*ny*nz, dtype=float).reshape(nx, ny, nz)
    
    else:
      if switchtofieldm:
        p = re.compile(r'\s+')
        line = p.sub(' ', l)
        line = line.lstrip()
        line = line.rstrip()
    
        e = float(line)
        energy[ix, iy, iz] = e
        #print ix, iy, iz, e
    
        # seguo la logica con cui sono scritti i kont ascii senza fare deduzioni
        # ovviamente va migliorato
        iy = iy + 1
        if (iy == ny):
          iy = 0
          ix = ix + 1
        
        if (ix == nx):
          ix = 0
          iy = 0
          iz = iz + 1
    
        if (iz == nz):
          ix = 0
          iy = 0
          iz = 0
    
      else:
        p = re.compile(r'\s+')
        line = p.sub(' ', l)
        line = line.lstrip()
        line = line.rstrip()
        n = ""
        x = ""
        y = ""
        z = ""

        if len(line.split(" ")) < 4:
            n = l[:7]
            x = l[8:16]
            y = l[17:24]
            z = l[25:]
        else:
            n, x, y, z = line.split(" ")
    
        xsets.add(float(x))
        ysets.add(float(y))
        zsets.add(float(z))
 
  fk.close()

  dx = sorted(xsets)[1] - sorted(xsets)[0]
  dy = sorted(ysets)[1] - sorted(ysets)[0]
  dz = sorted(zsets)[1] - sorted(zsets)[0]
 
  botx = min(list(xsets))
  boty = min(list(ysets))
  botz = min(list(zsets))
 
  topx = max(list(xsets))
  topy = max(list(ysets))
  topz = max(list(zsets))

  fk = open(kontname)
 
  coords = numpy.empty([nx,ny,nz], dtype=object)
 
  for iz in range(nz):
      for ix in range(nx):
          for iy in range(ny):
              l = fk.readline()
              p = re.compile(r'\s+')
              line = p.sub(' ', l)
              line = line.lstrip()
              line = line.rstrip()

              n = ""
              x = ""
              y = ""
              z = ""

              if len(line.split(" ")) < 4:
                  n = l[:7]
                  x = l[8:16]
                  y = l[17:24]
                  z = l[25:]
              else:
                  n, x, y, z = line.split(" ")

              coords[ix, iy, iz] = (float(x), float(y), float(z), int(n))

  fk.close()
 
 
  return energy, coords, \
          botx, boty, botz, topx, topy, topz, dx, dy, dz, nx, ny, nz

###############################################################################

def get_mifatomsintesect (filescoord, energy, energy_coords, \
  progress = None, checkcancel = None, startwith = 0, tot = 100,  \
    VDW = 1.0, ELIMIT=0.0):
  
  if checkcancel != None:
    if checkcancel.was_cancelled():
      return None

  results = []

  for i, mol in enumerate(filescoord):

    if checkcancel != None:
      if checkcancel.was_cancelled():
        return None

    coords = []
    radii = []
    for atom in mol:
      coords.append(atom.coords)
      radii.append(atom.radii)

    counter = 0
    counter_multiple = 0
    peratom_counter = []
    peratom_counter_multiple = []
    
    for ai in range(len(coords)):
        peratom_counter.append(0)
        peratom_counter_multiple.append(0)
    
    for iy in range(energy_coords.shape[1]):
        for ix in range(energy_coords.shape[0]):
            for iz in range(energy_coords.shape[2]):
                x, y, z, n = energy_coords[ix, iy, iz] 
                e = energy[ix, iy, iz]
                
                partialconter = 0
                distfromatom = []
                isnearatom = []
                for ai in range(len(coords)):
                    ax, ay, az = coords[ai]
    
                    dist = (ax-x)**2 + (ay-y)**2 + (az-z)**2 
                    distfromatom.append(dist)
                    isnearatom.append(0)
    
                    if dist < VDW*radii[ai] and e <= ELIMIT:
                        partialconter += 1
                        isnearatom[ai] = 1
                        peratom_counter_multiple[ai] += 1
    
                counter_multiple += partialconter
    
                if partialconter > 1:
                    #print partialconter
                    partialconter = 1
    
                    mindistai = -1
                    mindist = 0.0
                    for ai in range(len(coords)):
                        if isnearatom[ai] != 0:
                            if mindistai < 0:
                                mindist = distfromatom[ai]
                                mindistai = ai
                            else:
                                if distfromatom[ai] < mindist:
                                    mindist = distfromatom[ai]
                                    mindistai = ai
    
                    if mindistai >= 0:
                        peratom_counter[mindistai] += 1
                    else:
                        print("Error")
                        exit(1)
    
                elif partialconter  == 1:
                    for ai in range(len(coords)):
                        if isnearatom[ai] != 0:
                            peratom_counter[ai] += 1
    
                counter += partialconter

    dictres = {"counter" : counter, \
      "counter_multiple" : counter_multiple, \
      "peratom_counter" : peratom_counter, \
      "peratom_counter_multiple" : peratom_counter_multiple}

    results.append(dictres)

    if progress != None:
      where = int(startwith + (tot * ((i+1)/len(filescoord))))
      progress.emit(where)

    if checkcancel != None:
      if checkcancel.was_cancelled():
        return None

  return results

###############################################################################