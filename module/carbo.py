import numpy 
import math

IDXSLCT = 5

###############################################################

def returncarbodxs(set1, set2, verbose=False, axis="x", \
    count_changed = None, progress = None):

    generalidx = 0
  
    aidx1 = 0
    aidx2 = 1
    aidx3 = 2
  
    if axis == "x":
        aidx1 = 0
        aidx2 = 1
        aidx3 = 2
    elif axis == "y":
        aidx1 = 1
        aidx2 = 0
        aidx3 = 2
    elif axis == "z":
        aidx1 = 2
        aidx2 = 0
        aidx3 = 1

    g = next(iter(set1.values()))
    xrefpoints = numpy.zeros(g[1].grid.shape[aidx1])
    carboidxs = numpy.zeros((len(set1)*len(set2), g[1].grid.shape[aidx1]))

    totcounter = 0 
    for v1 in set1:
        if progress != None:
            if progress.was_cancelled():
                return None

        for v2 in set2:
            totcounter += 1
            if count_changed != None:
                where = 100 * (totcounter / (len(set1)*len(set2)))
                count_changed.emit(where)
            
            if verbose:
                print("Compare ", v1, v2)
            
            g1 = set1[v1][1]
            g2 = set2[v2][1]
         
            try:
                g1.check_compatible(g2)
            except TypeError as te:
                raise Exception(v1 + " and " + v2 + " are not compatible ")
         
            x = y = z = 0.0
            ix = iy = iz = 0
            movcoord = 0.0
         
            for i in range(g1.grid.shape[aidx1]):
                if aidx1 == 0:
                    ix = i
                    x = g1.origin[aidx1] + i*g1.delta[aidx1]
                    movcoord = x
                elif aidx1 == 1:
                    iy = i
                    y = g1.origin[aidx1] + i*g1.delta[aidx1]
                    movcoord = y
                elif aidx1 == 2:
                    iz = i
                    z = g1.origin[aidx1] + i*g1.delta[aidx1]
                    movcoord = z
             
                num = 0.0
                denum1 = 0.0 
                denum2 = 0.0
             
                for j in range(g1.grid.shape[aidx2]):
                    if aidx2 == 0:
                        ix = j
                        x = g1.origin[aidx2] + j*g1.delta[aidx2]
                    elif aidx2 == 1:
                        iy = j
                        y = g1.origin[aidx2] + j*g1.delta[aidx2]
                    elif aidx2 == 2:
                        iz = j
                        z = g1.origin[aidx2] + j*g1.delta[aidx2]
                 
                    for k in range(g1.grid.shape[aidx3]):
                        if aidx3 == 0:
                            ix = k
                            x = g1.origin[aidx3] + k*g1.delta[aidx3]
                        elif aidx3 == 1:
                            iy = k
                            y = g1.origin[aidx3] + k*g1.delta[aidx3]
                        elif aidx3 == 2:
                            iz = k
                            z = g1.origin[aidx3] + k*g1.delta[aidx3]

                        num = num + g1.grid[ix, iy, iz]*g2.grid[ix, iy, iz]
                        denum1 = denum1 + g1.grid[ix, iy, iz]*g1.grid[ix, iy, iz]
                        denum2 = denum2 + g2.grid[ix, iy, iz]*g2.grid[ix, iy, iz]
                
                carboidx = 0.0
                if denum1 == 0.0 and denum2 != 0.0:
                    carboidx = -1.0
                elif denum2 == 0.0 and denum1 != 0.0:
                    carboidx = -1.0
                elif denum2 == 0.0 and denum1 == 0.0:
                    carboidx = 1.0
                else:
                    carboidx = num/math.sqrt(denum1 * denum2)
                
                if verbose:
                    print("%10.5f %10.5f"%(movcoord, carboidx)) 
                
                xrefpoints[i] = movcoord
                carboidxs[generalidx,i] = carboidx
  
            generalidx += 1
  
    weights = numpy.zeros(len(set1)*len(set2))
    pweights = numpy.zeros(len(set1)*len(set2))
    
    # compute weight
    generalidx = 0
    sum = 0.0
    for v1 in set1:
        for v2 in set2:
            w1 = set1[v1][0]
            w2 = set2[v2][0]
            # compute weights
            weights[generalidx] = w1 + w2
            weights[generalidx] = weights[generalidx] / 2.0
            pweights[generalidx] = w1 * w2
            sum = sum + w1*w2
            generalidx = generalidx + 1
    
    pweights =  pweights / sum
    
    return (carboidxs, xrefpoints, weights, pweights)

#################################################################################