# Biomed2Vec
Learning Effective Distributed Representation of Complex Biomedical Concepts

# Corpus
- Step 1: run download.sh to download all raw corpora
- Step 2: run corpus.py for preprocessing
- Step 3: run detector.py for indexing concepts

# Training
- Run wordvec.py to train vectors

# Benchmark
- Run bench.py for benchmarks

# Trained vectors
- Vectors trained on all corpora. We uploaded only vectors of biomedical concepts, full term vectors is available upon request due to the large size.
    - 100-dimensional vectors
    - 200-dimensional vectors
    - 300-dimensional vectors
    - 400-dimensional vectors
    - 500-dimensional vectors
    - 1000-dimensional vectors 
    
  
- Try
  - Download (1) or (2) ((2) is more preferable because its size is smaller and vocab is limited to only biomedical concepts)
  - Load the model: 
  ```
    m = KeyedVectors.load_word2vec_format('path to .bin file', binary=True)
    m.wv.most_similar('hair_loss')
    ...
  ```
