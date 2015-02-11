# This script takes the .csv training data and labels
# test data with p_buy = {0,1}. 
# The data is given as 8 sequential pairs of site - time spent (s)
# followed by a 0 (no buy) or 1 (buy)

#strategies:

# 1. Plot total time spent vs. p_buy and come up with rough rule

# 2a. for each page compute p(b|p) = prob buy given page in history
# then compute p(b|p') = prob buy given page ensemble

# 2b. compute p(b|p-p-p) = prob buy given page-page-page pattern

# 2a and 2b are implemented in the Strat2.py script - this one implements
# strategy 1.

import pylab
import operator
import sys
from random import random

# ingest the data
data = []
with open('train.csv') as f:
    for line in f:
        words = line.split(',')
        struct = []
        for i in range (0,8):
            struct.append((words[i*2], int(words[i*2+1]))) # (page, time)
        struct.append(bool(int(words[-1].rstrip())))
        data.append(struct)
# data is in format: 
# [[(page, time), (page, time), ... (buy/no_buy)], [(page,time),...]]  
# yum!


#Strategy 1 - total time spent:
tot_times = {}
for line in data:
    tot_time = 0 #time so far
    for page in line[:-1]:
        tot_time += page[1]
    if tot_time in tot_times: # record how total times correlate with buy / no buy
        if line[-1]: tot_times[tot_time][True] += 1 #buy
        else: tot_times[tot_time][False] += 1  #no buy
    else:
        tot_times[tot_time] = {True : 0, False : 0}
        tot_times[tot_time][line[-1]] += 1

# compute the overall average buy probability for later use
p_buy_sum = 0
max_time = 0
for time in tot_times:
    if (tot_times[time][False] or tot_times[time][True]):
        p_buy_sum += tot_times[time][True] / float(( tot_times[time][False] + tot_times[time][True] ))
    if (time > max_time):
        max_time = time
p_buy = p_buy_sum / len(tot_times)
# p_buy = 0.23365578

# bin the data to make analysis easier
bin_size = 50
binned = []
for j in range (0,1+(max_time/ bin_size)):
    binned.append([j,0,0])
for time in tot_times:
    binned[time/bin_size][1] += tot_times[time][True] 
    binned[time/bin_size][2] += tot_times[time][False] 

#generate the plot
#with open('tmp1', 'w') as plot:
#    for time in tot_times:
#        plot.write("%s %s %s \n" % (time, tot_times[time][True], tot_times[time][False]))
with open('tmp3', 'w') as plot:
    for time in binned:
        plot.write("%s %s %s \n" % (time[0], time[1], time[2]))
#data1 = pylab.loadtxt('tmp1')
data3 = pylab.loadtxt('tmp3')
#pylab.plot(data1[:,0], data1[:,1], label = 'Buy', marker='o', color='b')
#pylab.plot(data1[:,0], -1*data1[:,2], label = 'NoBuy', marker='o', color='r')
#pylab.plot(data1[:,0], data1[:,1] - data1[:,2], label = 'Diff', marker='x', color='g')
#pylab.plot(data1[:,0], data1[:,1]/(data1[:,1] + data1[:,2]) - p_buy, label = 'Prob_buy', marker='o', color='k', linestyle = '')
#pylab.plot(data1[:,0], data1[:,1]/(data1[:,1] + data1[:,2]), label = 'Prob_buy', marker='o', color='k', linestyle = '')
pylab.plot(data3[:,0], data3[:,1]/(data3[:,1] + data3[:,2]), label = 'Prob_buy_binned', marker='o', color='g', linestyle = '')
pylab.plot([0, 300], [p_buy, p_buy], color='k', linestyle='-', linewidth=2, label = 'Overall average')
pylab.axis([0, 300, -0.5, 1])
pylab.ylabel('Prob_buy')
pylab.xlabel('Total time (s*%s) spent on website (first 8 links) ' % bin_size)
pylab.legend()
# uncomment the line below to show the plot
pylab.show()

# The preliminary analysis indicates that users with session total time (first 8 pages) 
#between 150 and 3750 seconds are ~10% more likely to buy than the overall average  
# A crude classifier computes session total time and: 
# 1. if the total session time is between 150 and 3750 s, p_buy = 0.35
# 2. else, p_buy = 0.23 

if len(sys.argv) > 1:  # The syntax is : # <script> <test> <marked_test>
    out = open(sys.argv[2], 'w')
    with open(sys.argv[1], 'r') as test:
        for line in test:
            words = line.split(',')
            tot_time = 0 
            for i in range (0,8):
                tot_time += int(words[i*2 + 1])
            if tot_time > 150 and tot_time < 3750: 
                out.write(line[:-3]+',0.3536\n') #buy
            else:
                out.write(line[:-3]+',0.2336\n') #no buy
