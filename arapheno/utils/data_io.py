import scipy as sp

'''
Parse Accession File Including Meta-Information (e.g. 1001 Genomes Master Table)
Input: filename: filename of accession file
Output: 
'''

'''
Parse Phenotype File in PLINK format
Input: filename: filename of phenotype file
Output: phenotype_matrix: accession_ids x phenotypes (or replicates)
        accession_ids: scipy array of accession ids
        names: phenotype or replicate names
'''
def parsePhenotypePLINKFile(filename=None):
    if filename==None:
        return None
    #Parse file
    f = open(filename,'r')
    accession_ids = []
    pmatrix = []
    names = None
    split_delimiter = " "
    for i,line in enumerate(f):
        sv = line.strip().split(split_delimiter)
        if i==0:
            if len(sv)==1:
                sv = line.strip().split("\t")
                if len(sv)>1:
                    split_delimiter = "\t"
                else:
                    raise Exception("Wrong file format")
            names = map(lambda s: s.replace("_"," "),sv[2:])
        else:
            accession_ids.append(sv[0].strip())
            pmatrix.append(map(float,sv[2:]))
    f.close()
    accession_ids = sp.array(accession_ids)
    pmatrix = sp.array(pmatrix)
    return [pmatrix,accession_ids,names]
