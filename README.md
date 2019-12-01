# autoIOC
CS6332 System Security Project 19F: automated IOC processing

## Summarizer setup
This assumes you already have python2 installed.

1. Install Conda for python2: https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html
2. Create a new environment: `conda create --name autoIOC --file conda-req.txt`
3. Activate environment: `conda activate autoIOC`
4. Install skip-thoughts in this directory: `git clone https://github.com/ryankiros/skip-thoughts.git`
- Project website: https://pypi.org/project/skip-thoughts/
5. Obtain the pre-trained models:
```
mkdir skip-thoughts/models
wget -P ./skip-thoughts/models http://www.cs.toronto.edu/~rkiros/models/dictionary.txt
wget -P ./skip-thoughts/models http://www.cs.toronto.edu/~rkiros/models/utable.npy
wget -P ./skip-thoughts/models http://www.cs.toronto.edu/~rkiros/models/btable.npy
wget -P ./skip-thoughts/models http://www.cs.toronto.edu/~rkiros/models/uni_skip.npz
wget -P ./skip-thoughts/models http://www.cs.toronto.edu/~rkiros/models/uni_skip.npz.pkl
wget -P ./skip-thoughts/models http://www.cs.toronto.edu/~rkiros/models/bi_skip.npz
wget -P ./skip-thoughts/models http://www.cs.toronto.edu/~rkiros/models/bi_skip.npz.pkl
```
6. Update lines 23-24 of skip-thoughts/skipthoughts.py to provide the right paths to the models above

## Running summarizer
Currently, use `runner.py` to summarize your text. It loads the text into an array, and passes it `summary.py`.
You must activate the Conda environment first.

TODO: update `runner.py`

Usage: `python runner.py`

## Text cleaner setup
This assumes you already have python3.6 installed.

1. Deactivate Conda: `conda deactivate`
2. Create a pip environment: `python3.6 -m venv cleaner`
3. Activate environment: `source cleaner/bin/activate`
4. Install dependencies: `pip install -r pip-cleaner-req.txt`

## Running text cleaner
Activate the pip environment, and run `python textcleaner.py <pdf file> <toc>`
where `<toc>` is the page number of the table of contents. This refers to the physical page number in the file.
