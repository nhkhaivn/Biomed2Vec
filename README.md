# Biomed2Vec
Learning Effective Distributed Representation of Complex Biomedical Concepts
(Source code is available after a publication. However, now you can download pre-trained models)

# Corpus
- Step 1: run download.sh to download all raw corpora
- Step 2: run corpus.py for preprocessing
- Step 3: run detector.py for indexing concepts
- Summary (as of April 2018)

    | Corpus        |Tokens         | Distinct biomedical concepts|
    | ------------- | ------------- | ------------- |
    | Wikipedia     | 2,374,659,439 | 655,187       |
    | Pubmed        |3,125,953,041  | 979,601       |
    | PMC           |9,895,775,276  | 990,897       |
    | Merge         |15,396,387,756 | 1,359,860     |
    
# Training
- Run wordvec.py to train vectors

# Benchmark
- Run bench.py for benchmarks

# Pre-trained models
- There are two versions for each model: 
    - [Full model with all terms](mailto:nhkhai@nii.ac.jp) (accessible upon request due to the large size)
    - [Limited model with only biomedical concepts](https://drive.google.com/drive/folders/1VFwaXcBN2fy_fz6Ip68ynfrZMxgJvtgE)
 
# Try
- Download pub_wikipedia_500.bin (trained on Merge corpus, d=500)
- Load the model: 
  ```
    m = KeyedVectors.load_word2vec_format('path to pub_wikipedia_500.bin', binary=True)
    m.wv.most_similar('hair_loss')
    ...
  ```
