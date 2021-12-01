> protvsligand.csv
> ligandvsprto.csv 
> fieldvsfield.csv

cd ./ligands
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

  babel -ixyz "$name"_ligand_coord.xyz -opdb -O "$name"_ligand_coord.pdb
  babel -ixyz "$name"_ligand_coord.xyz -omol2 -O "$name"_ligand_coord.mol2
  ./mol2kout "$name"_ligand_coord.mol2
  ./kouttokont "$name"_ligand_coord.kout DRY > "$name"_ligand_coord.kont 
  ./k2xplor  "$name"_ligand_coord.kont 
  mv 1.xplor "$name"_ligand_coord.xplor

  cd ../

  export BOXLIM=$(python extractbox.py ./ligands/"$name"_ligand_coord.kont)
  echo $BOXLIM

  cd ./proteins

  ./fixpdb --kout-out="$name"_prot-ass_ok.kout "$name"_prot-ass_ok.pdb 
  ./kouttokont "$name"_prot-ass_ok.kout DRY > "$name"_prot-ass_ok.kont 
  ./k2xplor  "$name"_prot-ass_ok.kont 
  mv 1.xplor "$name"_prot-ass_ok.xplor
  
  cd ../

  python counter.py ./proteins/"$name"_prot-ass_ok.kont ./Ligands/"$name"_ligand_coord.pdb >> protvsligand.csv
  python counter.py ./ligands/"$name"_ligand_coord.kont ./Proteins/"$name"_prot-ass_ok.pdb >> ligandvsprto.csv

  python fieldvsfield.py ./proteins/"$name"prot-ass_ok.kont ./ligands/"$name"_ligand_coord.kont >> fieldvsfield.csv
done

exit

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

  ./fixpdb --kout-out="$name"_prot-ass_ok.kout "$name"_prot-ass_ok.pdb 
  ./kouttokont -g "$BOXLIM" "$name"_prot-ass_ok.kout DRY > "$name"_prot-ass_ok.kont 
  ./k2xplor  "$name"_prot-ass_ok.kont 
  mv 1.xplor "$name"_prot-ass_ok.xplor

  cd ../

  python counter.py ./proteins/"$name"_prot-ass_ok.kont ./Ligands/"$name"_ligan.pdb >> protvsligand.csv
  python counter.py ./ligands/"$name"_ligand_opt.kont ./Proteins/"$name"_protein.pdb >> ligandvsprto.csv

  python fieldvsfield.py ./Proteins/"$name"_protein.kont ./Ligands/"$name"_ligand_opt.kont >> fieldvsfield.csv
done

> protvsligand.csv
> ligandvsprto.csv 
> fieldvsfield.csv

cd ./proteins/ 
ln -s ../fixpdb ./
ln -s ../kouttokont ./
ln -s ../k2xplor ./
ln -s ../ccd_dictionary.db ./

cd ../ligands/
ln -s ../mol2kout ./
ln -s ../kouttokont ./
ln -s ../k2xplor ./
ln -s ../ccd_dictionary.db ./

cd ../


for name in $(cat names.txt); do 

  >&2 echo "$name" 

  export BOXLIM=$(python extractbox.py ./ligands/"$name"_ligand_opt.kont)
  echo $BOXLIM

  cd ./Proteins/

  #mv "$name"_protein.xplor "$name"_protein.xplor.full
  #mv "$name"_protein.kont "$name"_protein.kont.full

  ./kouttokont -g "$BOXLIM" "$name"_protein.kout DRY > "$name"_protein.kont 
  ./k2xplor "$name"_protein.kont 
  mv 1.xplor "$name"_protein.xplor

  cd ../
done

