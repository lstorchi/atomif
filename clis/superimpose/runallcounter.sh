> protvsligand.csv
> ligandvsprto.csv 
> fieldvsfield.csv

cd ./ligands
ln -s ../mol2kout ./
ln -s ../fixpdb ./
ln -s ../kouttokont ./
ln -s ../k2xplor ./
ln -s ../ccd_dictionary.db ./

cd ../

cd ./proteins
ln -s ../fixpdb ./
ln -s ../kouttokont ./
ln -s ../k2xplor ./
ln -s ../ccd_dictionary.db ./

cd ../

for name in $(cat names.txt); do 
  >&2 echo "$name" 

  cd ./ligands

  obabel -ixyz "$name"_LR-ligand.xyz -opdb -O "$name"_LR-ligand.pdb
  obabel -ixyz "$name"_LR-ligand.xyz -omol2 -O "$name"_LR-ligand.mol2
  ./mol2kout "$name"_LR-ligand.mol2
  ./kouttokont "$name"_LR-ligand.kout DRY > "$name"_LR-ligand.kont 
  ./k2xplor  "$name"_LR-ligand.kont 

  cd ../

  export BOXLIM=$(python extractbox.py ./ligands/"$name"_LR-ligand.kont)
  echo $BOXLIM

  cd ./proteins

  ./fixpdb --kout-out="$name"_protein.kout "$name"_protein.pdb 
  ./kouttokont "$name"_protein.kout DRY > "$name"_protein.kont 
  ./k2xplor  "$name"_protein.kont 
  
  cd ../

  python counter.py ./proteins/"$name"_protein.kont ./ligands/"$name"_LR-ligand.pdb >> protvsligand.csv
  python counter.py ./ligands/"$name"_LR-ligand.kont ./proteins/"$name"_protein.pdb >> ligandvsprto.csv

  python fieldvsfield.py ./proteins/"$name"_protein.kont ./ligands/"$name"_LR-ligand.kont >> fieldvsfield.csv

  python3 main.py  ./ligands/"$name"_LR-ligand.kont ./proteins/"$name"_protein.pdb > "$name"_ligandkont_vs_protein.csv
  python3 main.py  ./proteins/"$name"_protein.kont ./ligands/"$name"_LR-ligand.pdb  > "$name"_proteinkont_vs_ligand.csv
done
