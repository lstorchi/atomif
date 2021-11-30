import openbabel
import pybel
import sys
import vtk

sys.path.append("./common")
import gridfield

ELIMIT = -1.0
VDW = 1.0

kontfilename = ""
pdbfilename = ""
usevtk = False

if (len(sys.argv)) == 3:
    kontfilename = sys.argv[1]
    pdbfilename = sys.argv[2]                        
else:
                                
    print("usage :", sys.argv[0] , " filename.kont filename.pdb ")
    exit(1)

energy, energy_coords, \
        _ , _ , _ , _ , _ , _ , _ , _ , _ , _ , _ , _  \
        = gridfield.read_kontfile(kontfilename)

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


spheres = []
if (usevtk):
    for ai in range(len(coords)):
        ax, ay, az = coords[ai]

        asphere = vtk.vtkSphereSource()
        asphere.SetCenter(ax, ay, az)
        asphere.SetRadius(float(VDW*radii[ai]))
        spheres.append(asphere)

fields = []
if usevtk:
    for iy in range(energy_coords.shape[1]):
        for ix in range(energy_coords.shape[0]):
            for iz in range(energy_coords.shape[2]):
                x, y, z, n = energy_coords[ix, iy, iz] 
                e = energy[ix, iy, iz]

                if e <= ELIMIT:
	            sphere = vtk.vtkSphereSource()
                    sphere.SetCenter(x, y, z)
                    sphere.SetRadius(float(0.1))
                    fields.append(sphere)


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
            
	    if usevtk and e < ELIMIT:
		    sphere = vtk.vtkSphereSource()
                sphere.SetCenter(x, y, z)
                sphere.SetRadius(float(0.1))
                fields.append(sphere)

	    #if e < -1.0:
            #    print "H ", x, " ", y, " ", z, " ", n

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

print(kontfilename, " ", pdbfilename, " ,", counter, " , " , counter_multiple)

sum = 0
sum_multiple = 0
for ai in range(len(peratom_counter_multiple)):
    if peratom_counter[ai] > 0:
      print(ai+1, " , ", atomuniqid[ai], " , ", \
              peratom_counter_multiple[ai], " , ", \
              peratom_counter[ai])
    sum_multiple += peratom_counter_multiple[ai]
    sum += peratom_counter[ai]

if sum_multiple != counter_multiple:
    print("Error in Tot: ", sum_multiple, " vs ", counter_multiple)

if sum != counter:
    print("Error in Tot: ", sum, " vs ", counter)

if usevtk:
   actors = []
   for s in spheres:
       mapper = vtk.vtkPolyDataMapper()
       if vtk.VTK_MAJOR_VERSION <= 5:
           mapper.SetInput(s.GetOutput())
       else:
           mapper.SetInputConnection(s.GetOutputPort())
           
       actor = vtk.vtkActor()
       actor.SetMapper(mapper)
       actor.GetProperty().SetOpacity(1.0)
       actors.append(actor)

   for s in fields:
       mapper = vtk.vtkPolyDataMapper()
       if vtk.VTK_MAJOR_VERSION <= 5:
           mapper.SetInput(s.GetOutput())
       else:
           mapper.SetInputConnection(s.GetOutputPort())
           
       actor = vtk.vtkActor()
       actor.SetMapper(mapper)
       actor.GetProperty().SetOpacity(1.0)
       actor.GetProperty().SetColor(1.0, 1.0, 0.0)
       actors.append(actor)
 
   
   ren = vtk.vtkRenderer()
   renWin = vtk.vtkRenderWindow()
   renWin.AddRenderer(ren)
   iren = vtk.vtkRenderWindowInteractor()
   iren.SetRenderWindow(renWin)
    
   for actor in actors :
     ren.AddActor(actor)
                   
   iren.Initialize()
   renWin.Render()
   iren.Start()

