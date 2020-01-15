# Download the NCBI genome summary
wget -c ftp://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_genbank.txt
# Download NCBI taxonomy (taxdump) WTF is this?
wget -c ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz
tar xvf taxdump.tar.gz
# Parse taxdump for all legal taxonomy
# Then search the taxid in assemlies summary for the seven level taxonomy
scripts/search_taxdump_for_assmebly_summary.py
# Create the folder for all genomes
scripts/get_download_summary_for_clades.py Fungi
scripts/get_download_summary_for_clades.py Prokaryota
scripts/get_download_summary_for_clades.py Unclassified_Eukaryota
scripts/get_download_summary_for_clades.py Metazoa
scripts/get_download_summary_for_clades.py Viridiplantae
scripts/get_download_summary_for_clades.py Virus
# The script will generated a taxa-fixed GTDB style taxonomy file, and a download list for that clade.
# And a command for download them.