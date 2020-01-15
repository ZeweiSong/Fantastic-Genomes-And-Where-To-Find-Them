#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 10:36:47 2018

This script will parse the NCBI names.dmp and nodes.dmp into species taxid and its seven level
taxonomy. Then it will look into NCBI genome summary file for the corresponding FTP
link and accession id.

Coders who love to comment their code are unlikely to have bad luck.

@author: Zewei Song
@email: songzewei@genomics.cn
"""
#%
from __future__ import print_function
from __future__ import division
import networkx as nx

names_dump = 'names.dmp'
nodes_dump = 'nodes.dmp'
genome_summary = 'assembly_summary_genbank.txt'

# With a given nodeid and graph, return the seven (eight) levels linear in taxid
# 0 is not an eligible NCBI taxid, we used here as a place holder
def uptrace(nodeid, graph):
    thesevens = {'species':0, 'genus':0, 'family':0, 'order':0, 'class':0, 'phylum':0, 'kingdom':0, 'superkingdom':0}
    level = graph.nodes[nodeid]['level']
    thesevens[level] = nodeid
    pre = list(graph.predecessors(nodeid))
    while pre:
        nodeid = pre[0]
        level = graph.nodes[nodeid]['level']
        if level in thesevens.keys():
            thesevens[level] = nodeid
        else:
            pass
        pre = list(graph.predecessors(pre[0]))    
    return thesevens

# With a given nodeid and graph, return all level linear
def uptraceAll(nodeid, graph):
    level = graph.nodes[nodeid]['level']
    linear = [(nodeid, level)]
    pre = list(graph.predecessors(nodeid))
    while pre:
        nodeid = pre[0]
        level = graph.nodes[nodeid]['level']
        linear.append((nodeid, level))
        pre = list(graph.predecessors(nodeid))
    return linear

#%%
# Read in nodes.dmp, add edges to a directed graph
print('Parsing NCBI taxdump, this may take a while ...')    

G = nx.DiGraph()
countLine = 0
levelSpace = {}

with open(nodes_dump, 'r') as f:
    for line in f:
        countLine += 1
        line = line.strip('\n').split('\t|\t')
        child = int(line[0])
        parent = int(line[1])
        levelSpace[line[2]] = levelSpace.get(line[2], 0) + 1
        if child == parent: # This is the root node 
            G.add_node(child)
            G.nodes[child]['level'] = line[2]
        else:
            G.add_edge(parent, child)
            G.nodes[child]['level'] = line[2]
print('nodes.dmp has {0} lines.'.format(countLine))
print('Graph contains {0} nodes, and {1} edges.'.format(G.number_of_nodes(), G.number_of_edges()))
#print(levelSpace)

#%%
# Read in names.dmp and save in dictionary using taxid as key
names = {0:[('Unclassified', '', 'scientific name')]}
with open(names_dump, 'r') as f:
    for line in f:
        line = line.strip('\t|\n').split('\t|\t')
        nodeid = int(line[0])
        value = line[1]
        unique_name = line[2]
        name_class = line[3]
        names[nodeid] = names.get(nodeid, []) + [(value, unique_name, name_class)]
print('Found {0} names in names.dmp.'.format(len(names)))

# Clean names.dmp to leave only scientific names
# scientific_names is the Namespace for all taxid
scientific_names = {}
for key, value in names.items():
    for record in value:
        if record[2] == 'scientific name':
            scientific_names[key] = scientific_names.get(key, []) + [record]
print('Clean up and leave {0} scientific names.'.format(len(scientific_names)))
#%% This is for testing only
#taxid = 7227
#linear = uptrace(taxid, G)
#linear_string = {'species':0, 'genus':0, 'family':0, 'order':0, 'class':0, 'phylum':0, 'kingdom':0, 'superkingdom':0}
#linear_string = {level:(scientific_names[value][0][0], value) for level, value in linear.items()}
#print(linear_string)

#%% open assembly_summary_genbank.txt and search for taxonomy.
taxa = []
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

samples = {}
no_record = []
count = 0
with open(genome_summary, 'rb') as f:
    f.readline()
    f.readline()
    for line in f:
        count += 1
        line = line.decode('utf-8', 'slashescape')
        line = line.strip('\n').split('\t')
        taxid = int(line[5])
        try:
            species = scientific_names[taxid]
            linear = uptrace(taxid, G)
            linear_string = {'species':0, 'genus':0, 'family':0, 'order':0, 'class':0, 'phylum':0, 'kingdom':0, 'superkingdom':0, 'accid':'', 'ftp':''}
            linear_string = {level:(scientific_names[value][0][0], value) for level, value in linear.items()}
            linear_string['ftp'] = line[19]
            linear_string['accid'] = line[0]
            linear_string['genome_type'] = line[4]
            taxa.append(linear_string)
        except KeyError:
            no_record.append(line)

if len(record) > 0:
    print('We found {0} records in the ncbi assemblies summary have taxid not in taxdump.'.format(len(no_record)))
    print('These record is saved in no_record_ncbi_assemblies.txt.')
    with open('no_record_ncbi_assemblies.txt', 'w') as f:
        for line in no_record:
            f.write('{0}\n'.format('\t'.join(line)))

print('{0} records in {1}.'.format(count, genome_summary))
print('{0} records found legal taxonomic linear in taxdump.'.format(count - len(no_record)))
print('Writen into ncbi_genbank_genomes.txt.')

with open('ncbi_genbank_genomes.txt', 'w') as f:
    f.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\n'.format('taxid', 'superkingdom', 'kingdom', 'phylum', 'class', 'order', \
                                                                'family', 'genus', 'species', 'accid', 'genome_type', 'ftp'))
    for item in taxa:
        taxid = item['species'][1]
        f.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\n'.format(taxid, item['superkingdom'][0], item['kingdom'][0],\
                item['phylum'][0], item['class'][0], item['order'][0], item['family'][0], item['genus'][0], item['species'][0], \
                item['accid'], item['genome_type'], item['ftp']))