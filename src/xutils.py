import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')

import sys, os, time, logging, gzip, bz2, pickle, collections
from gensim.utils import tokenize as gensim_tokenizer


class Dirs:
    Model = '../model/'
    Data = '../input/'
    Log = '../log/'
    Corpus = '../corpus/'
    Temp = '../tmp/'

    @staticmethod
    def init():
        path = os.path.dirname(os.path.realpath(__file__)) + '/'
        Dirs.Model = path + Dirs.Model
        Dirs.Data = path + Dirs.Data
        Dirs.Log = path + Dirs.Log
        Dirs.Corpus = path + Dirs.Corpus
        Dirs.Temp = path + Dirs.Temp
        os.makedirs(Dirs.Model, exist_ok=True)
        os.makedirs(Dirs.Model, exist_ok=True)
        os.makedirs(Dirs.Data, exist_ok=True)
        os.makedirs(Dirs.Log, exist_ok=True)
        os.makedirs(Dirs.Corpus, exist_ok=True)
        os.makedirs(Dirs.Temp, exist_ok=True)

    @staticmethod
    def find(file):
        if not os.path.isfile(file):
            if not os.path.isdir(os.path.dirname(file)):
                name = os.path.basename(file)
                for d in (Dirs.Data, Dirs.Model, Dirs.Temp, Dirs.Corpus, Dirs.Log):
                    if os.path.isfile(d + name):
                        lg.info('Found: %s in %s', name, d)
                        return d + name
        return file


Dirs.init()

def get_logger(name=None, level=logging.INFO):
    log = logging.getLogger(name)
    if not name: name = 'root'
    log.setLevel(level)
    for h in log.handlers[:]:
        log.removeHandler(h)

    ch = logging.StreamHandler(sys.stdout)
    fh = logging.FileHandler(filename=Dirs.Log + name + '.log')
    fm = logging.Formatter(fmt='%(asctime)s [%(levelname)s] %(message)s (%(filename)s:%(lineno)s)',
                           datefmt='%Y-%m-%d:%H:%M:%S')
    fh.setFormatter(fm)
    ch.setFormatter(fm)
    log.addHandler(fh)
    log.addHandler(ch)
    fh.setLevel(level if name != 'root' else logging.WARNING)
    ch.setLevel(level)
    return log

get_logger(level=logging.WARNING) #root logger, triggers WARN
lg = get_logger('xutils')


def join(sep=' ', *tup):
    '''
        Join anythings
    '''
    return sep.join(map(str, tup))


class TimeWatch:
    '''
        Stopwatcher with percentage, estimation, and output delay
    '''
    # goal = 0: undefined goal
    # min_interval: not return time string if elapsed step duration is less than min_interval, to prevent fast continuous output
    def __init__(self, goal=0, update_type='increment', min_interval=1):
        self.Previous = self.Start = time.time()
        self.Interval = min_interval
        self.Progress = 0
        self.Goal = goal
        self.UpdateType = update_type

    def progress(self, value=1, *message_on_update):
        self.Progress = self.Progress + value if self.UpdateType == 'increment' else value
        t = time.time()
        if t - self.Previous >= self.Interval or self.Progress == self.Goal:
            self.Previous = t
            elp = t - self.Start
            if self.Goal > 0:  # defined goal
                rmn = elp / self.Progress * (self.Goal - self.Progress)
                msg = '{:02.2f}% {} {}'.format(self.Progress * 100.0 / self.Goal, TimeWatch.format_time(elp),
                                               TimeWatch.format_time(rmn))
            else:  # undefined goal
                msg = str(TimeWatch.format_time(elp))
            print('\r%s %s' % (msg, join(' ', *message_on_update)), end='')
            if self.Progress == self.Goal: print()


    def update(self, *message_on_update):
        self.progress(1, *message_on_update)

    @staticmethod
    def format_time(tick):
        hours, rem = divmod(tick, 3600)
        minutes, seconds = divmod(rem, 60)
        return '{:0>2}:{:0>2}:{:0>2}'.format(int(hours), int(minutes), int(seconds))


def browse_files(dir):
    return [os.path.join(root, file) for root, dirs, files in os.walk(dir) for file in files]


def open_file(file, mode='rt', encoding='utf-8'):
    '''
    An alternative to smart_open, work with gz, bz2, text, binary, with encoding
    Automatically find file within directories listed in Dirs (only need basename as input)
    '''
    if 'r' in mode:
        file = Dirs.find(file)

    open_func = open
    if file.endswith('.gz'):
        open_func = gzip.open
    elif file.endswith('.bz2'):
        open_func = bz2.open
    if 'b' in mode:
        return open_func(file, mode=mode)
    else:
        return open_func(file, mode=mode, encoding=encoding)


def save(obj, file, mode='b'):
    '''
    pickle.dump wrapper
    '''
    if isinstance(file, str):
        pickle.dump(obj, open_file(file, 'w' + mode))
    else:
        pickle.dump(obj, file)
        

def load(file, mode='b'):
    '''
    pickle.load wrapper
    '''
    if isinstance(file, str):
        file = open_file(file, 'r' + mode)
    s = os.fstat(file.fileno()).st_size
    d = []
    while file.tell() < s:
        d.append(pickle.load(file))
    file.close()
    if len(d) == 1:
        return d[0]
    else: 
        return d
       

def read_all_lines(file):
    with open_file(file, 'rt') as f:
        data = [line.strip() for line in f.readlines()]
    return data


def write_all_lines(file, list_lines):
    with open_file(file, 'wt') as f:
        for line in list_lines:
            f.write(str(line))
            f.write('\n')


def read_all_symbol_separated_file(file, sep='\t'):
    with open_file(file, 'rt') as f:
        data = [line.strip().split(sep) for line in f.readlines()]
    return data


def write_symbol_separated_file(file, list_lines, sep='\t'):
    with open_file(file, 'wt') as f:
        for line in list_lines:
            f.write(sep.join(map(str, line)))
            f.write('\n')


def chunk(l, max_parts, min_size=1):
    '''
    chunk l into maxium max_parts, each part has min size min_size
    '''
    N = len(l)
    s = max(N // max_parts, min_size)  # size of each part
    n = max(N // s, 1)
    s = N // n
    r = N % n
    p = [[] for i in range(n)]
    k = 0
    for i in range(n):
        for j in range(s + int(i < r)):
            p[i].append(l[k])
            k += 1
    return p


def peek(obj, n=1):
    '''
    Peek the first n item of a iterable object
    '''
    if isinstance(obj, dict):
        obj = obj.items()
    i = iter(obj)
    return [next(i) for j in range(n)]
        

def tokenize(s, lower=True):
    return [x for x in gensim_tokenizer(s, lowercase=lower) if  x]


def distinct(inp):
    '''
    Return distiction of inp
    '''
    inp = set('*****'.join(x) for x in inp)
    inp = [x.split('*****') for x in inp]
    return inp

