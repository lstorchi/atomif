> protvsligand.csv
> ligandvsprto.csv 
> fieldvsfield.csv

cd ./Proteins/ 
ln -s ../fixpdb ./
ln -s ../kouttokont ./
ln -s ../k2xplor ./
ln -s ../ccd_dictionary.db ./

cd ../Ligands/
ln -s ../mol2kout ./
ln -s ../kouttokont ./
ln -s ../k2xplor ./
ln -s ../ccd_dictionary.db ./

cd ../


for name in $(cat names.txt); do 

  >&2 echo "$name" 

  cd ./Ligands/

  babel -imol2 "$name"_ligand_opt.mol2 -opdb "$name"_ligand_opt.pdb
  ./mol2kout "$name"_ligand_opt.mol2
  ./kouttokont "$name"_ligand_opt.kout DRY > "$name"_ligand_opt.kont 
  ./k2xplor  "$name"_ligand_opt.kont 
  mv 1.xplor "$name"_ligand_opt.xplor

  cd ../Proteins/

  ./fixpdb --kout-out="$name"_protein.kout "$name"_protein.pdb 
  ./kouttokont "$name"_protein.kout DRY > "$name"_protein.kont 
  ./k2xplor  "$name"_protein.kont 
  mv 1.xplor "$name"_protein.xplor

  cd ../

  python counter.py ./Proteins/"$name"_protein.kont ./Ligands/"$name"_ligand_opt.pdb >> protvsligand.csv
  python counter.py ./Ligands/"$name"_ligand_opt.kont ./Proteins/"$name"_protein.pdb >> ligandvsprto.csv

  python fieldvsfield.py ./Proteins/"$name"_protein.kont ./Ligands/"$name"_ligand_opt.kont >> fieldvsfield.csv
done

