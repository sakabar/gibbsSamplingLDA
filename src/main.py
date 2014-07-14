#coding: utf-8
import sys
import lda
import random

if __name__ == '__main__':
  #文書群を読み込む
  documents = []
  for line in sys.stdin:
    line = line.rstrip("\n")
    documents.append(line.split(" "))

  #コマンドライン引数でLDAのトピック数などを決定する
  if len(sys.argv) != 5:
    sys.stderr.write("Usage: python " + sys.argv[0] + " topic_num alpha beta iterate_time\n")
    sys.stderr.write("e.g. : python "+ sys.argv[0] + " 10 1.0 1.0 10000\n")
    sys.exit(1)
  else:
    pass

  k = int(sys.argv[1])
  alpha = float(sys.argv[2])
  beta = float(sys.argv[3])
  iter_time = int(sys.argv[4])

  lda = lda.LDA(k, documents, alpha, beta, iter_time)

  #サンプリング
  lda.gibbs_sampling()

  #トピックごとに、単語の出現率が高い順に出力
  for topic_k in xrange(0, k):
    print "topic " + str(topic_k)
    for (w,p) in lda.rank_words_in_a_topic(topic_k):
      print str(w) + " : " + str(p)

    print "-----------------------"
