import sys

#######################################################################

def sum_and_dump (all_atoms):
    
    for atom in all_atoms:
        
        tot = 0.0
        for i in range(2, len(all_atoms[atom]), 2):
            local_atom = all_atoms[atom][i]
            local_energy = all_atoms[atom][i+1]
            tot += local_energy

        for i in range(2, len(all_atoms[atom]), 2):
            all_atoms[atom][i+1] = 100.0*(all_atoms[atom][i+1]/tot)

        sys.stdout.write( atom + " , " + str(all_atoms[atom][0]) +" , " + \
                str(all_atoms[atom][1]))

        for i in range(2, len(all_atoms[atom]), 2):
            local_atom = all_atoms[atom][i]
            local_energy = all_atoms[atom][i+1]

            sys.stdout.write(" , " + local_atom + " , " + \
                    str(local_energy))
        sys.stdout.write("\n")

#######################################################################

csvname = ""

if (len(sys.argv)) == 2:
    csvname = sys.argv[1]
else:
    print("usage :", sys.argv[0] , " filename.csv ")
    exit(1)

fp = open(csvname, "r")

all_atoms = {}

for l in fp:
    sline = l.split(",")

    if len(sline) == 2:
        #print all_atoms
        sum_and_dump (all_atoms)
        all_atoms = {}
        print(sline[0].rstrip().lstrip(), " , ", sline[1].rstrip().lstrip())
    else:
        first_atom = sline[0].rstrip()
        first_atom = first_atom.lstrip()
        
        energy = sline[1].rstrip()
        energy = energy.lstrip()
        
        if first_atom in all_atoms:
            all_atoms[first_atom][0] += 1
            all_atoms[first_atom][1] += float(energy)

            new_values = []
            for i in range(2, len(sline)-1, 2):
                val = sline[i].rstrip()
                val = val.lstrip()
                new_values.append(val)
                val = sline[i+1].rstrip()
                val = val.lstrip()
                new_values.append(float(val))

            values = all_atoms[first_atom]

            for i in range(len(new_values), 2):
                atom = new_values[i]
                local_energy = new_values[i+1]

                added = False
                for j in (2, len(values), 2):
                    if values[j] == atom:
                        values[j+1] += local_energy 
                        added = True

                if not added:
                    values.append(atom)
                    values.append(local_energy)
        else:
            values = []
            values.append(1)
            values.append(float(energy))
            for i in range(2, len(sline)-1, 2):
                val = sline[i].rstrip()
                val = val.lstrip()
                values.append(val)
                val = sline[i+1].rstrip()
                val = val.lstrip()
                values.append(float(val))
        
            all_atoms[first_atom] = values 

sum_and_dump (all_atoms)

fp.close()
