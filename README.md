miRNA
=====

# Data Sources:
## Ensembl cDNA Sequences
Using Ensembl REST API, we get the cDNA (exons + UTR) sequences as such:
`http://rest.ensembl.org/sequence/id/<EID>?content-type=text/xfasta;type=cdna;multiple_sequences=1`

## NCBI Gene

1. First, get the Gene Ids `http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&term=DMRT2[GENE] AND "Homo Sapiens"[ORGN]`
2. Then, can obtain the data using: `http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=gene&id=10655&format=xml`

## Disease Linkage to Genes
`http://www.disgenet.org/web/DisGeNET/menu/downloads#curated`

## miRNA Link to Diseases
`http://www.mir2disease.org/`
Specifically, this file: `http://watson.compbio.iupui.edu:8080/miR2Disease/download/AllEntries.txt`

# miRNA Sequences from
`http://www.mirbase.org/ftp.shtml`
