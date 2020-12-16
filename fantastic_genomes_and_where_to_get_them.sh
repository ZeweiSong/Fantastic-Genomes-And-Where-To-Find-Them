# I describe the procedues of creating an index containing most microorganisms
# we can find in the environment. To do this, we have to put the genomes
# of all prokaryota, fungi, protists, virus, and human together
# Human genome is used as the default host genome.

# We also assume that genomes hosted on NCBI represent the major body
# of the genomes we known. Of course there are genomes being hind by
# individual labs that we are not aware of.

# The index is used for kraken2.

# New genomes can be added readily later.

# First let's download the NCBI genome summary to see what we got so far.
# This text file is supposed to contain all public availble genomes,
# that has been shared to the science community.
wget -c ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_genbank.txt

# The genomes are identified by their taxid. This is an ID system used by NCBI taxonomy to
# avoid conflict of identical terms. You can think of this as a taxonomy projection of the 
# genome data. Let's download NCBI taxonomy (taxdump).
wget -c ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz
gzip -cd taxdump.tar.gz | tar xvf

# Parse taxdump for all legal taxonomy
# Then search the taxid in assemlies summary for the seven level taxonomy
scripts/search_taxdump_for_assmebly_summary.py

# Create the folder for all genomes (Unused clades were commented out)
scripts/get_download_summary_for_clades.py Fungi
#scripts/get_download_summary_for_clades.py Prokaryota
scripts/get_download_summary_for_clades.py Unclassified_Eukaryota
#scripts/get_download_summary_for_clades.py Metazoa
#scripts/get_download_summary_for_clades.py Viridiplantae
scripts/get_download_summary_for_clades.py Virus

# The script will generated a taxa-fixed GTDB style taxonomy file, and a download list for that clade.
# And a command for download them.
# For our index, we will include all fungi, protist, viruses, and human genome, and 
# all genomes in GTDB.
# Of course, this will take a decent while.

cat ncbi_Fungi_genomes_download.txt | parallel -j 4 wget -q -c '{}' --directory-prefix=genomes_Fungi
cat ncbi_Unclassified_Eukaryota_genomes_download.txt | parallel -j 4 wget -q -c '{}' --directory-prefix=genomes_Unclassified_Eukaryota
cat ncbi_Virus_genomes_download.txt | parallel -j 4 wget -q -c '{}' --directory-prefix=genomes_Virus

# Download GRCh38.p13
wget https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/405/GCF_000001405.39_GRCh38.p13/GCF_000001405.39_GRCh38.p13_genomic.fna.gz
# Create the gtdb style taxonomy file
echo -e "RS_GCA_000001405.28\td__Metazoa;p__Chordata;c__Mammalia;o__Primates;f__Hominidae;g__Homo;s__Homo_sapiens" > ncbi_hg38_gtdb_taxonomy.txt

# Download the latest GTDB data
wget https://data.ace.uq.edu.au/public/gtdb/data/releases/release89/89.0/gtdbtk_r89_data.tar.gz
gzip -c gtdbtk_r89_data.tar.gz
tar -xvf gtdbtk_r89_data.tar

# Merge the gtdb style taxonomy into one
cat ncbi_Fungi_gtdb_taxonomy.txt ncbi_Unclassified_Eukaryota_taxonomy.txt ncbi_Virus_gtdb_taxonomy.txt ncbi_hg38_gtdb_taxonomy.txt release89/taxonomy/gtdb_taxonomy.tsv > gtdb_AllMicro_taxonomy.txt

# Here we need to create a pseudo taxdump as input for kraken2.
# https://github.com/rrwick/Metagenomics-Index-Correction has a ready to use script.
# We introduced several modifications to the script, so it is less likely to get errors.
# The script will check for redundant terms in all taxonomy. You need to run it several 
# times, and fix those redundant terms everytime, until you got a clean pass.
# Check for redundant terms and fix them all by hand (yes, you read in right)
scripts/tax_from_gtdb.py --gtdb gtdb_AllMicro_taxonomy.txt

# Gether all genome fasta file into one folder using softlinks
# Since there are too many files in a folder, we need to use
# a loop
filepath='/path/to/theOneIndexForAll/genomes_Fungi/'
for file in $(ls $filepath)
do
        echo $file
        ln -s $filepath$file /path/to/theOneIndexForAll/genomes_unlabeled/;
done

filepath='/path/to/theOneIndexForAll/genomes_Unclassified_Eukaryota/'
for file in $(ls $filepath)
do
        echo $file
        ln -s $filepath$file /path/to/theOneIndexForAll/genomes_unlabeled/;
done

filepath='/path/to/theOneIndexForAll/genomes_Virus/'
for file in $(ls $filepath)
do
        echo $file
        ln -s $filepath$file /path/to/theOneIndexForAll/genomes_unlabeled/;
done

filepath='/path/to/theOneIndexForAll/release89/fastani/database/'
for file in $(ls $filepath)
do
        echo $file
        ln -s $filepath$file /path/to/theOneIndexForAll/genomes_unlabeled/
done

# There should be more lines in taxonomy than that as genome fasta file.
# Since some taxons do not have genome sequenced.

# Let's run tax_from_gtdb.py again to add taxid to all genomes
# It will take a decent time to run
tax_from_gtdb.py --gtdb gtdb_AllMicro_taxonomy.txt --assemblies genomes_unlabeled --nodes toifa.tree -names toifa.name --kraken_dir genomes_kk2

# We can now add those genomes to the kraken2 library
find genomes_kk2/ -name '*.fa' -print0 | xargs -0 -I{} -n1 kraken2-build --add-to-library {} --db theOneIndexForAll

# Finally, we can build the index for kraken2.
# You will need a super large memory for calculating this index.
# By super large I mean the size of TB, like 1TB.
mkdir theOneIndexForAll/taxonomy
cp toifa.name theOneIndexForAll/taxonomy/names.dmp
cp toifa.tree theOneIndexForAll/taxonomy/nodes.dmp
kraken2-build --build --db theOneIndexForAll --threads 4