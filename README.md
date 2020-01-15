# Fantastic Genomes And Where To Find Them
 
This is a simple pipeline for parsing the assembly summary of all genomes from NCBI.

The summary file of genomes contains only the taxid. So we need to parse the taxonomy information using taxdump.

The script will search automatically for the seven level taxonomy, and will also correct for redundant taxa names (Unclassified and Candida).

To use the script, run it:

    git clone https://github.com/ZeweiSong/Fantastic-Genomes-And-Where-To-Find-Them
    cd Fantastic-Genomes-And-Where-To-Find-Them
    ./fantastic_genomes_and_where_to_get_them.sh
