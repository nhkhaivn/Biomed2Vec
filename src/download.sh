wget https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2
wget -r ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/
wget -r ftp://ftp.ncbi.nlm.nih.gov/pubmed/updatefiles/
wget -r ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/
wget -r ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/manuscript/
wget -r ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/historical_ocr/

mkdir ./pmc_manuscript
find ./ftp.ncbi.nlm.nih.gov/pub/pmc/manuscript/ -name "*.txt.tar.gz" -exec tar -xvf {} -C ./pmc_manuscript \;
mkdir ./pmc_oa
find ./ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/ -name "*txt.tar.gz" -exec tar -xvf {} -C ./pmc_oa \;
mkdir ./pmc_ocr
find ./ftp.ncbi.nlm.nih.gov/pub/pmc/historical_ocr/ -name "*.tar.gz" -exec tar -xvf {} -C ./pmc_ocr \;
