# coding=utf-8

from natasha import NamesExtractor
import pymystem3
import pymorphy2
import nltk

extractor = NamesExtractor()
m = pymystem3.Mystem()
morph = pymorphy2.MorphAnalyzer()
prob_thresh = 0.4
nltk.download('punkt')

with open("names.tsv", encoding="utf-8") as file:
    for line in file:
        for word in nltk.word_tokenize(line):
            for p in morph.parse(word):
                if 'Name' in p.tag and p.score >= prob_thresh:
                    print('{:<12}\t({:>12})\tscore:\t{:0.3}'.format(word,
                                                                    p.normal_form,
                                                                    p.score))

print()
print("***********************************************")
print()

with open("names.tsv", encoding="utf-8") as file:
    for line in file:
        matches = extractor(line)
        for match in matches:
            if match.fact.first:
                print("имя:", match.fact.first)
            if match.fact.last:
                print("фамилия:", match.fact.last)

print()
print("***********************************************")
print()

with open("names.tsv", encoding="utf-8") as file:
    for line in file:
        alz = m.analyze(line)
        for x in alz:
            if 'analysis' in x:
                for y in x['analysis']:
                    if ',фам' in y['gr']:
                        print("фамилия:", y['lex'])
                    if ',имя' in y['gr']:
                        print("имя:", y['lex'])
