import openbabel
import pybel
import math
import sys

sys.path.append("./common")
import gridfield

ELIMIT = -1.0
VDW = 1.0

kontfilename = ""
pdbfilename = ""
csvfilename = ""
fieldpdbname = ""

if (len(sys.argv)) == 5:
    kontfilename = sys.argv[1]
    pdbfilename = sys.argv[2]      
    csvfilename = sys.argv[3]
    fieldpdbname = sys.argv[4]
else:
    print(("usage :" + sys.argv[0] + " filename1.kont filename2.pdb filename1.csv filename1.pdb"))
    print ("       filename1.pdb is used to well identify atomname and residue")
    exit(1)

energy_dec_list = gridfield.read_splitted_contrib_csv(csvfilename)

energy, energy_coords, \
        _ , _ , _ , _ , _ , _ , _ , _ , _ , _ , _ , _  \
        = gridfield.read_kontfile(kontfilename)

#print energy.size, " ", len(energy_dec_list)

coords = []
radii = []
atomuniqid = []
mol = next(pybel.readfile("pdb", pdbfilename))
pt = openbabel.OBElementTable()
for atom in mol:
    coords.append(atom.coords)
    radii.append(pt.GetVdwRad(atom.OBAtom.GetAtomicNum ())) 
    residue = atom.OBAtom.GetResidue()
    atomuniqid.append(str(atom.OBAtom.GetId())+"_"+residue.GetName()+"_"+ \
            str(residue.GetNum()))

coords_map = {}
coords_field_pdb = []
atomuniqid_field_pdb = []
mol_field_pdb = next(pybel.readfile("pdb", fieldpdbname))
pt_field_pdb = openbabel.OBElementTable()
for atom in mol_field_pdb:
    uniqid = str(atom.OBAtom.GetType())+"_"+\
            str(atom.OBAtom.GetId())+"_"+\
            residue.GetName()+"_"+ \
            str(residue.GetNum())
    coords_field_pdb.append(atom.coords)
    residue = atom.OBAtom.GetResidue()
    atomuniqid_field_pdb.append(uniqid)
    
    x = atom.coords[0]
    y = atom.coords[1]
    z = atom.coords[2]
    stringa = "%.3f_%.3f_%.3f"%(x, y, z)
    coords_map[stringa] = uniqid

    #print stringa, " ==> ", uniqid

counter = 0
counter_multiple = 0
peratom_counter = []
peratom_counter_multiple = []

for ai in range(len(coords)):
    peratom_counter.append(0)
    peratom_counter_multiple.append(0)

print(kontfilename, " , ", pdbfilename)

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
                    
                    index = "%.3f_%.3f_%.3f"%(x, y, z)
                    if index in energy_dec_list:
                        #stringa = atomuniqid[mindistai] + " , " + \
                        #        "%10.3f , %10.3f , %10.3f , "%(x, y, z)
                        stringa = atomuniqid[mindistai] + " , " + \
                                "%10.3f , "%(e)
                        tot = 0.0
                        for a in energy_dec_list[index].atomslist:

                            num = a[0]
                            name = a[1]
                            resname = a[2]
                            x = a[3]
                            y = a[4]
                            z = a[5]
                            perc = a[6]

                            tot += perc
                            
                            chiave = "%.3f_%.3f_%.3f"%(x, y, z)
                            uniqid = "NOTFOUND_"+chiave
                            if chiave in coords_map:
                                uniqid = coords_map[chiave] 

                            stringa += "%s_%s_%s , %6.3f , "%( name, resname, uniqid, perc)

                        #stringa += str(e)
                        
                        if math.fabs(tot - 100.0) > 10.0:
                            print("Error in total perc")
                            exit(1)

                        print(stringa)
                else:
                    print("Error")
                    exit(1)

            elif partialconter  == 1:
                for ai in range(len(coords)):
                    if isnearatom[ai] != 0:
                        peratom_counter[ai] += 1

                        index = "%.3f_%.3f_%.3f"%(x, y, z)
                        if index in energy_dec_list:
                            #stringa = atomuniqid[ai] + " , " + \
                            #        "%10.3f , %10.3f , %10.3f , "%(x, y, z)
                            stringa = atomuniqid[ai] + " , " + \
                                    "%10.3f , "%(e)
                            tot = 0.0
                            for a in energy_dec_list[index].atomslist:

                                num = a[0]
                                name = a[1]
                                resname = a[2]
                                x = a[3]
                                y = a[4]
                                z = a[5]
                                perc = a[6]
                                
                                tot += perc
                                
                                chiave = "%.3f_%.3f_%.3f"%(x, y, z)
                                uniqid = "NOTFOUND_"+chiave
                                if chiave in coords_map:
                                    uniqid = coords_map[chiave] 
                                
                                stringa += "%s_%s_%s , %6.3f , "%( name, resname, uniqid, perc)

                            #stringa += str(e)
                            
                            if math.fabs(tot - 100.0) > 10.0:
                                print("Error in total perc")
                                exit(1)
                        
                            print(stringa)
 
            counter += partialconter

sum = 0
sum_multiple = 0
for ai in range(len(peratom_counter_multiple)):
    #if peratom_counter[ai] > 0:
    #  print ai+1, " , ", atomuniqid[ai], " , ", \
    #          peratom_counter_multiple[ai], " , ", \
    #          peratom_counter[ai]
    sum_multiple += peratom_counter_multiple[ai]
    sum += peratom_counter[ai]

if sum_multiple != counter_multiple:
    print("Error in Tot: ", sum_multiple, " vs ", counter_multiple)

if sum != counter:
    print("Error in Tot: ", sum, " vs ", counter)
