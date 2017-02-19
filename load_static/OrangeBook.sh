#/bin/bash
rm tmp -rf
mkdir tmp
cd tmp
wget https://www.fda.gov/downloads/Drugs/InformationOnDrugs/UCM163762.zip
unzip UCM163762.zip
cd ..

python load_slide.py tmp/products.txt FdaOrangeBookProducts
python load_slide.py tmp/patent.txt FdaOrangeBookPatent
python load_slide.py tmp/exclusivity.txt FdaOrangeBookExclusivity
