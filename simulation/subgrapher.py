#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import json, csv, re
import math
import random
import networkx as nx
from networkx.algorithms import bipartite
from networkx.readwrite import json_graph

from miRNA_meta_data import miRNA_meta_data
from gene_meta_data import gene_meta_data

mirna_dict = {}
gene_dict = {}
gene_lis_for_mirna_subgraph = []
mirna_lis_for_gene_subgraph = []

'''
Forms data and subgraph for any miRNA as user input.
'''
def form_data_mirna():
	mirna_lis = random.sample(miRNA_meta_data.keys(), 10)
	loop = int(raw_input('Enter number of miRNAs you wish to choose.\n'))
	for i in xrange(0,loop):
		print mirna_lis
		user_input = str(raw_input('Choose miRNAs from above list.\n'))
		if user_input in mirna_lis:
			if user_input in miRNA_meta_data.keys():
				mirna_dict, gene_lis_for_mirna_subgraph = collect_gene_info_for_mirna(user_input)
		else:
			print 'Wrong input. Please enter again.'
			sys.exit(0)

	mirna_subgraph(mirna_dict, gene_lis_for_mirna_subgraph)


def collect_gene_info_for_mirna(user_input):
	'''
	Creates a list of genes to be included as nodes.
	Creates miRNA dictionary with host gene and target genes with affinity.
	'''
	target_gene_lis_for_mirna_subgraph = []
	host_gene_lis_for_mirna_subgraph = []
	mirna_dict[user_input] = {}
	if 'Target Gene with Transcript Count' in miRNA_meta_data[user_input].keys():
		# This list contains tuples of the format (gene symbol, transcript count, affinity).
		target_gene_lis_for_mirna_subgraph = miRNA_meta_data[user_input]["Target Gene with Transcript Count"]
		
	if 'Host Gene' in miRNA_meta_data[user_input].keys() and not miRNA_meta_data[user_input]['Host Gene'] == '':
		host_gene_lis_for_mirna_subgraph.append(miRNA_meta_data[user_input]["Host Gene"])

	for each in host_gene_lis_for_mirna_subgraph:
		gene_lis_for_mirna_subgraph.append(each)

	for each in target_gene_lis_for_mirna_subgraph:
		# each - tuple; each[0] - gene symbol
		gene_lis_for_mirna_subgraph.append(each[0])

	mirna_dict[user_input]['Target Genes'] = target_gene_lis_for_mirna_subgraph
	mirna_dict[user_input]['Host Genes'] = host_gene_lis_for_mirna_subgraph
	
	# print gene_lis_for_mirna_subgraph
	# print mirna_dict

	return mirna_dict, gene_lis_for_mirna_subgraph


def mirna_subgraph(mirna_dict, gene_lis_for_mirna_subgraph):
	G = nx.DiGraph()
	G.add_nodes_from(mirna_dict.keys())
	G.add_nodes_from(gene_lis_for_mirna_subgraph)

	for mirna in mirna_dict:
		for target_gene in mirna_dict[mirna]['Target Genes']:
			G.add_edge(mirna, target_gene[0])
		for host_gene in mirna_dict[mirna]['Host Genes']:
			G.add_edge(host_gene, mirna)
		# g.add_edges_from(mirna, mirna_dict[mirna]['Target Genes'])
		# g.add_edges_from(mirna_dict[mirna]['Host Genes'], mirna)
	nx.write_gexf(G,"mirna_subgraph.gexf")
	print 'Done!'

'''
Forms data for any gene as user input.
'''
def form_data_genes():
	gene_lis = random.sample(gene_meta_data.keys(), 10)
	loop = int(raw_input('Enter number of genes you wish to choose.\n'))
	for i in xrange(0,loop):
		print gene_lis
		user_input = str(raw_input('Choose genes from above list.\n'))
		if user_input in gene_lis:
			if user_input in gene_meta_data.keys():
				mirna_lis_for_gene_subgraph, gene_dict = collect_mirna_info_for_gene(user_input)
		else:
			print 'Wrong input. Please enter again.'
			sys.exit(0)

	gene_subgraph(gene_dict, mirna_lis_for_gene_subgraph)


def collect_mirna_info_for_gene(user_input):
	'''
	Creates a list of miRNAs to be included as nodes.
	Creates gene dictionary with 'host for' and 'target for' keys with miRNA as values.
	'''
	mirna_host_lis = []

	if 'Host for' in gene_meta_data[user_input].keys() and not gene_meta_data[user_input]['Host for'] == '':
		mirna_host_lis.append(gene_meta_data[user_input]['Host for'])
	if 'Target for' in gene_meta_data[user_input].keys():
		mirna_target_lis = gene_meta_data[user_input]['Target for']
	
	mirna_lis_for_gene_subgraph = mirna_host_lis + mirna_target_lis

	gene_dict[user_input] = {}
	gene_dict[user_input]['Host for'] = gene_meta_data[user_input]['Host for']
	gene_dict[user_input]['Target for'] = gene_meta_data[user_input]['Target for']

	# print mirna_lis_for_gene_subgraph
	# print gene_dict

	return mirna_lis_for_gene_subgraph, gene_dict


def gene_subgraph(gene_dict, mirna_lis_for_gene_subgraph):
	G = nx.DiGraph()
	G.add_nodes_from(gene_dict.keys())
	G.add_nodes_from(mirna_lis_for_gene_subgraph)

	for gene in gene_dict.keys():
		for host_mirna in gene_dict[gene]['Host for']:
			G.add_edge(gene, host_mirna)
		for target_mirna in gene_dict[gene]['Target for']:
			G.add_edge(target_mirna, gene)

	nx.write_gexf(G,"gene_subgraph.gexf")
	print 'Done!'


def jsonify(dictionary, filename, text='None'):
	a = json.dumps(dictionary, sort_keys=True, indent=4, separators=(',', ': '))
	with open(str(filename), 'w') as outfile:
		if text == 'None':
			outfile.write(a)
		else:
			outfile.write(text + ' = ')
			outfile.write(a)


if __name__ == '__main__':
	form_data_mirna()
	with open('./gene_ID_Store.json', 'r') as infile:
		gene_data = json.loads(infile.read())
		form_data_genes()
		
		# For all genes
		gene_subgraph(gene_meta_data, miRNA_meta_data.keys())