# Fantastic Genomes And Where To Find Them
 
# Introduction

This is a simple pipeline for parsing the assembly summary of all genomes from NCBI.

The summary file of genomes contains only the taxid. So we need to parse the taxonomy information using taxdump.

The script will search automatically for the seven level taxonomy, and will also correct for redundant taxa names (Unclassified and Candida).

To use the script, run it:

    git clone https://github.com/ZeweiSong/Fantastic-Genomes-And-Where-To-Find-Them
    cd Fantastic-Genomes-And-Where-To-Find-Them
    chmod 744 fantastic_genomes_and_where_to_get_them.sh
    ./fantastic_genomes_and_where_to_get_them.sh

You can run the two scripts independently too.
This command will get a GTDB style taxonomy file and a dwonload list for all fungi:

    scripts/get_download_summary_for_clades.py Fungi

Availabel clades are: Fungi, Prokaryota, Virus, Metazoa, Viridiplantae, and Unclassified_Eukaryota.

# The redundant taxa name and how do we remove them.

NCBI taxdump may contain some taxa name that have different parents. For example:

    d__Fungi;p__Ascomycota;c__Unclassified;
    d__Fungi;p__Basidiomycota;c__Unclassified;
  
Here the Phylum of c__Unclassified is not unique. This will create bias when reads are assigned to this bin, or when the taxonomic strcuture is used.
