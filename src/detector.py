# -*- coding: utf-8 -*-
import xutils, os, glob, multiprocessing, sys
from collections import defaultdict

def ngram(data, n):
    '''
    ngram generator from one file
    :param data: input file name or list of strings
    :param n: max n gram
    '''
    for line in data:
        tokens = line.split()
        terms = []
        for i in range(len(tokens)):
            if (len(terms) == n): del terms[-1]
            for j in range(len(terms)): terms[j].append(tokens[i])
            terms.insert(0, [tokens[i]])
            yield terms
        if line.endswith('\n'): yield '\n'


def detector(ngram_generator, concepts, window):
    '''
    Detect concepts from ngrams
    :param ngram_generator: ngram result as generator
    :param concepts: list of concepts
    :param window: window size
    :return: token/concept (as generator, one for each yield)
    '''
    cache = []
    for terms in ngram_generator:
        words = ['_'.join(x) for x in terms]
        matches = [(words[0], 0)] + [(x,i) for i,x in enumerate(words) if x in concepts]
        for m in reversed(matches): #iterate longest first
            i, j = 0, m[1]
            while j and -i < len(cache) and cache[i-1][1] < j:
                j = j - cache[i-1][1] - 1
                i = i - 1
            if not j: #can put m to cache
                if i: del cache[i:]
                cache.append(m)
                break

        if len(cache) == window:
            yield [cache.pop(0)[0]]
    yield [x[0] for x in cache]


def __detect_concepts(input_file, output_file, concepts, window_size):
    '''
    detect tokens and concepts in one file
    '''
    print(input_file)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    d = detector(ngram(xutils.open_file(input_file), window_size), concepts, window_size)
    f = xutils.open_file(output_file, 'wt') 
    for ts in d:
        for t in ts:
            f.write(t)
            if t != '\n': f.write(' ')
    f.close()


def __select_concepts(input_file, output_file, concepts, window_size):
    '''
    detect concepts in one file
    '''
    print(input_file)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    d = detector(ngram(xutils.open_file(input_file), window_size), concepts, window_size)
    f = xutils.open_file(output_file, 'wt') 
    for ts in d:
        for t in ts:
            if t in concepts or t=='\n':
                f.write(t)
                if t != '\n': f.write(' ')
    f.close()


def __corpus_counter(task):
    print(task)
    freq = defaultdict(int)
    with xutils.open_file(task) as file:
        for line in file:
            for word in line.strip().split():
                freq[word] = freq[word] + 1
                tok = word.split('_')
                if len(tok)>1:
                    for t in tok:
                        freq[t] = freq[t] + 1
    return freq


if __name__ == '__main__':
    '''
    Convert raw corpus to concept-recognized corpus
    '''
    if sys.argv[1]=='detect':
        inputCorpus = xutils.Dirs.Corpus + sys.argv[2]
        outputCorpus = xutils.Dirs.Corpus + sys.argv[3]
        window_size = 15
        concepts = set(xutils.read_all_lines('concepts.txt'))
        concepts_multi = set(filter(lambda x: 1 < len(x.split('_')) <= window_size, concepts))
        files = glob.glob(inputCorpus + '/**/*.*', recursive=True)
        pool = multiprocessing.Pool(8)
        for f in files:
            pool.apply_async(__detect_concepts, args = (f, f.replace(inputCorpus, outputCorpus), concepts_multi, window_size))
        pool.close()
        pool.join()

    '''
    Coverage analysis
    '''
    if sys.argv[1]=='count':
        inputCorpus = xutils.Dirs.Corpus + sys.argv[2]
        files = glob.glob(inputCorpus + '/**/*.*', recursive=True)
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        freq = pool.imap_unordered(__corpus_counter, (f for f in files))
        fr = defaultdict(int)
        for frq in freq:
            for c,f in frq.items():
                fr[c] = fr[c] + f
        xutils.write_all_lines(xutils.Dirs.Temp + sys.argv[3],
                               ('%s\t%d'%(k,v) for k, v in fr.items()))
        

    #generate Concept-only corpus
    # inputCorpus = xutils.Dirs.Corpus + 'concept'
    # outputCorpus = xutils.Dirs.Corpus + 'concept_only'
    # window_size = 15
    # concepts = set(xutils.read_all_lines('concepts.txt'))
    # concepts_multi = set(filter(lambda x: 0 < len(x.split('_')) <= window_size, concepts))
    # files = glob.glob(inputCorpus + '/**/*.*', recursive=True)
    # pool = multiprocessing.Pool(multiprocessing.cpu_count())
    # for f in files:
    #     pool.apply_async(__select_concepts, args = (f, f.replace(inputCorpus, outputCorpus), concepts_multi, window_size))
    # pool.close()
    # pool.join()
