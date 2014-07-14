#coding: utf-8
import sys
import random
from compiler.ast import flatten

def sampling_dist(lst):
  s = 0
  p_lst = []
  for num in lst:
    s += num
    p_lst.append(s)
    
  eps = 0.000001
  if (1.0 - eps <= s) and (s <= 1.0 + eps):
    pass
  else:
    print "sum is " + str(s)
    sys.exit(1)


  r = random.random()
  for ind, num in enumerate(p_lst):
    if num > r:
      return ind
    else:
      pass

  print "Error: line26"
  sys.exit(1)


class LDA:
  def __init__(self, k, documents, alpha, beta, iter_time):
    self.k = k
    self.documents = documents
    self.iter_time = iter_time

    #語彙の集合(重複なし)
    self.vocab_set = set(flatten(documents))

    self.alpha_vec = [alpha for x in xrange(0,k)]
    self.alpha_sum = sum(self.alpha_vec)
    # self.beta_vec = [beta for x in xrange(0,len(self.vocab_set))]
    self.beta_sum = 0
    self.beta_vec = {}
    for w in self.vocab_set:
      self.beta_vec[w] = beta
      self.beta_sum += beta

    #n_d_zi[doc_ind][k]
    #文書dの中でトピック番号kが推定された回数
    #文書dごとに定義される
    #まず0で初期化して、トピックを乱数で初期化する際に同時に更新する
    self.n_d_zi = []
    for doc_ind, doc in enumerate(documents):
      self.n_d_zi.append([0 for i in xrange(0,k)])

    #n_w_zi[word][k]
    #単語wordにトピックkが推定された回数
    #文書群全体で定義される
    self.n_w_zi = {}
    for word in self.vocab_set:
      self.n_w_zi[word] = [0 for i in xrange(0,k)]
        
    #word_topic_pair[doc_ind][word_ind]
    #doc中のwordとトピック番号のペア
    #まずは0に初期化
    self.word_topic_pairs = []
    for doc in documents:
      self.word_topic_pairs.append([0 for word in doc])

    #n_d[doc_ind]
    #doc_ind中のトピックの数
    self.n_d = [0 for doc_ind in xrange(0, len(documents))]

    #n_zi[k]        
    #トピックkが推定された回数
    self.n_zi = [0 for x in xrange(0, self.k)]


    for doc_ind, doc in enumerate(documents):
      for word_ind, word in enumerate(doc):
        initial_topic = random.randint(0,k-1)
        self.word_topic_pairs[doc_ind][word_ind] = (word, initial_topic)

        #カウントの更新
        self.n_d_zi[doc_ind][initial_topic] += 1
        self.n_w_zi[word][initial_topic] += 1
        self.n_d[doc_ind] += 1
        self.n_zi[initial_topic] += 1

    #DEBUG
    # for doc_ind, _ in enumerate(documents):
    #   for initial_topic in xrange(0,k):
    #     print self.n_d_zi[doc_ind][initial_topic]

    #DEBUG
    # for word in self.vocab_set:
    #   for initial_topic in xrange(0,k):
    #     print self.n_w_zi[word][initial_topic]

  def get_probability(self, doc_ind, word, topic_k):
    if (0 <= topic_k) and (topic_k < self.k):
      pass
    else:
      print "line85"
      sys.exit(1)

    beta_nume = self.n_w_zi[word][topic_k] + self.beta_vec[word]
    beta_deno = self.n_zi[topic_k] + self.beta_sum
    
    alpha_nume = self.n_d_zi[doc_ind][topic_k] + self.alpha_vec[topic_k]
    alpha_deno = self.n_d[doc_ind] + self.alpha_sum

    return alpha_nume * beta_nume / alpha_deno / beta_deno

  def gibbs_sampling(self):
    for itr in xrange(0, self.iter_time):
      # sys.stderr.write(str(itr) + "\n")
      for doc_ind, doc in enumerate(self.documents):
        # sys.stderr.write(str(itr) + " " + str(doc_ind) + "\n")
        for word_ind, word in enumerate(doc):
          # print str(doc_ind) + " " + word
          w_t_pair = self.word_topic_pairs[doc_ind][word_ind]
          word = w_t_pair[0]
          old_topic = w_t_pair[1]

          #現在のz_iに対応するカウントをデクリメント
          self.n_d_zi[doc_ind][old_topic] -= 1
          self.n_w_zi[word][old_topic] -= 1
          self.n_d[doc_ind] -= 1
          self.n_zi[old_topic] -= 1

          #サンプリングのための分布を計算
          dist = []
          for topic_k in xrange(0, self.k):
            dist.append(self.get_probability(doc_ind, word, topic_k))

          s = sum(dist)
          dist = [d / s for d in dist]

          #新しいトピックに応じて、各変数の値を更新する
          new_topic = sampling_dist(dist)
          self.word_topic_pairs[doc_ind][word_ind] =(word,  new_topic)
          self.n_d_zi[doc_ind][new_topic] += 1
          self.n_w_zi[word][new_topic] += 1
          self.n_d[doc_ind] += 1
          self.n_zi[new_topic] += 1 

  def get_phy(self, word, topic_k):
    nume = self.n_w_zi[word][topic_k] + self.beta_vec[word]
    deno = self.n_zi[topic_k] + self.beta_sum

    return nume / deno

  def rank_words_in_a_topic(self, topic_k):
    lst = [(word, self.get_phy(word, topic_k)) for word in self.vocab_set]
    ans = sorted(lst, key=lambda (w,p):p, reverse=True)
    # print sum([p for (w,p) in ans])

    return ans[0:10]
      
