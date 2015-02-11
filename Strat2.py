# This script takes the .csv training data and labels
# test data with p_buy = {0,1}.
# The data is given as 8 sequential pairs of site - time spent (s)
# followed by a 0 (no buy) or 1 (buy)

#strategies:

# 1. Plot total time spent vs. p_buy and come up with rough rule

# 2a. for each page compute p(b|p) = prob buy given page in history
# then compute p(b|p') = prob buy given page ensemble

# 2b. compute p(b|p-p-p) = prob buy given page-page-page pattern

# 2a and 2b are implemented in this script - Strat1.py implements
# strategy 1.

import pylab
import operator
import sys
from math import log, exp
from random import random

#ingest the data
data = []
with open('train.csv') as f:
    for line in f:
        words = line.split(',')
        struct = []
        for i in range (0,8):
            struct.append((words[i*2], int(words[i*2+1]))) # (page, time)
        struct.append(bool(int(words[-1].rstrip())))
        data.append(struct)
#data is in format [[(page, time), (page, time), ... (buy/no_buy)], [(page,time),...]]

# Strategy 2 Naive Bayes
# This strategy ignores time spent and assumes no correlation between pages
# or page sequences in the user path. This is probably not true, for instance it would be
# unusual to see CART before SKU, but we'll see how it does.

# Bayes Theorem:
# p(buy|p_i) = p(p_i|buy) * p(buy) / ( p(p_i|buy) * p(buy) + p(p_i|no_buy) * p(no_buy))
# p(buy|p_i) = p(p_i|buy) * p(buy) / p(p_i)

# p(p_i|buy) = N(p_i, buy) / N(buy)
# p(buy) = N(buy) / N(tot)
# p(p_i|no_buy) = N(p_i, no_buy) / N(no_buy) = N(p_i, no_buy) / (1-N(buy))
# p(no_buy) = N(no_buy) / N(tot) = (1-N(buy))/N(tot)
# p(p_i) = N(p_i) / N(tot)

# p(buy|p_i) = N(p_i, buy) / N(buy) * N(buy)/N(tot) / ( N(p_i) / N(tot))
#            = N(p_i, buy) / N(tot) / (N(p_i) / N(tot)
#            = N(p_i, buy) / N(p_i)
# p(buy|p_i) = N(p_i, buy) / N(buy) * N(buy)/N(tot) / [ N(p_i, buy)/N(buy) * N(buy)/N(tot) + N(p_i, no_buy) / (1-N(buy) * (1-N(buy))/N(tot) ]
#            = N(p_i, buy) / N(tot) / [ N(p_i, buy) / N(tot) + N(p_i, no_buy) / N(tot) ]
#            = N(p_i, buy) / N(p_i)

# Naive Bayes combination:
# p(buy|p) = Pi_i(p_i) / [Pi_i(p_i) + Pi_i(1-p_i)]

# so to compute p(buy|P) we need to compute the p_i for each webpage, i, in the path.
# P is the vector of pages visited (in any order).
# this means counting the N(p_i, buy) for each i and the N(p_i)

counts = {}  # tally up how many buys there are for each page type (SKU, CART, etc).
for path in data:
    for page in path[:-1]:
        if page[0] not in counts:
            counts[page[0]] = {}
            counts[page[0]]['occur'] = 1
            counts[page[0]]['buy'] = 0
            if path[8]:
                counts[page[0]]['buy'] = 1
        else:
            counts[page[0]]['occur'] += 1
            if path[8]:
                counts[page[0]]['buy'] += 1

for page in counts:
    counts[page]['ratio'] = float(counts[page]['buy'])/counts[page]['occur']

labels = counts.keys()
stats = counts.values()
ratio = []
for page in stats:
    ratio.append(float(page['buy'])/page['occur'])
pylab.bar(range(len(counts)), ratio, align='center')
pylab.xticks(range(len(counts)), labels, size='small')
pylab.ylabel('prob( buy | page )')
#pylab.show()
# uncomment the line above to show the probability of buy, given that the page
# of the given type appears in the user path.

# At this point it is clear which pages (irrespective of order in the path) contribute
# most to buying - CART and HOME, followed by ACCOUNT, OTHER_PAGE, and SKU. Kind of
# surprising to see HOME up there - maybe this has something to do with human vs. bot
# traffic? Maybe bots aren't going to HOME as much as humans?

# run on the test data and label if input file provided
if len(sys.argv) > 1: #syntax is: <script> <test> <out2a> <out2b>
    out = open(sys.argv[2], 'w')
    with open(sys.argv[1], 'r') as test:
        for line in test:
            words = line.split(',')
            P = 1
            for i in range (0,8):
                page = words[i*2].rstrip()
                p_i = float(counts[page]['ratio'])
                P_num = 1
                P_denom = 1
                if p_i > 0 and p_i <= 1:  #just use straight product, not log sum for now
                    P_num = P_num * p_i
                    P_denom = P_denom*(1-p_i)
                else:
                    print ('badly formed probability for page %s' % page)
            prob = str(P_num  / (P_num + P_denom))
            out.write(line[:-3]+','+prob+'\n') #buy

# Now lets consider sequences of up to 3 page hops as independent features
# This means we will compute the probability of a buy given a sequence
# S_ijk = page_i --> page_j --> page_k
# This is chosen because of the intuition that the appearance of certain
# sequences of moves may be indicative of user purchase intent.
# Other length sequences could be evaluated (2, 4, etc.) but since there
# are 9 page categories and about ~100K training data entries, using sequences
# of 3 means there will be 9*9*9 possible sequences and (very roughly)
# 1000 samples per sequence. In fact ~ 1/2 the possible sequences appear in the
# training data, so this is good.

# This approach assumes the probability of appearance of two sequences is independent.
# which is obviously untrue - if 'abc' is in the path, then the probability of bcx is
# probably greater than normal. This could be accomodated with a more sophisticated
# computation of the relevant probabilities.

seqs = {}
for path in data:
    i = 0
    for i in range(0, len(path[:-3])):
        seq = path[i][0]+path[i+1][0]+path[i+2][0]
        if seq not in seqs:
            seqs[seq] = {}
            seqs[seq]['occur'] = 1
            seqs[seq]['buy'] = 0
            if path[8]:
                seqs[seq]['buy'] = 1
        else:
            seqs[seq]['occur'] += 1
            if path[8]:
                seqs[seq]['buy'] += 1

for seq in seqs:
    seqs[seq]['ratio'] = float(seqs[seq]['buy'])/seqs[seq]['occur']

# use the data to predict
if len(sys.argv) > 3:  #syntax is <script> <test> <out2a> <out2b>
    out = open(sys.argv[3], 'w')
    with open(sys.argv[1], 'r') as test:
        for line in test:
            words = line.split(',')
            P = 1
            for i in range (0,6):
                seq = words[i*2].rstrip() + \
                      words[i*2+2].rstrip() + \
                      words[i*2+4].rstrip()
                # for p_i use 0.23365... if either the sequence is missing OR the ratio is missing
                p_i = float(seqs.get(seq,{}).get('ratio', 0.23365578)) or 0.23365578
                P_num = 1
                P_denom = 1
                if p_i > 0 and p_i <= 1:
                    P_num = P_num * p_i
                    P_denom = P_denom*(1-p_i)
                else:
                    print ('badly formed probability for page sequence %s is %s' % (seq, p_i))
            prob = str(P_num  / (P_num + P_denom))
            out.write(line[:-3]+','+prob+'\n')
