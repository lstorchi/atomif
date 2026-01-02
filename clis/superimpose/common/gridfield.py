import scipy.spatial
import subprocess
import openbabel
import numpy 
import math
import re
import os
import os.path

###############################################################################

class energydecomposion:

    def __init__ (self, xin = 0.0, yin = 0.0, zin = 0.0, ein = 0.0):

        self.x = xin
        self.y = yin
        self.z = zin
        
        self.atomslist = []

    def __repr__(self):
        return self.__str__() + "\n"

    def __str__(self):
        s = "%10.3f %10.3f %10.3f has %d atoms"%(self.x, \
                self.y, self.z, len(self.atomslist))
        return s


###############################################################################

def read_splitted_contrib_csv(filename):

    fp = open(filename)

    energylist = {}
    
    linecounter = 0
    for l in fp:
        linecounter += 1
        p = re.compile(r'\s+')
        line = p.sub(' ', l)
        line = line.lstrip()
        line = line.rstrip()

        sline = line.split()

        if len(sline) >= 4:

            x = float(sline[0])
            y = float(sline[1])
            z = float(sline[2])

            # memento this is not necessarily the total energy 
            totenergy = float(sline[-1])

            newe = energydecomposion(x, y, z)

            tot = 0.0
            atomnum = 0
            #print x, y, z, totenergy
            #print linecounter, " ", line
            for i in range(3, len(sline)-1, 7):
                atomnum += 1
                anum = int(sline[i])
                aenergy = float(sline[i+1])
                aname = sline[i+2]
                resname = sline[i+3]
                ax = float(sline[i+4])
                ay = float(sline[i+5])
                az = float(sline[i+6])

                if totenergy != 0.0:
                    perc = 100.0*(aenergy/totenergy)
                    newe.atomslist.append((anum, aname, resname, \
                            ax, ay, az, perc))
                    tot += perc
                else:
                    newe.atomslist.append((anum, aname, resname, \
                            ax, ay, az, 100.0))
                    tot += 100.0

            #if tot != 0.0 and math.fabs(100.0 - tot) > 2.0:
            #    print "Error in total percentage ", math.fabs(100.0 - tot)
            #    print "    with ", atomnum
            #    exit(1)

            index = "%.3f_%.3f_%.3f"%(x, y, z)
            energylist[index] = newe

    fp.close()

    return energylist

###############################################################################

def ifextrm (filename):

    if os.path.isfile(filename):
        os.remove(filename)

    return 

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

    f.close()

    return lines

###############################################################################

def read_kontfile (kontname):

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

    if "HEADER" in l:
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

        #print(n, x, y, z )
    
        xsets.add(float(x))
        ysets.add(float(y))
        zsets.add(float(z))
 
  fk.close()

  if (len(xsets) == 0 ) or (len(ysets) == 0 ) or (len(zsets) == 0 ):
    print("ERROR sets empty")
    return None, None, \
           None, None, None, None, None, None, \
           None, None, None, None, None, None


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
