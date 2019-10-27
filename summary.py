# adapated from https://medium.com/jatana/unsupervised-text-summarization-using-sentence-embeddings-adb15ce83db1

import numpy as np
from nltk.tokenize import sent_tokenize
from skipthoughts import skipthoughts
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
# ***************************************************************************

def split_sentences(all_para):
    """
    Splits the paragraphs into individual sentences
    """
    n_para = len(all_para)
    for i in range(n_para):
        para = all_para[i]
        sentences = sent_tokenize(para)
        for j in reversed(range(len(sentences))):
            sent = sentences[j]
            sentences[j] = sent.strip()
            if sent == '':
                sentences.pop(j)
        all_para[i] = sentences


def skipthought_encode(emails):
    """
    Obtains sentence embeddings for each sentence in the paragraph
    """
    enc_emails = [None]*len(emails)
    cum_sum_sentences = [0]
    sent_count = 0
    for email in emails:
        sent_count += len(email)
        cum_sum_sentences.append(sent_count)

    all_sentences = [sent for email in emails for sent in email]
    print('Loading pre-trained models...')
    model = skipthoughts.load_model()
    encoder = skipthoughts.Encoder(model)
    print('Encoding sentences...')
    enc_sentences = encoder.encode(all_sentences, verbose=False)

    for i in range(len(emails)):
        begin = cum_sum_sentences[i]
        end = cum_sum_sentences[i+1]
        enc_emails[i] = enc_sentences[begin:end]
    return enc_emails


def summarize(all_para):
    """
    Performs summarization of paragraphs
    """
    n_para = len(all_para)
    summary = [None]*n_para
    print('Preprecesing...')
    # preprocess(emails)
    print('Splitting into sentences...')
    split_sentences(all_para)
    print(all_para)
    print('Starting to encode...')
    enc_all_paras = skipthought_encode(all_para)
    print('Encoding Finished')
    for i in range(n_para):
        enc_para = enc_all_paras[i]
        n_clusters = int(np.ceil(len(enc_para)**0.5))
        kmeans = KMeans(n_clusters=n_clusters, random_state=0)
        kmeans = kmeans.fit(enc_para)
        avg = []
        closest = []
        for j in range(n_clusters):
            idx = np.where(kmeans.labels_ == j)[0]
            avg.append(np.mean(idx))
        closest, _ = pairwise_distances_argmin_min(kmeans.cluster_centers_,\
                                                   enc_para)
        ordering = sorted(range(n_clusters), key=lambda k: avg[k])
        summary[i] = ' '.join([all_para[i][closest[idx]] for idx in ordering])
    print('Clustering Finished')
    return summary
