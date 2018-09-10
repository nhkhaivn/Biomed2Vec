import xutils, os, sys, random, multiprocessing
from gensim.models import KeyedVectors, Word2Vec
from gensim.models.callbacks import CallbackAny2Vec

lg = xutils.get_logger('wordvec')

#corpus reader
class SentenceReader(object):
    def __init__(self, files):
        self.Files = files

    def __iter__(self):
        for filename in self.Files:
            with xutils.open_file(filename, 'rt') as file:
                for line in file:
                    terms = line.strip().replace('_', ' ').split()
                    if len(terms):
                        yield terms

#save model at every epoch
class EpochSaver(CallbackAny2Vec):
    def __init__(self, prefix, epoch=1, step=1):
        self.path_prefix = prefix
        self.epoch = epoch
        self.step = step
        self.first_epoch = True

    def on_epoch_end(self, model):
        output_path = '{}{}_epoch_{}'.format(xutils.Dirs.Temp, self.path_prefix, self.epoch)
        model.save(output_path)
        lg.info('Saved gensim model ' + output_path)

        if self.step == 1 or (not self.first_epoch and self.epoch % self.step == 0):
            output_path = '{}{}_epoch_{}'.format(xutils.Dirs.Model, self.path_prefix, self.epoch)
            model.wv.save_word2vec_format(output_path + '.bin', binary=True)
            lg.info('Saved Word2vec model ' + output_path + 'bin')

        # remove previous model if not the first epoch
        if not self.first_epoch:
            old_path = '{}{}_epoch_{}'.format(xutils.Dirs.Temp, self.path_prefix, self.epoch - 1)
            old_path = [old_path, old_path + '.trainables.syn1neg.npy', old_path + '.wv.vectors.npy']
            for op in old_path:
                if os.path.isfile(op):
                    os.remove(op)
                    lg.info('Removed gensim model ' + op)

        self.first_epoch = False
        self.epoch += 1

#word2vec training
def train(corpus, sz, epoch=10, begin_epoch=1, step=1):
    corpus = os.path.basename(corpus.strip('/\\'))
    xutils.get_logger(level=0)  # enable gensim log
    files = xutils.browse_files(xutils.Dirs.Corpus + corpus)

    model = Word2Vec(sg=0, size=sz, window=5, min_count=10, workers=multiprocessing.cpu_count())
    output_prefix = '%s_%d' % (corpus, sz)
    begin_model = '{}_epoch_{}'.format(xutils.Dirs.Temp + output_prefix, begin_epoch)
    if os.path.isfile(begin_model):
        lg.info('Loading ' + begin_model)
        model = Word2Vec.load(begin_model)
    else:
        if not os.path.isfile(xutils.Dirs.Corpus + corpus + '.vocab'):
            model.build_vocab(SentenceReader(files))
            vocab = {w: model.wv.vocab[w].count for w in model.wv.vocab}
            xutils.save(vocab, xutils.Dirs.Corpus + corpus + '.vocab')
        else:
            vocab = xutils.load(xutils.Dirs.Corpus + corpus + '.vocab')
            model.build_vocab_from_freq(vocab)
        del vocab

    epoch_saver = EpochSaver(output_prefix, begin_epoch, step)
    lg.info('Training word vectors of size %s from %s files' % (sz, len(files)))
    model.train(SentenceReader(files), epochs=epoch, callbacks=[epoch_saver], total_examples=model.corpus_count)
    model.wv.save_word2vec_format("{}{}_{}.bin".format(xutils.Dirs.Model, corpus, sz), binary=True)

#reduce vocab of word2vec model into predefined concepts
def reduce_to_vocab(model, output_file, concepts):
    if isinstance(model, str): model = KeyedVectors.load_word2vec_format(model, binary=True)
    vocab = [x for x in concepts if x in model]
    fo = xutils.open_file(output_file, 'wb')
    fo.write(('%s %s\n' % (len(vocab), model.vector_size)).encode('utf-8'))
    for w in vocab:
        fo.write(w.encode('utf-8') + b' ' + model[w].tostring())
    fo.close()


def benchmark(model, output_fname, synsets=None, test_size=0):
    if not synsets:
        cui_str = xutils.load('cui_pstr')
        shared_vocab = xutils.load('vector_shared_vocab')
        synsets = [x for x in cui_str.values() if len(x) > 1]
        synsets = [set(filter(lambda x: x in shared_vocab, y)) for y in synsets]
        synsets = [x for x in synsets if len(x) > 1]
            
    if isinstance(model, str):
        model = KeyedVectors.load_word2vec_format(model, binary=True)
    if test_size:
        test_size = min(test_size, len(synsets))
        synsets = synsets[:test_size]

    max_rank = len(model.vocab)

    rank = []
    sum_rank = 0
    tm = xutils.TimeWatch(len(synsets))
    for i, syns in enumerate(synsets):
        s = random.choice(list(syns))
        query_result = model.most_similar(s, topn=max_rank)
        lr = max_rank
        for j, r in enumerate(query_result):
            if r[0] in syns:
                lr = j
                break
        rank.append(lr)
        sum_rank += lr
        tm.update(i, sum_rank / (i + 1))
    xutils.save(rank, output_fname)




if __name__ == "__main__":
    if sys.argv[1]=='train':
        argv = [sys.argv[2]] + list(map(int, sys.argv[3:]))
        train(*argv)

    if sys.argv[1]=='benchmark':
        os.makedirs(xutils.Dirs.Temp+'benchmark', exist_ok=True)
        for m in sys.argv[3:]:
            shared_vocab = xutils.load(sys.argv[2])
            cui_str = xutils.load('cui_pstr')
            synsets = [x for x in cui_str.values() if len(x) > 1]
            synsets = [set(filter(lambda x: x in shared_vocab, y)) for y in synsets]
            synsets = [x for x in synsets if len(x) > 1]
            benchmark(xutils.Dirs.Model + m, xutils.Dirs.Temp + 'benchmark/' + m, synsets)

    if sys.argv[1]=='reduce':
        vocab = xutils.load(sys.argv[3])
        model = xutils.Dirs.find(sys.argv[2])
        reduce_to_vocab(model, model  + '.reduce', vocab )

