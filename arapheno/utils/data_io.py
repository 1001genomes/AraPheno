from datetime import datetime
import csv

'''
Accession Class
'''
class AccessionClass(object):
    def __init__(self):
        self.id = None
        self.name = None
        self.country = None
        self.sitename = None
        self.collector = None
        self.collection_date = None
        self.longitude = None
        self.latitude = None
        self.cs_number = None
        self.species = None

    def to_dict(self):
        fields = {'name':self.name,'country':self.country}
        return {'model':'phenotypedb.Accession','pk':self.id,'fields':fields}

'''
Parse Accession File Including Meta-Information (e.g. 1001 Genomes Master Table)
Input: filename: filename of accession file
Output: accession list: list of accession classes
'''
def parseAccessionFile(filename=None, species=1):
    if filename==None:
        return None
    accession_list = []
    with open(filename,'r') as f:
        reader = csv.reader(f,delimiter=',')
        header = reader.next()
        if header != ['id','name','country','sitename','latitude','longitude','collector','collectiondate','CS_number']:
            raise Exception('header must be of form %s' % header)
        for row in reader:
            accession = AccessionClass()
            accession.id = int(row[0])
            accession.name = row[1]
            accession.country = row[2]
            accession.sitename = row[3]
            try:
                accession.latitude = float(row[4])
            except:
                pass 
            try:
                accession.longitude = float(row[5])
            except: 
                pass
            accession.collector = row[6]
            try: 
                accession.collection_data = datetime.strptime(row[7],'%Y-%m-%d %H:%M:%S')
            except:
                pass
            accession.cs_number = row[8]
            accession_list.append(accession)
            accession.species = species
    return accession_list


def convertAccessionsToJson(accessions):
    accession_dict = []
    for acc in accessions:
        fields = {'name':acc.name,'country':acc.country,'sitename':acc.sitename,
        'collector':acc.collector,'collection_date':acc.collection_date,'latitude':acc.latitude,'longitude':acc.longitude,'cs_number':acc.cs_number,'species':acc.species}
        acc_dict = {'model':'phenotypedb.Accession','pk':acc.id,'fields':fields}
        accession_dict.append(acc_dict)
    return accession_dict

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
