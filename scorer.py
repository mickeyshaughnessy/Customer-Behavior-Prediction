import sys
import difflib
import pylab

with open(sys.argv[2], 'r') as data:
    dat1 = data.readlines()
with open(sys.argv[3], 'r') as data2:
    dat2a= data2.readlines()
with open(sys.argv[4], 'r') as data3:
    dat2b= data3.readlines()
with open(sys.argv[1], 'r') as test_in:
    test = test_in.readlines()

total_scores = {'strat1_prec' : [], 'strat2a_prec' : [], 'strat2b_prec' : [] \
            ,'strat1_rec' : [], 'strat2a_rec' : [], 'strat2b_rec' : []} 
                


for i in range(0,101):
    threshold = i / 100.0
    print ('scoring threshold = %s' % threshold)
    scores = [[0,0,0],[0,0,0],[0,0,0]] # [A, B, C] for each strategy
    # A = Number of true positives: 1_test = 1_predicted
    # B = Number of false negatives: 1_test = 0_predicted
    # C = Number of false positives: 0_test = 1_predicted 
    # Prec = A / (A+C)
    # Recall = A / (A+B)
    for j in range(0,len(test)):
        test_words = test[j].split(',')
        dat1_words = dat1[j].split(',')
        dat2a_words = dat2a[j].split(',')
        dat2b_words = dat2b[j].split(',')
        target = int(test_words[-1])
        strat1 = 1 if float(dat1_words[-1]) > threshold else 0
        strat2a = 1 if float(dat2a_words[-1]) > threshold else 0
        strat2b = 1 if float(dat2b_words[-1]) > threshold else 0
        if target == 1:
            print ('target : %s predicts : %s %s %s' % (target, strat1, strat2a, strat2b))
            if strat1 == 1: scores[0][0] += 1
            else: scores[0][1] += 1
            if strat2a == 1: scores[1][0] += 1
            else: scores[1][1] += 1
            if strat2b == 1: scores[2][0] += 1
            else: scores[2][1] += 1
        else:
            if strat1 == 1: scores[0][2] += 1
            if strat2a == 1: scores[1][2] += 1
            if strat2b == 1: scores[2][2] += 1
    total_scores.get('strat1_prec').append(float(scores[0][0]) / (scores[0][0] + scores[0][2] or 1))    
    total_scores.get('strat2a_prec').append(float(scores[1][0]) / (scores[1][0] + scores[1][2] or 1))    
    total_scores.get('strat2b_prec').append(float(scores[2][0]) / (scores[2][0] + scores[2][2] or 1))    
    total_scores.get('strat1_rec').append(float(scores[0][0]) / (scores[0][0] + scores[0][1] or 1))    
    total_scores.get('strat2a_rec').append(float(scores[1][0]) / (scores[1][0] + scores[1][1] or 1))    
    total_scores.get('strat2b_rec').append(float(scores[2][0]) / (scores[2][0] + scores[2][1] or 1))    
            
#pylab.scatter(total_scores('strat1_prec'), total_scores('strat1_rec'), s=area, c=colors, alpha=0.5)
pylab.scatter(total_scores['strat1_prec'][:], total_scores['strat1_rec'][:], c = 'b',\
            label = 'Strat1')
#                 s = [20*2**n for n in range(21)])
#                 s = [80*2 for n in range(21)], label = 'Strat1')
pylab.scatter(total_scores['strat2a_prec'][:], total_scores['strat2a_rec'][:], c = 'g', label = 'Strat2a')
pylab.scatter(total_scores['strat2b_prec'][:], total_scores['strat2b_rec'][:], c = 'r', label = 'Strat2b')
pylab.xlabel('Precision')
pylab.ylabel('Recall')
pylab.legend()
pylab.show()

print total_scores
#print('number right : %s, number wrong : %s' % (score, len(test)-score)) 
