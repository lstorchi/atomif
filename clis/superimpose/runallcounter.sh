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

  obabel -ixyz "$name"_L_opt-frozen.xyz -opdb -O "$name"_L_opt-frozen.pdb
  obabel -ixyz "$name"_L_opt-frozen.xyz -omol2 -O "$name"_L_opt-frozen.mol2
  ./mol2kout "$name"_L_opt-frozen.mol2
  ./kouttokont "$name"_L_opt-frozen.kout DRY > "$name"_L_opt-frozen.kont 
  ./k2xplor  "$name"_L_opt-frozen.kont 

  cd ../

  export BOXLIM=$(python extractbox.py ./ligands/"$name"_L_opt-frozen.kont)
  echo $BOXLIM

  cd ./proteins

  ./fixpdb --kout-out="$name"_R_opt-frozen.kout "$name"_R_opt-frozen.pdb 
  ./kouttokont "$name"_R_opt-frozen.kout DRY > "$name"_R_opt-frozen.kont 
  ./k2xplor  "$name"_R_opt-frozen.kont 
  
  cd ../

  python counter.py ./proteins/"$name"_R_opt-frozen.kont ./ligands/"$name"_L_opt-frozen.pdb >> protvsligand.csv
  python counter.py ./ligands/"$name"_L_opt-frozen.kont ./proteins/"$name"_R_opt-frozen.pdb >> ligandvsprto.csv

  python fieldvsfield.py ./proteins/"$name"_R_opt-frozen.kont ./ligands/"$name"_L_opt-frozen.kont >> fieldvsfield.csv

  python3 main.py  ./ligands/"$name"_L_opt-frozen.kont ./proteins/"$name"_R_opt-frozen.pdb > "$name"_ligandkont_vs_R_opt-frozen.csv
  python3 main.py  ./proteins/"$name"_R_opt-frozen.kont ./ligands/"$name"_L_opt-frozen.pdb  > "$name"_R_opt-frozenkont_vs_ligand.csv
done

for name in $(cat names.txt); do 
  >&2 echo "$name" 
  python3 main.py  ./ligands/"$name"_L_opt-frozen.kont ./proteins/"$name"_R_opt-frozen.pdb > "$name"_ligandkont_vs_R_opt-frozen.csv
  python3 main.py  ./proteins/"$name"_R_opt-frozen.kont ./ligands/"$name"_L_opt-frozen.pdb  > "$name"_R_opt-frozenkont_vs_ligand.csv      
done
