import numpy
import scipy
import sys

sys.path.append("./common")
import gridfield

ELIMIT = -0.5
LELIMIT = -0.1

kontfilename1 = ""
kontfilename2 = ""

if (len(sys.argv)) == 3:
    kontfilename1 = sys.argv[1]
    kontfilename2 = sys.argv[2]                        
else:
                                
    print(("usage :" + sys.argv[0] + " filename1.kont filename2.kont "))
    exit(1)

energy1, energy1_coords, \
        _ , _ , _ , _ , _ , _ , _ , _ , _ , _ , _ , _  \
        = gridfield.read_kontfile(kontfilename1)

energy2, energy2_coords, \
        _ , _ , _ , _ , _ , _ , _ , _ , _ , _ , _ , _  \
        = gridfield.read_kontfile(kontfilename2)


mapidx1 = {}
coords1 = []
mapidx2 = {}
coords2 = []

lidx = 0

for ix in range(energy1_coords.shape[0]):
    for iy in range(energy1_coords.shape[1]):
        for iz in range(energy1_coords.shape[2]):

            if energy1[ix, iy, iz] <= ELIMIT:
                x, y, z, n = energy1_coords[ix, iy, iz] 
                coords1.append((x, y, z))
                mapidx1[lidx] = (ix, iy, iz)
                lidx += 1

lidx = 0
for ix in range(energy2_coords.shape[0]):
    for iy in range(energy2_coords.shape[1]):
        for iz in range(energy2_coords.shape[2]):

            if energy2[ix, iy, iz] <= ELIMIT:
                x, y, z, n = energy2_coords[ix, iy, iz] 
                coords2.append((x, y, z))
                mapidx2[lidx] = (ix, iy, iz)
                lidx += 1


maxdist = 10
collection = []
energies = []

if (len(coords1) > 0) and (len(coords2) > 0):

   cdists = scipy.spatial.distance.cdist(coords1, coords2, \
           metric='euclidean')
   
   #idxs = numpy.argwhere(cdists < 3.0)
   #for v in range(idxs.shape[0]):
   #    i = idxs[v][0]
   #    j = idxs[v][1]
   #    print (i, j , " ==> ", cdists[i, j])
   #    print (energy1_coords[mapidx1[i]], energy1[mapidx1[i]])
   #    print (energy2_coords[mapidx2[j]], energy2[mapidx2[j]])
   
  
   for id in range(maxdist):
       idxs = numpy.argwhere(cdists < float(id))
       collection.append(idxs.shape[0])  
       energies.append(0.0)
       for v in range(idxs.shape[0]):
           i = idxs[v][0]
           j = idxs[v][1]
           energies[id] += energy1[mapidx1[i]]
           energies[id] += energy2[mapidx2[j]]
else:

    for id in range(maxdist):
        energies.append(0.0)
        collection.append(0)


sys.stdout.write (kontfilename1 + " " + kontfilename2 + " , ")
for i, v in enumerate(collection):
    if i:
        sys.stdout.write(" , ")
    sys.stdout.write(str(v))
    sys.stdout.write(" , ")
    sys.stdout.write(" %10.5f "%(energies[i]))
sys.stdout.write("\n")
