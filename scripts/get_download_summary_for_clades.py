#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 10:36:47 2018

Generate the summary file for one clade of below:
    
    Fungi, Prokaryote, All unclassified Eukaryote, Viruses, Metazoa (animal), Viridiplantae (Plant)

Two files will be generated:
    ncbi_[clade]_gtdb_taxonomy.txt
    ncbi_[clade]_genomes_download.sh

Coders who love to comment their code are unlikely to have bad luck.

@author: Zewei Song
@email: songzewei@genomics.cn
"""
#%%
from __future__ import print_function
from __future__ import division
import argparse
from pathlib import Path
import os

parser = argparse.ArgumentParser()
parser.add_argument('clade', choices=['Fungi', 'Prokaryota', 'Virus', 'Metazoa', 'Viridiplantae', 'Unclassified_Eukaryota'], \
                    help='Specify a clade to parse.')
args = parser.parse_args()
clade = args.clade
# Check Unclassified (and Candida) redundancy
def fix_unclassified(taxa):
    if type(taxa) != 'list':
        taxa = taxa.split(';')
    assert len(taxa) == 7
    name = taxa[0][3:]
    taxa_nr = []
    for i, item in enumerate(taxa): # Starting from Phylum
        if i == 0:
            taxa_nr.append(item)
        else:
            if item[3:] == 'Unclassified' and taxa[i-1][3:15] != 'Unclassified':
                taxa_nr.append(item + taxa[i-1][3:])
                name = taxa[i-1][3:]
            elif item[3:] == 'Unclassified' and taxa[i-1][3:] == 'Unclassified':
                taxa_nr.append(item + name)
            elif item[3:] == 'Candida':
                taxa_nr.append(item + taxa[i-1][3:])
            else:
                taxa_nr.append(item)
    if taxa == taxa_nr:
        value = 0
    else:
        value = 1
    return (taxa_nr, value)

# An example taxonomy string
#t = 'd__Protozoa;p__Unclassified;c__Filasterea;o__Unclassified;f__Unclassified;g__Capsaspora;s__Capsaspora owczarzaki'

term = {'Fungi':((1, 'Fungi'),), 'Prokaryota':((0, 'Bacteria'), (0, 'Archaea')), \
        'Virus':((0, 'Viruses'),), 'Metazoa':((1, 'Metazoa'),), 'Viridiplantae':((1, 'Viridiplantae'),),\
        'Unclassified_Eukaryota':((0, 'Eukaryota'), (1, 'Unclassified'))}
genome_type = {'reference genome':'RS_', 'representative genome':'RS_', 'na':'GB_'}

#clade = 'Fungi'
if clade in term:
    print('{0} is the chosen clade.'.format(clade))
else:
    print('{0} is not a legal clade.'.format(clade))

print('Now parsing the genomes in NCBI ...')
content = []
with open('ncbi_genbank_genomes.txt', 'r') as f:
    for line in f:
        line = line.strip('\n').split('\t')
        if clade != 'Unclassified_Eukaryota':
            for search in term[clade]:
                if line[search[0]+1] == search[1] and line[-1] != 'na': # need to check if the FTP is 'na'
                    content.append([line[0], line[search[0]+1]] + line[2:])
                else:
                    pass
        else:
            if line[term[clade][0][0]+1] == term[clade][0][1] and line[term[clade][1][0]+1] == term[clade][1][1] and line[-1] != 'na': # need to check if the FTP is 'na'
                content.append([line[0], clade] + line[2:])

count = 0
with open('ncbi_' + clade + '_gtdb_taxonomy.txt', 'wt') as f:
    for line in content:
        line[8] = line[8].replace(' ', '_')
        taxa = 'd__' + line[1] + ';p__' + line[3] + ';c__' + line[4] + ';o__' + line[5] + ';f__' + line[6] + ';g__' + line[7] + ';s__' + line[8]
        taxa = fix_unclassified(taxa)
        count += taxa[1]
        accid = genome_type[line[10]] + line[9]
        f.write('{0}\t{1}\n'.format(accid, ';'.join(taxa[0])))

print('Finished analysis.')
print('\tFound {0} genomes with FTP link.'.format(len(content)))
print('\tFixed {0} taxa with ambiguous names.'.format(count))

folder = Path('genomes_' + clade)
finished_list = {}
if folder.is_dir():
    print('The folder genomes_{0}/ is there, I will check for genomes already downloaded.'.format(clade))
    filenames = os.listdir(folder)
    print('Seems there are {0} files already there.'.format(len(filenames)))
    for item in filenames:
        accid = item[:15]
        finished_list[accid] = item
else:
    print('I will create a new folder named "genomes_{0}"'.format(clade))
    os.makedirs(folder)

count = 0
count_to_fetch = 0
with open('ncbi_' + clade + '_genomes_download.txt', 'wt',newline='') as f:
    #f.write('mkdir genomes_{0}\n'.format(clade))
    for line in content:
        count += 1
        ftp = line[-1]
        link = ftp + '/' + line[-1].split('/')[-1] + '_genomic.fna.gz'
        accid = line[9]
        #f.write('wget -c {0} --directory-prefix=genomes_{1} --wait=5 --random-wait\n'.format(link, clade))
        try:
            finished_list[accid]
        except KeyError:
            count_to_fetch += 1
            f.write('{0}\n'.format(link))
print('Found {0} genomes availabe in NCBI genomes FTP.'.format(count))
if count_to_fetch != 0:
    print('Need to download {0} genomes.'.format(count_to_fetch))
    print('The FTP list for download is in {0}.'.format('ncbi_' + clade + '_genomes_download.txt'))
    print('You can download them in parallel using:\n')
    print('cat {0} | parallel -j 4 wget -q -c {1} --directory-prefix=genomes_{2}'.format('ncbi_' + clade + '_genomes_download.txt', '{}', clade))
    print('check parallel -h for how to set the parameters.')
else:
    print('You have all the genomes in this clade.')

