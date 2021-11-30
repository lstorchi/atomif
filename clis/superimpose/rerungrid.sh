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

  export BOXLIM=$(python extractbox.py ./Ligands/"$name"_ligand_opt.kont)
  echo $BOXLIM

  cd ./Proteins/

  #mv "$name"_protein.xplor "$name"_protein.xplor.full
  #mv "$name"_protein.kont "$name"_protein.kont.full

  ./kouttokont -g "$BOXLIM" "$name"_protein.kout DRY > "$name"_protein.kont 
  ./k2xplor "$name"_protein.kont 
  mv 1.xplor "$name"_protein.xplor

  cd ../
done

