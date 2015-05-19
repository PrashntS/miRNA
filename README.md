miRNA
=====

Contains explosive, uncommented scraping and statistics scripts for scraping gene and miRNA target description from ncbi. The only useful thing here you may find is perhaps the `gene_data_summary_target.json`.

`gene_data_summary_target.json` contains around 12,000 Genes and miRNAs that target the respective genes, their Description, and type. The data is scraped from `http://www.ncbi.nlm.nih.gov/`, which, surprisingly had a latency of 7 seconds (approx.) per request on Delhi University's 500MB Fiber line.
