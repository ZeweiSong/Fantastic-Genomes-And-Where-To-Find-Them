#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 10:36:47 2018

Parse all NCBI genomes

Coders who love to comment their code are unlikely to have bad luck.

@author: Zewei Song
@email: songzewei@genomics.cn
"""
#%%
from __future__ import print_function
from __future__ import division
import codecs
def slashescape(err):
    """ codecs error handler. err is UnicodeDecode instance. return
    a tuple with a replacement for the unencodable part of the input
    and a position where encoding should continue"""
    #print err, dir(err), err.start, err.end, err.object[:err.start]
    thebyte = err.object[err.start:err.end]
    repl = u'\\x'+hex(ord(thebyte))[2:]
    return (repl, err.end)

codecs.register_error('slashescape', slashescape)
file_path = 'ncbi_genbank_genomes.txt'
records = []
with open(file_path, 'rb') as f:
    for line in f:
        line = line.decode('utf-8', 'slashescape')
        line = line.strip('\n').split('\t')
        records.append(line)
print(len(records))
#%%
fungi = []
for line in records:
    if line[0] == 'Eukaryota' and line[1] == 'Fungi':
        fungi.append(line)
print(len(fungi))
with open('ncbi_fungi_genomes.txt', 'w', encoding = 'utf-8') as f:
    f.write('{0}\n'.format('\t'.join(records[0])))
    for line in fungi:
        f.write('{0}\n'.format('\t'.join(line)))
#%%
fungi = []
protist = []
bacteria = []
archaea = []

for line in records:
    if line[0] == 'Eukaryota':
        if line[1] == 'Fungi':
            fungi.append(line)
        elif line[1] == 'Unclassified':
            protist.append(line)
    elif line[0] == 'Bacteria':
        bacteria.append(line)
    elif line[0] == 'Archaea':
        archaea.append(line)
print(len(fungi), len(protist), len(bacteria), len(archaea))
#%%
species = {}
for line in fungi:
    s = line[7]
    ge = line[8]
    species[s] = species.get(s, 0) + 1
dist = {}
for key, value in species.items():
    dist[value] = dist.get(value, 0) + 1
dist_output = [(i, j) for i, j in dist.items()]
dist_output.sort(key=lambda x: x[0])
#%%
family = {}
for line in fungi:
    f = line[5]
    g = line[6]
    family[(f, g)] = family.get((f, g), 0) + 1
family = [i for i in family.keys()]
family_dict = {}
for item in family:
    family_dict[item[0]] = family_dict.get(item[0], 0) + 1
dist = {}
for key, value in family_dict.items():
    dist[value] = dist.get(value, 0) + 1
dist_output = [(i, j) for i, j in dist.items()]
dist_output.sort(key=lambda x: x[0])
print(dist_output)
#%%
with open('fungi-family-genus.dist', 'w') as f:
    f.write('ParentCount\tChildCount\n')
    for line in dist_output:
        f.write('{0}\t{1}\n'.format(line[0], line[1]))

#%% Parse the gtdb taxonomy
content = []
with open('gtdb_taxonomy.tsv', 'r') as f:
    for line in f:
        line = line.strip('\n').split('\t')
        t = line[1].split(';')
        content.append([line[0]] + t)
print(len(content))
accid = []
species = []
for line in content:
    accid.append(line[0])
    species.append(line[7])
accid = set(accid)
species = set(species)
print(len(accid), len(species), len(content))
#%%
genus = {}
for line in content:
    if line[1] == 'd__Bacteria':
        g = line[6]
        s = line[7]
        genus[(g, s)] = genus.get((g, s), 0) + 1
genus = [i for i in genus.keys()]
genus_dict = {}
for item in genus:
    genus_dict[item[0]] = genus_dict.get(item[0], 0) + 1
dist = {}
for key, value in genus_dict.items():
    dist[value] = dist.get(value, 0) + 1
dist_output = [(i, j) for i, j in dist.items()]
dist_output.sort(key=lambda x: x[0])
print(dist_output)

with open('gtdb-genus-species.dist', 'w') as f:
    f.write('ParentCount\tChildCount\n')
    for line in dist_output:
        f.write('{0}\t{1}\n'.format(line[0], line[1]))