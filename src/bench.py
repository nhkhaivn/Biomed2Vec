# -*- coding: utf-8 -*-
from gensim.models import KeyedVectors
import xutils,sys,os
from wordvec import reduce_to_vocab
from collections import defaultdict    

def merge(freqs):
    fq=defaultdict(int)
    for f in freqs:
        for t,c in f.items():
            fq[t]+=int(c)
    return fq

def corpus_stats():
    #run corpus.py count concept/wikipedia wikipedia
    #run corpus.py count concept/pubmed pubmed
    #run corpus.py count concept/pmc_manuscript pmc_manuscript
    #run corpus.py count concept/pmc_oa pmc_oa
    
    ss=['wikipedia', 'pubmed', 'pmc_manuscript', 'pmc_oa']
    r=[{x[0]:int(x[1]) for x in xutils.read_all_symbol_separated_file(s+'.txt') if len(x)==2} for s in ss]
    concepts=set(xutils.read_all_lines('umls_concepts.txt'))
    f=merge(r)
    r[2]=merge((r[2],r[3]))
    r[3]=f
    trans = lambda x: [(y.count('_')+1,y,x[y]) for y in x if y in concepts]
    ms=[trans(x) for x in r]
    
    for mm in ms:
        count=[0]*16
        frq=[0]*16
        for tc,c,f in mm:
            count[tc-1]+=1
            frq[tc-1]+=f
        print(count)
        print(frq)            
    sinle=[x for x in concepts if x.count('_')==0]    
    for f in r:
        m=[x for x in f if '_' not in x]
        print(len(m), sum(f[x] for x in m)) #token
        m=[x for x in f if '_' not in x and f[x]>=10]
        print(len(m), sum(f[x] for x in m)) #token, mincount=10
        
        m=[x for x in concepts if x in f]           #concept count, concept appearance
        print(len(m), sum(int(f[x]) for x in m))    
        
        m=[x for x in concepts if x in f and f[x]>=10] #concept count, concept appearance
        print(len(m), sum(int(f[x]) for x in m))
    
        m=[x for x in sinle if x in f and f[x]>=10] #concept count, concept appearance
        print(len(m), sum(int(f[x]) for x in m))


def collect_shared_vocab(model_names, output_file):
    shared_vocab = None
    for fname in model_names:
        m = KeyedVectors.load_word2vec_format(fname, binary=True)
        if not shared_vocab: 
            shared_vocab = set(m.vocab)             
        else:
            shared_vocab = set.intersection(shared_vocab, set(m.vocab))
    xutils.save(shared_vocab, output_file)
    


def analyze(fname):
    m=[1,5,10,20,50]
    d = xutils.load(fname)
    n=len(d)
    c=[len([x for x in d if x < t])/n for t in m]
    r = [1/(1+x) for x in d]
    mrr = sum(r)/len(r)
    return c + [mrr]


def test_stat(cui_str, vocab):    
    synsets = [x for x in cui_str.values() if len(x) > 1]
    synsets = [set(filter(lambda x: x in vocab, y)) for y in synsets]    
    synsets = [x for x in synsets if len(x) > 1]
    print(len(vocab), len(synsets), sum(len(x) for x in synsets), sum(len(x)*len(x)-1 for x in synsets))    
  
    
if __name__=='__main__':
    model = xutils.Dirs.Model+ sys.argv[1]
    t1=['pmc', 'pubmed', 'wikipedia','pub_wikipedia']
    t2=['pub_wikipedia']
    t3=['wikipedia-pubmed-and-PMC-w2v','pmc', 'pubmed', 'wikipedia','pub_wikipedia']
    t4=['concept_only','pmc', 'pubmed', 'wikipedia','pub_wikipedia']
    ss=[100,100,200,500]
    ns=['t1','t2','t3','t4']
    cui_str=xutils.load('cui_pstr')
    for n,s in zip(ns,ss):
        ms = ['%s%s_%d.bin'%(xutils.Dirs.Model, x, s) for x in eval(n)]
        collect_shared_vocab(ms, xutils.Dirs.Model + 'shared_vocab_' + n)
        vocab = xutils.load(xutils.Dirs.Model + 'shared_vocab_' + n)
        test_stat(cui_str, vocab)
        for m in ms:
            reduce_to_vocab(m, m + '.' + n, vocab)
            
    #run wordvec.py benchmark shared_vocab_t1 wikipedia_500.bin.t1 pubmed_500.bin.t1 pmc_500.bin.t1 pub_wikipedia_500.bin.t1
    #run wordvec.py benchmark shared_vocab_t2 pub_wikipedia_100.bin.t2 pub_wikipedia_200.bin.t2  pub_wikipedia_300.bin.t2  pub_wikipedia_400.bin.t2  pub_wikipedia_500.bin.t2
    #run wordvec.py benchmark shared_vocab_t3 wikipedia-pubmed-and-PMC-w2v_200.bin wikipedia_200.bin.t1 pubmed_200.bin.t1 pmc_200.bin.t1 pub_wikipedia_200.bin.t1
    #run wordvec.py benchmark shared_vocab_t4 concept_only_500.bin.t4 pub_wikipedia_500.bin.t1
    
    r = {os.path.basename(f):analyze(f) for f in xutils.browse_files(xutils.Dirs.Temp + 'benchmark/')}
    t = sorted(r, key=r.get)
    t = [(k,r[k]) for k in t]
    print(t)

