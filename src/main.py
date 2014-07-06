#coding: utf-8
import sys
import lda
import random

if __name__ == '__main__':
  documents = []
  for line in sys.stdin:
    line = line.rstrip("\n")
    documents.append(line.split(" "))

  k = 10
  alpha = 0.5
  beta = 0.5
  lda = lda.LDA(k, documents, alpha, beta)
  lda.gibbs_sampling()

  for topic_k in xrange(0, k):
    print "topic " + str(topic_k)
    for (w,p) in lda.rank_words_in_a_topic(topic_k):
      print str(w) + " : " + str(p)

    print "-----------------------"
