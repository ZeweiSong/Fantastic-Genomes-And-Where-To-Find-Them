![alt text](https://github.com/ZeweiSong/Fantastic-Genomes-And-Where-To-Find-Them/blob/master/header.png)

# Fantastic Genomes And Where To Find Them
 
# Introduction

This is a simple pipeline for parsing the assembly summary of all genomes from NCBI. We have a pipeline on how to build a kraken2 index using customized genomes too.

The summary file of genomes contains only the taxid. So we need to parse the taxonomy information using taxdump.

The script will search automatically for the seven level taxonomy, and will also correct for redundant taxa names (Unclassified and Candida).

To use the script, run it:

    git clone https://github.com/ZeweiSong/Fantastic-Genomes-And-Where-To-Find-Them
    cd Fantastic-Genomes-And-Where-To-Find-Them
    
The two scripts can be run independently.
This command will get a GTDB style taxonomy file and a dwonload list for all fungi:

    scripts/get_download_summary_for_clades.py Fungi

Availabel clades are: Fungi, Prokaryota, Virus, Metazoa, Viridiplantae, and Unclassified_Eukaryota. The Unclassified_Eukaryota is mostly Protozoa.

The output of get_download_summary_for_clades.py will be like:

    Fungi is the chosen clade.
    The folder genomes_Fungi/ is there, I will check for genomes already downloaded.
    Seems there are 5300 files already there.
    Found 5575 genomes availabe in NCBI genomes FTP.
    Need to download 275 genomes.
    The FTP list is in ncbi_Fungi_genomes_download.txt.
    You can download them in parallel using:

    cat ncbi_Fungi_genomes_download.txt | parallel -j 4 wget -q -c {} --directory-prefix=genomes_Fungi

You can install parallel using:

    sudo apt-get parallel

# The redundant taxa name and how do we remove them.

NCBI taxdump may contain some taxa name that have different parents. For example:

    d__Fungi;p__Ascomycota;c__Unclassified;
    d__Fungi;p__Basidiomycota;c__Unclassified;
  
Here the Phylum of c__Unclassified is not unique. This will create bias when reads are assigned to this bin, or when the taxonomic strcuture is used. Another problem maker is "g_Candida".

We fix such inconsistence by assigning the upstream name to Unclassified or Candida. The taxonomic string above will be changed to:

    d__Fungi;p__Ascomycota;c__UnclassifiedAscomycota;
    d__Fungi;p__Basidiomycota;c__UnclassifiedBasidiomycota;

# Build a Kraken2 index.

Refer to fantastic_genomes_and_where_to_get_them.sh for an explaination on everystep.

fin.
