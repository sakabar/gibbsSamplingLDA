#coding: utf-8
import sys
import random

# 多重の配列を1重の配列にする関数 flatten を使えるようにする
# flatten([1, [2,3], [4]]) => [1, 2, 3, 4]
from compiler.ast import flatten

def sampling_dist(lst):
  s = 0
  probability_density_lst = []
  for num in lst:
    s += num
    probability_density_lst.append(s)
    
  eps = 0.000001
  if (1.0 - eps <= s) and (s <= 1.0 + eps):
    pass
  else:
    print "sum is " + str(s) + ", not 1.0"
    sys.exit(1)


  #rは1未満の値を取る。probability_density_lstの末尾は1.0である
  r = random.random()
  for ind, prob_density in enumerate(probability_density_lst):
    if prob_density > r: #等号なしで正しい
      return ind
    else:
      pass

  print "Error: probability_density_lst is invalid"
  print "probability_density_lst is " + str(probability_density_lst)
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



    #トピックをランダムに割り当てる。その際、カウントをインクリメントする
    for doc_ind, doc in enumerate(documents):
      for word_ind, word in enumerate(doc):
        initial_topic = random.randint(0, k-1)
        self.word_topic_pairs[doc_ind][word_ind] = (word, initial_topic)

        #カウントの更新
        self.n_d_zi[doc_ind][initial_topic] += 1
        self.n_w_zi[word][initial_topic] += 1
        self.n_d[doc_ind] += 1
        self.n_zi[initial_topic] += 1


  def get_p_zi(self, doc_ind, word, topic_k):
    if (0 <= topic_k) and (topic_k < self.k):
      pass
    else:
      print "Error: topic numbuer is invalid"
      sys.exit(1)

    beta_nume = self.n_w_zi[word][topic_k] + self.beta_vec[word]
    beta_deno = self.n_zi[topic_k] + self.beta_sum
    
    alpha_nume = self.n_d_zi[doc_ind][topic_k] + self.alpha_vec[topic_k]
    alpha_deno = self.n_d[doc_ind] + self.alpha_sum

    return alpha_nume * beta_nume / alpha_deno / beta_deno

  def gibbs_sampling(self):
    for itr in xrange(0, self.iter_time):
      # イテレートの回数を出力
      # sys.stderr.write(str(itr) + "\n")
      for doc_ind, doc in enumerate(self.documents):
        for word_ind, word in enumerate(doc):
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
            dist.append(self.get_p_zi(doc_ind, word, topic_k))

          #正規化
          s = sum(dist)
          dist = [d / s for d in dist]

          #新しいトピックに応じて、各変数の値を更新する
          new_topic = sampling_dist(dist)
          self.word_topic_pairs[doc_ind][word_ind] =(word,  new_topic)
          self.n_d_zi[doc_ind][new_topic] += 1
          self.n_w_zi[word][new_topic] += 1
          self.n_d[doc_ind] += 1
          self.n_zi[new_topic] += 1 

  #ある単語がtopic_kである確率を返す
  def get_phy(self, word, topic_k):
    nume = self.n_w_zi[word][topic_k] + self.beta_vec[word]
    deno = self.n_zi[topic_k] + self.beta_sum

    return nume / deno

  def rank_words_in_a_topic(self, topic_k):
    lst = [(word, self.get_phy(word, topic_k)) for word in self.vocab_set]
    ans = sorted(lst, key=lambda (w,p):p, reverse=True)

    return ans[0:10]
