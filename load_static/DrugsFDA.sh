#/bin/bash
rm tmp_drugs -rf
mkdir tmp_drugs
cd tmp_drugs
wget https://www.fda.gov/downloads/Drugs/InformationOnDrugs/UCM527389.zip
unzip UCM527389.zip
cd ..

python load_tab.py tmp_drugs/Products.txt FdaProducts
python load_tab.py tmp_drugs/Submissions.txt FdaSubmissions
python load_tab.py tmp_drugs/SubmissionPropertyType.txt FdaSubmissionPropertyType
python load_tab.py tmp_drugs/SubmissionClass_Lookup.txt FdaSubmissionClassLookup
python load_tab.py tmp_drugs/TE.txt FdaTE
python load_tab.py tmp_drugs/MarketingStatus_Lookup.txt FdaMarketingStatusLookup
python load_tab.py tmp_drugs/MarketingStatus.txt FdaMarketingStatus add_int_id
python load_tab.py tmp_drugs/ApplicationsDocsType_Lookup.txt FdaApplicationsDocsTypeLookup
python load_tab.py tmp_drugs/ActionTypes_Lookup.txt FdaActionTypesLookup
python load_tab.py tmp_drugs/ApplicationDocs.txt FdaApplicationDocs
python load_tab.py tmp_drugs/Applications.txt FdaApplications add_int_id
