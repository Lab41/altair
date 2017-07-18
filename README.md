# Altair
<img src="assets/altair_logo.png" width=500 height=300 alt="altair logo" />

## Assessing Source Code Similarity with Unsupervised Learning

How do you determine what a segment of source code does?

How do you search a corpus for source code that you want to use?

Altair is Lab41's exploration of representing source code and its associated features in a vector space. We are interested in generating robust source code embeddings for Python like [Word2Vec](https://code.google.com/archive/p/word2vec/) creates word embeddings for written text. You can read about our early experimentation with word embeddings for source code on the Lab41 [blog](https://gab41.lab41.org/python2vec-word-embeddings-for-source-code-3d14d030fe8f#.c6zmcq8be).

Our primary use case of source code representation and similarity calculation is enabling meaningful recommendations of code to coders. We believe that similar techniques could be useful for code security analysis, code authorship, and code plaigarism detection.

## Prerequisites

Local Computing Components
* git
* python3
* pip
* conda

## Installation

##### Cloning the repository

Clone Altair repository from the command line, then cd into the directory
```
git clone https://github.com/Lab41/altair.git
cd altair
```

##### Conda

Anaconda is a completely free Python distribution. It includes more than 400 of the most popular Python packages for science, math, engineering, and data analysis. Anaconda includes conda, a cross-platform package manager and environment manager and seen by some as the successor to pip.

Before getting started, you’ll need both conda and gcc installed on your system. Download the Anaconda version for Python3+ by entering the following (as of Feb 2017) on a Linux command line:
```
wget https://repo.continuum.io/archive/Anaconda3-4.3.0-Linux-x86_64.sh
bash Anaconda3-4.3.0-Linux-x86_64.sh
```

Once that’s done, you can create an new environment on your system by calling:
```
conda env create -f environment.yml
```

Note: If the conda command is not found, start a new shell to refresh your path.

After it finishes, you should have a new conda environment named altair containing all of the dependencies. Activate it by calling
```
source activate altair
```
Check out the preprocessing [README.md](altair/preprocess00/README.md) to find out where you can obtain our training and testing data.

## Notes

Per [Gensim] (http://radimrehurek.com/gensim/models/doc2vec.html), reproducibility between interpreter launches requires use of the PYTHONHASHSEED environment variable to control hash randomization in Python 3.
