import scipy as sp
from datetime import datetime

'''
Accession Class
'''
class AccessionClass(object):
    def __init__(self):
        self.accession_id = None
        self.accession_name = None
        self.accession_description = None
        self.url = None
        self.source = None
        self.country = None
        self.sitename = None
        self.collector = None
        self.collection_data = None
        self.longitude = None
        self.latitude = None

'''
Parse Accession File Including Meta-Information (e.g. 1001 Genomes Master Table)
Input: filename: filename of accession file
Output: accession list: list of accession classes
'''
def parseAccessionFile(filename=None):
    if filename==None:
        return None
    accession_list = []
    f = open(filename,'r')
    for i,line in enumerate(f):
        if not i==0:
            sv = line.strip().split(",")
            accession = AccessionClass()
            accession.accession_id = sv[0].strip()
            accession.source = sv[1].strip()
            accession.accession_name = sv[2].strip()
            accession.country = sv[3].strip()
            accession.sitename = sv[4].strip()
            try:
                accession.latitude = float(sv[5].strip())
            except:
                accession.latitude = None
            try:
                accession.longitude = float(sv[6].strip())
            except:
                accession.longitude = None
            accession.collector = sv[7].strip()
            if len(sv[8].strip())>0:
                try:
                    accession.collection_data = datetime.strptime(sv[8].strip().split(" ")[0],"%Y-%m-%d")
                except:
                    try:
                        accession.collection_data = datetime.strptime(sv[8].strip().split(" ")[0],"%m/%d/%y")
                    except:
                        accession.collection_data = None
            accession_list.append(accession)
    f.close()
    return accession_list

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
