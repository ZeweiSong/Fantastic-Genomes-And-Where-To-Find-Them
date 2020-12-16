#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 10:36:47 2018

Coders who love to comment their code are unlikely to have bad luck.

@author: Zewei Song
@email: songzewei@genomics.cn
"""
#%%
from __future__ import print_function
from __future__ import division
import os
from pathlib import Path

content = []
with open('ncbi_fungi_genomes.list', 'r') as f:
    f.readline()
    for line in f:
        line = line.strip('\n').split('\t')
        content.append(line)
print(len(content))

group_list = {}
with open('ncbi_fungi_genome_group_index.txt', 'r') as f:
    for line in f:
        line = line.strip('\n').split('\t')
        group_list[line[0]] = int(line[1])
#%%
cmd_list = []
count = 0
local_path = '/ifs1/pub/database/ftp.ncbi.nih.gov/genomes/all/'
ncbi_path = 'ftp://ftp.ncbi.nlm.nih.gov/genomes/all/'
for line in content:
    filename = line[27].split('/')[-1] +'_genomic.fna.gz'
    path = line[27].replace(ncbi_path, local_path) + '/' + filename
    try:
        group_index = group_list[filename]
        cmd = 'ln -s ' + path + ' fg_{0}/'.format(group_index)
        cmd_list.append(cmd)
        if Path(path).is_file():
            count += 1
            os.system(cmd)
        else:
            print(path)
    except KeyError:
        print('Genome not in the list')

print(count)