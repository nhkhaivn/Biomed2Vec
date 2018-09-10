# Biomed2Vec
We focused on training effective representations for biomedical concepts including complex ones with multiple tokens. 
We used an efficient technique to index all possible concepts of UMLS in a corpus of 15,4 billion tokens.
We can obtain the vector representations for more than 650,000 concepts (with minimum frequency is 10). 

# Quick try
- Download pub_wikipedia_500.bin (trained on Merge corpus, d=500, size=1.22GB)
- Load the model: 
  ```
    m = KeyedVectors.load_word2vec_format('path to pub_wikipedia_500.bin', binary=True)
    m.wv.most_similar('hair_loss')
    ...
  ```

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

# Resources
- Download resources from [this link](https://drive.google.com/drive/folders/1EvyJqJhwQKUgf0mme1qztO72rQs-ZvQm)
    
# Training
- Run train.py to train vectors

# Benchmark
- Run bench.py for benchmarks
for benchmarks

# Pre-trained models
- There are two versions for each model: 
    - Full model with all terms (accessible upon [request](mailto:nhkhai@nii.ac.jp) due to the large size)
    - [Limited model with only biomedical concepts](https://drive.google.com/drive/folders/1VFwaXcBN2fy_fz6Ip68ynfrZMxgJvtgE)
 
