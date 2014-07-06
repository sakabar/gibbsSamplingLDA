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

  print "line26"
  sys.exit(1)


class LDA:
  def __init__(self, k, documents, alpha, beta):
    self.k = k
    self.documents = documents

    self.alpha_vec = [alpha for x in xrange(0,k)]
    self.beta_vec = [beta for x in xrange(0,k)]

    #語彙の集合(重複なし)
    self.vocab_set = set(flatten(documents))

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
        
    for doc_ind, doc in enumerate(documents):
      for word_ind, word in enumerate(doc):
        topic_k = random.randint(0,k-1)
        self.word_topic_pairs[doc_ind][word_ind] = (word, topic_k)

        #カウントの更新
        self.n_d_zi[doc_ind][topic_k] += 1
        self.n_w_zi[word][topic_k] += 1

    #DEBUG
    # for doc_ind, _ in enumerate(documents):
    #   for topic_k in xrange(0,k):
    #     print self.n_d_zi[doc_ind][topic_k]

    #DEBUG
    # for word in self.vocab_set:
    #   for topic_k in xrange(0,k):
    #     print self.n_w_zi[word][topic_k]

  def get_probability(self, doc_ind, word, topic_k):
    if (0 <= topic_k) and (topic_k < self.k):
      pass
    else:
      print "line85"
      sys.exit(1)

    beta_nume = self.n_w_zi[word][topic_k] + self.beta_vec[topic_k]
    beta_deno = sum([self.n_w_zi[w][topic_k] for w in self.vocab_set]) + sum(self.beta_vec)
    
    alpha_nume = self.n_d_zi[doc_ind][topic_k] + self.alpha_vec[topic_k]
    alpha_deno = sum([self.n_d_zi[doc_ind][t] for t in xrange(0, self.k)]) + sum(self.alpha_vec)

    return alpha_nume * beta_nume / alpha_deno / beta_deno

  def gibbs_sampling(self):
    iter_times = 10

    for itr in xrange(0,iter_times):
      # print "iter: " + str(itr)
      for doc_ind, doc in enumerate(self.documents):
        for word_ind, word in enumerate(doc):
          # print str(doc_ind) + " " + word
          w_t_pair = self.word_topic_pairs[doc_ind][word_ind]
          word = w_t_pair[0]
          old_topic = w_t_pair[1]

          #現在のz_iに対応するカウントをデクリメント
          self.n_d_zi[doc_ind][old_topic] -= 1
          self.n_w_zi[word][old_topic] -= 1

          #サンプリングのための分布を計算
          dist = []
          for topic_k in xrange(0, self.k):
            dist.append(self.get_probability(doc_ind, word, topic_k))

          s = sum(dist)
          dist = [d / s for d in dist]

          new_topic = sampling_dist(dist)
          self.n_d_zi[doc_ind][new_topic] += 1
          self.n_w_zi[word][new_topic] += 1

  def get_phy(self, word, topic_k):
    nume = self.n_w_zi[word][topic_k] + self.beta_vec[topic_k]
    deno = sum([self.n_w_zi[w][topic_k] for w in self.vocab_set]) + sum(self.beta_vec)

    return nume / deno

  def rank_words_in_a_topic(self, topic_k):
    lst = [(word, self.get_phy(word, topic_k)) for word in self.vocab_set]
    ans = sorted(lst, key=lambda (w,p):p, reverse=True)

    return ans[0:10]
      
