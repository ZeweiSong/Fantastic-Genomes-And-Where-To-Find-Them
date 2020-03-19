# Download the NCBI genome summary
wget -c ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_genbank.txt

# Download NCBI taxonomy (taxdump) WTF is this?
wget -c ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz
tar xvf taxdump.tar.gz

# Parse taxdump for all legal taxonomy
# Then search the taxid in assemlies summary for the seven level taxonomy
scripts/search_taxdump_for_assmebly_summary.py

# Create the folder for all genomes (example)
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

cat ncbi_Fungi_genomes_download.txt | parallel -j 4 wget -q -c '{}' --directory-prefix=genomes_Fungi
cat ncbi_Unclassified_Eukaryota_genomes_download.txt | parallel -j 4 wget -q -c '{}' --directory-prefix=genomes_Unclassified_Eukaryota
cat ncbi_Virus_genomes_download.txt | parallel -j 4 wget -q -c '{}' --directory-prefix=genomes_Virus

# Download GRCh38.p13
wget https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/405/GCF_000001405.39_GRCh38.p13/GCF_000001405.39_GRCh38.p13_genomic.fna.gz
# Create the gtdb style taxonomy file
cat RS_GCA_000001405.28	d__Metazoa;p__Chordata;c__Mammalia;o__Primates;f__Hominidae;g__Homo;s__Homo_sapiens > ncbi_hg38_gtdb_taxonomy.txt

# Download the latest GTDB data
wget https://data.ace.uq.edu.au/public/gtdb/data/releases/release89/89.0/gtdbtk_r89_data.tar.gz
gzip -c gtdbtk_r89_data.tar.gz
tar -xvf gtdbtk_r89_data.tar

# Merge the gtdb style taxonomy into one
cat ncbi_Fungi_gtdb_taxonomy.txt ncbi_Unclassified_Eukaryota_taxonomy.txt ncbi_Virus_gtdb_taxonomy.txt ncbi_hg38_gtdb_taxonomy.txt release89/taxonomy/gtdb_taxonomy.tsv > gtdb_AllMicro_taxonomy.txt
# Check for redundant terms and fix them all by hand (yes, you read in right)
tax_from_gtdb.py --gtdb gtdb_AllMicro_taxonomy.txt

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
        ln -s $filepath$file /path/to/theOneIndexForAll/genomes_unlabeled/;
done

# There should be more lines in taxonomy than that as genome fasta file.
# Since some taxons do not have genome sequenced.

# Let's run tax_from_gtdb.py again to add taxid to all genomes
# It will take a decent time to run
tax_from_gtdb.py --gtdb gtdb_AllMicro_taxonomy.txt --assemblies genomes/unlabeled --nodes toifa.tree -names toifa.name --kraken_dir genomes_kk2

