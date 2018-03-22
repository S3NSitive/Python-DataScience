import numpy as np
import matplotlib.pyplot as plt
import platform
import nltk
import scipy as sp
import pandas as pd
import urllib
import time

from konlpy.corpus import kobill
from PIL import Image
from konlpy.tag import Kkma
from konlpy.tag import Twitter
from konlpy.tag import Hannanum
from wordcloud import WordCloud, STOPWORDS
from matplotlib import font_manager, rc
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from bs4 import BeautifulSoup
from urllib.request import urlopen
'''
kkma = Kkma()
hannanum = Hannanum()
t = Twitter()

print(kkma.sentences('한국어 분석을 시작합니다 재미있어요~'))
print(kkma.nouns('한국어 분석을 시작합니다 재미있어요~'))
print(kkma.pos('한국어 분석을 시작합니다 재미있어요~'))

print(hannanum.nouns('한국어 분석을 시작합니다 재미있어요~'))
print(hannanum.morphs('한국어 분석을 시작합니다 재미있어요~'))
print(hannanum.pos('한국어 분석을 시작합니다 재미있어요~'))

print(t.nouns('한국어 분석을 시작합니다 재미있어요~'))
print(t.morphs('한국어 분석을 시작합니다 재미있어요~'))
print(t.pos('한국어 분석을 시작합니다 재미있어요~'))

text = open('Data/09. alice.txt').read()
alice_mask = np.array(Image.open('Data/09. alice_mask.png'))

stopwords = set(STOPWORDS)
stopwords.add("said")
'''
path = 'c:/Windows/Fonts/malgun.ttf'
if platform.system() == 'Darwin':
    rc('font', family='AppleGothic')
elif platform.system() == 'Windows':
    font_name = font_manager.FontProperties(fname=path).get_name()
    rc('font', family=font_name)
else:
    print('Unknown system')

plt.rcParams['axes.unicode.minus'] = False
'''
wc = WordCloud(background_color='white', max_words=2000,
               mask=alice_mask, stopwords=stopwords)
wc = wc.generate(text)

plt.figure(figsize=(12, 8))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.show()

files_ko = kobill.fileids()
doc_ko = kobill.open('1809890.txt').read()

t = Twitter()
tokens_ko = t.nouns(doc_ko)

ko = nltk.Text(tokens_ko, name='대한민국 국회 의안 제 1809890호')

stop_words = ['.', '(', ')', ',', "'", '%', '-', 'X', ').', '×','의','자','에','안','번',
                      '호','을','이','다','만','로','가','를']
ko = [each_word for each_word in ko if each_word not in stop_words]
ko = nltk.Text(ko, name='대한민국 국회 의안 제 1809890호')

plt.figure(figsize=(12, 6))
ko.plot(50)
plt.show()

plt.figure(figsize=(12, 6))
ko.dispersion_plot(['육아휴직', '초등학교', '공무원'])
plt.show()

data = ko.vocab().most_common(150)

# for mac : font_path='/Library/Fonts/AppleGothic.ttf'
wordcloud = WordCloud(font_path='c:/Windows/Fonts/malgun.ttf',
                      relative_scaling=0.2,
                      background_color='white',
                      ).generate_from_frequencies(dict(data))

plt.figure(figsize=(12, 6))
plt.imshow(wordcloud)
plt.axis("off")
plt.show()

train = [('i like you', 'pos'),
         ('i hate you', 'neg'),
         ('you like me', 'neg'),
         ('i like her', 'pos')]

all_words = set(word.lower() for sentence in train
                                for word in word_tokenize(sentence[0]))

t = [({word: (word in word_tokenize(x[0])) for word in all_words}, x[1]) for x in train]
for n in t:
    print(n)

classifier = nltk.NaiveBayesClassifier.train(t)
print(classifier.show_most_informative_features())

test_sentence = 'i like MeRui'
test_sent_features = {word.lower(): (word in word_tokenize(test_sentence.lower()))
                      for word in all_words}
print(test_sent_features)

print(classifier.classify(test_sent_features))

pos_tagger = Twitter()

train = [('메리가 좋아', 'pos'),
         ('고양이도 좋아', 'pos'),
         ('난 수업이 지루해', 'neg'),
         ('메리는 이쁜 고양이야', 'pos'),
         ('난 마치고 메리랑 놀거야', 'pos')]

all_words = set(word.lower() for sentence in train
                for word in word_tokenize(sentence[0]))
print(all_words)

t = [({word: (word in word_tokenize(x[0])) for word in all_words}, x[1]) for x in train]
for n in t:
    print(n)

clssifier = nltk.NaiveBayesClassifier.train(t)
print(clssifier.show_most_informative_features())

test_sentence = '난 수업이 마치면 메리랑 놀거야'
test_sent_feature = {word.lower(): (word in word_tokenize(test_sentence.lower()))
                                                    for word in all_words}

print(clssifier.classify(test_sent_feature))

def tokenize(doc):
    return ['/'.join(t) for t in pos_tagger.pos(doc, norm=True, stem=True)]

train_docs = [(tokenize(row[0]), row[1]) for row in train]
print(train_docs)

tokens = [t for d in train_docs for t in d[0]]
print(tokens)

def term_exists(doc):
    return {word: (word in set(doc)) for word in tokens}

train_xy = [(term_exists(d), c) for d, c in train_docs]
for k in train_xy:
    print(k)

clssifier = nltk.NaiveBayesClassifier.train(train_xy)

test_sentence = [('난 수업이 마치면 메리랑 놀거야')]
test_docs = pos_tagger.pos(test_sentence[0])
test_sent_feature = {word : (word in tokens) for word in test_docs}
print(clssifier.classify(test_sent_feature))

t = Twitter()
vectorizer = CountVectorizer(min_df=1)

contents = ['메리랑 놀러가고 싶지만 바쁜데 어떻하죠?',
            '메리는 공원에서 산책하고 노는 것을 싫어해요',
            '메리는 공원에서 노는 것도 싫어해요. 이상해요.',
            '먼 곳으로 여행을 떠나고 싶은데 너무 바빠서 그러질 못하고 있어요']

contents_tokens = [t.morphs(row) for row in contents]

contents_for_vectorize = []
for content in contents_tokens:
    sentence = ''
    for word in content:
        sentence = sentence + ' ' + word

    contents_for_vectorize.append(sentence)

X = vectorizer.fit_transform(contents_for_vectorize)
num_samples, num_features = X.shape
vectorizer.get_feature_names()
X.toarray().transpose()

new_post = ['메리랑 공원에서 산책하고 놀고 싶어요']
new_post_tokens = [t.morphs(row) for row in new_post]

new_post_for_vectorize = []
for new_post_content in new_post_tokens:
    new_post_sentence = ''
    for new_post_word in new_post_content:
        new_post_sentence = new_post_sentence + ' ' + new_post_word

    new_post_for_vectorize.append(new_post_sentence)

new_post_vec = vectorizer.transform(new_post_for_vectorize)

def dist_raw(v1, v2):
    delta = v1 - v2
    return np.linalg.norm(delta.toarray())

best_doc = None
best_dist = 65535
best_i = None

for i in range(0, num_samples):
    post_vec = X.getrow(i)
    d = dist_raw(post_vec, new_post_vec)

    print("== Post %i with dist=%.2f  :  %s" %(i, d, contents[i]))

    if d < best_dist:
        best_dist = d
        best_i = i

print("Best post is %i, dist = %.2f" % (best_i, best_dist))
print('-->', new_post)
print('---->', contents[best_i])

for i in range(0, len(contents)):
    print(X.getrow(i).toarray())

print('-----------------')
print(new_post_vec.toarray())

def dist_norm(v1, v2):
    v1_normalized = v1 / sp.linalg.norm(v1.toarray())
    v2_normalized = v2 / sp.linalg.norm(v2.toarray())

    delta = v1_normalized - v2_normalized

    return sp.linalg.norm(delta.toarray())

best_doc = None
best_dist = 65535
best_i = None

for i in range(0, num_samples):
    post_vec = X.getrow(i)
    d = dist_norm(post_vec, new_post_vec)

    print("== Post %i with dist=%.2f  :  %s" %(i, d, contents[i]))

    if d < best_dist:
        best_dist = d
        best_i = i

print("Best post is %i, dist = %.2f" % (best_i, best_dist))
print('-->', new_post)
print('---->', contents[best_i])

def tfidf(t, d, D):
    tf = float(d.count(t)) / sum(d.count(w) for w in set(d))
    idf = sp.log(float(len(D)) / (len([doc for doc in D if t in doc])))
    return tf, idf

a, abb, abc = ['a'], ['a', 'b', 'b'], ['a', 'b', 'c']
D = [a, abb, abc]

print(tfidf('a', a, D))
print(tfidf('b', abb, D))
print(tfidf('a', abc, D))
print(tfidf('b', abc, D))
print(tfidf('c', abc, D))

vectorizer = TfidfVectorizer(min_df=1, decode_error='ignore')

contents_tokens = [t.morphs(row) for row in contents]

contents_for_vectorize = []

for content in contents_tokens:
    sentence = ''
    for word in content:
        sentence = sentence + ' ' + word

    contents_for_vectorize.append(sentence)

X = vectorizer.fit_transform(contents_for_vectorize)
num_samples, num_features = X.shape

new_post = ['근처 공원에 메리랑 놀러가고 싶네요.']
new_post_tokens = [t.morphs(row) for row in new_post]

new_post_for_vectorize = []

for content in new_post_tokens:
    sentence = ''
    for word in content:
        sentence = sentence + ' ' + word

    new_post_for_vectorize.append(sentence)

new_post_vec = vectorizer.transform(new_post_for_vectorize)

best_doc = None
best_dist = 65535
best_i = None

for i in range(0, num_samples):
    post_vec = X.getrow(i)
    d = dist_norm(post_vec, new_post_vec)

    print("== Post %i with dist=%.2f  :  %s" %(i, d, contents[i]))

    if d < best_dist:
        best_dist = d
        best_i = i

print("Best post is %i, dist = %.2f" % (best_i, best_dist))
print('-->', new_post)
print('---->', contents[best_i])
'''
