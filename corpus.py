# -*- coding: utf-8 -*-

# Prepare corpus. Call this module after download using download.sh
# directory: corpus/download


import xutils, os, glob
from gensim.corpora.wikicorpus import extract_pages, filter_wiki
from nltk import sent_tokenize


def wikipedia_extract(input_file, output_dir):
    #character chunk
    chunk_size = 50000000
    os.makedirs(output_dir, exist_ok=True)
    fin = xutils.open_file(input_file, 'rt')
    extractor = extract_pages(fin, ['0'])
    
    fout, counter, chunk = None, chunk_size, -1
    for page in extractor:
        if page[1]:
            text = filter_wiki(page[1])
            if counter >= chunk_size:
                if fout: fout.close()
                counter, chunk = 0, chunk + 1
                output_file = '%s/%s_%d.txt.gz' % (output_dir, os.path.basename(input_file), chunk)
                fout = xutils.open_file(output_file, 'wt')
                print(output_file)
                
            counter += len(text)
            fout.write(text)
            fout.write('\n\n\n\n')   
    fin.close()
    

def extract_pubmed(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    flags = [["<ArticleTitle>", "</ArticleTitle>"], ["<AbstractText>",  "</AbstractText>"]]
    for fn in glob.glob(input_dir + '/**/*.xml.gz', recursive=True):
        print(fn)
        fin = xutils.open_file(fn, 'rt')
        fout = xutils.open_file(output_dir + '/' + os.path.splitext(os.path.basename(fn))[0] + '.txt', 'wt')
        for line in fin:
            for flag in flags:
                i = line.find(flag[0])
                while i > 0:
                    j = line.find(flag[1], i)
                    txt = line[i + 14: j]
                    i = line.find(flag[0], j)
                    fout.write(txt)
                    fout.write('\n')
        fout.close()
    

def preprocess_line(input_str):
    if len(input_str) >= 25 and '\t' not in input_str:
        tokens = [x for x in xutils.tokenize(input_str) if x]
        if len(tokens) >= 5:
            return ' '.join(tokens)
            
        
def preprocess_merge(input_files, output_file):
    fout = xutils.open_file(output_file, 'wt')
    for input_file in input_files:
        fin = xutils.open_file(input_files, 'rt')
        lines = fin
        if 'pmc_ocr' in input_file:
            lines = sent_tokenize(fin.read().replace('-\n', '').replace('\n', ' '))
        for line in lines:
            new_line = preprocess_line(line)
            if new_line: 
                fout.write(new_line)
                fout.write('\n')
        fin.close()
        fout.write('\n\n')
    fout.close()
    
 
def preprocess(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok = True)
    for df in os.listdir(input_dir): 
        df = input_dir + '/' + df
        print(df)
        f = [df] if os.path.isfile(df) else glob.glob(df + '/**/*.*', recursive=True)
        preprocess_merge(f, output_dir + '/' + os.path.splitext(os.path.basename(df))[0] + '.gz')
    


if __name__ == '__main__':
    wikipedia_extract(xutils.Dirs.Corpus + 'download/enwiki-latest-pages-articles.xml.bz2', xutils.Dirs.Corpus + 'download/wikipedia')
    extract_pubmed(xutils.Dirs.Corpus +  'download/ftp.ncbi.nlm.nih.gov/pubmed', xutils.Dirs.Corpus + 'download/pubmed')
    preprocess(xutils.Dirs.Corpus + 'download/wikipedia', xutils.Dirs.Corpus + 'tokenized/wikipedia')
    preprocess(xutils.Dirs.Corpus + 'download/pubmed', xutils.Dirs.Corpus + 'tokenized/pubmed')
    preprocess(xutils.Dirs.Corpus + 'download/pmc_manuscript', xutils.Dirs.Corpus + 'tokenized/pmc_manuscript')
    preprocess(xutils.Dirs.Corpus + 'download/pmc_oa', xutils.Dirs.Corpus + 'tokenized/pmc_oa')
    
