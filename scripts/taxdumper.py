#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 10:36:47 2018

TAXDUMPER

This is a parser for NCBI's taxdump.

Coders who love to comment their code are unlikely to have bad luck.

@author: Zewei Song
@email: songzewei@genomics.cn
"""
#%$
from __future__ import print_function
from __future__ import division
import argparse
import os
import sys
import networkx as nx

print('Taxdumper, Super Duper!')

parser = argparse.ArgumentParser()
parser.add_argument('action', help='Choose the action to take.', nargs='?', choices=('download', 'search', 'uptrace', 'downtrace'))
args = parser.parse_args()

if args.action == 'download':
    ftp_path = 'https://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz'
    os.system('wget {0}'.format(ftp_path))
    os.system('tar xvfz taxdump.tar.gz')
    print('Taxdumper has downloaded taxdump!')
    print('Taxdumper, Super Duper!')
    sys.exit()
#%%
nodes_file = 'nodes.dmp' # nodes.dmp from taxdump.tar.gz downloaded from https://ftp.ncbi.nih.gov/pub/taxonomy/
names_file = 'names.dmp' # names.dmp from taxdump.tar.gz downloaded from https://ftp.ncbi.nih.gov/pub/taxonomy/

# With a given taxid and graph, return all its predecessors.
# 0 is not an eligible NCBI taxid, we used here as a place holder
# return a dictionary
def uptrace(nodeid, graph):
    # thesevens = {'species':0, 'genus':0, 'family':0, 'order':0, 'class':0, 'phylum':0, 'kingdom':0, 'superkingdom':0}
    linear = {} # a dictionary for saving the trace
    level = graph.nodes[nodeid]['level'] # get the level of the node
    linear[level] = nodeid
    pre = list(graph.predecessors(nodeid)) # get the first predecessor in the graph
    while pre:
        nodeid = pre[0] # get the taxid of current predecessor
        level = graph.nodes[nodeid]['level'] # get the level of this node
        linear[level] = nodeid # add to the linear dictionary
        pre = list(graph.predecessors(pre[0])) # go to the next predecessor
    return linear


# Get all children's taxid of a given taxid in the taxdump graph
# Since taxdump contains taxon level beyond the seven levels, we will only downtrace to the closest anchor level
# return a tuple of taxids
def downtrace(nodeid, graph):
    children_list = []
    thesevens = ('species', 'genus', 'family', 'order', 'class', 'phylum', 'kingdom', 'superkingdom') # These are the levels we like to report
    dfs_dict = nx.dfs_successors(graph, source=nodeid) # Get all successors begin with our node in this graph
    ranks = {}
    for key, value in dfs_dict.items():
        for node in value:
            ranks[graph.nodes[node]['level']] = ranks.get(graph.nodes[node]['level'], 0) + 1
    ranks = list(ranks.keys())
    child_rank = ''
    for item in thesevens[::-1]:
        if item in ranks:
            child_rank = item
            break
    if child_rank != '':
        for key, value in dfs_dict.items():
            for node in value:
                if graph.nodes[node]['level'] == child_rank: # Keep on those with the anchor level
                    children_list.append(node)
        return children_list
    else:
        return children_list
        

#%%    
# Read in the scientific names from names dump
# a taxid may contain more than one names. At least one of the names is unique.
names = {0:[('Unclassified', '', 'scientific name')]} # add Unclassified taxid as 0.
with open(names_file, 'r') as f:
    for line in f:
        line = line.strip('\t|\n').split('\t|\t')
        nodeid = int(line[0]) # taxid
        value = line[1] # name value in this line
        unique_name = line[2] # unique value of this taxid
        name_class = line[3] # type of this value
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

# Create a directed graph for the nodes
G = nx.DiGraph()
G.add_node(0) # this is the node for Unclassified
G.nodes[0]['value'] = [('Unclassified', '', 'scientific name')]
countLine = 0
levelSpace = {}
with open(nodes_file, 'r') as f:
    for line in f:
        countLine += 1
        line = line.strip('\n').split('\t|\t')
        child = int(line[0])
        parent = int(line[1])
        level = line[2]
        levelSpace[level] = levelSpace.get(level, 0) + 1 # count the number of each level
        if child == parent: # This is the root node 
            G.add_node(child)
            G.nodes[child]['level'] = level
            G.nodes[child]['value'] = scientific_names[child]
        else:
            G.add_edge(parent, child)
            G.nodes[child]['level'] = line[2]
            G.nodes[child]['value'] = scientific_names[child]
print('nodes.dmp has {0} lines.'.format(countLine))
print('The taxdump graph contains {0} nodes, and {1} edges.'.format(G.number_of_nodes(), G.number_of_edges()))
print('Level\tCount')
for key, value in levelSpace.items():
    print('{0}\t{1}'.format(key, value))

#%%
# Revert the dictionary so we can look up for all scientific names
thebigdict = {}
for key, value in scientific_names.items():
    thebigdict[value[0][0]] = key

#%%
thesevens = ('species', 'genus', 'family', 'order', 'class', 'phylum', 'kingdom', 'superkingdom')
if args.action == 'search':
    keep_going = True
    c = 'Y'
    result = ''
    taxid = 0
    while keep_going:
        print('\n')
        query = input('Please enter the term for querying: ')
        print('The term to search is {0}'.format(query))
        if query.isnumeric():
            print('Seems the input term is a taxid')
            query = int(query)
            taxid = query
            result = scientific_names.get(query, False)
            if result:
                print('The name of {0} is {1}'.format(query, result[0][0]))
            else:
                print('{0} not exist.'.format(query))
        else:
            print('Seems the input term is a keyword')
            result = thebigdict.get(query, False)
            taxid = result
            if result:
                print('The taxid of {0} is {1}'.format(query, result))
            else:
                print('{0} not exist'.format(query))
        if result:
            print('The query is at level: {0}'.format(G.nodes[taxid]['level']))
            result_uptrace = uptrace(taxid, G) # Get the linear of query node
            linear = []
            for i in thesevens: # For the full linear, get those in the seven anchor ranks
                node = result_uptrace.get(i, False)
                if node:
                    linear.append('\t'+i+':\t'+str(node)+'\t'+G.nodes[node]['value'][0][0])
            print('The uptrace linear of {0} is:\n{1}'.format(query, '\n'.join(linear)))
            result_downtrace = downtrace(taxid, G) # Get all the closest anchor level node of the quert node
            if result_downtrace:
                closest_anchor = G.nodes[result_downtrace[0]]['level']
                result_downtrace = ['\t'+str(i)+'\t'+G.nodes[i]['value'][0][0] for i in result_downtrace]
                print('The closest child anchor level is: {0} '.format(closest_anchor))
                print('The closest children are:\n{0}'.format('\n'.join(result_downtrace)))
            else:
                print('{0} is at the lowest level or not in the seven taxon levels'.format(query))
        c = input('Continue? (Y/n) ')
        while c not in ('Y', 'y', 'Yes', 'yes', 'N', 'n', 'No', 'no'):
            c = input('Continue? (Y/n) ')
        if c in ('Y', 'y', 'Yes', 'yes'):
            pass
        elif c in ('N', 'n', 'No', 'no'):
            print('Thanks for using taxdumper.')
            print('Taxdumper, Super Duper!')
            keep_going = False

elif args.action == 'uptrace':
    pass
elif args.action == 'downtrace':
    pass