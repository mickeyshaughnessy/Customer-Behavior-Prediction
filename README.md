# Customer-Behavior-Prediction
These scripts are used to predict wether a website customer will make a purchase based on their browsing history

This directory contains the data files, scripts, outputs and plots. 

There are three learning strategies - one (1) based simply on total time the 
user spends on the webpage; the other two based on a Naive Bayes classifier
approach, using either the individual pages (2a) visited or the sequences of 3 
pages (2b) visited.

Strategy 2b has the greatest area under the precision - recall curve, so this one is the
best of the three. Its results marking the test.csv data are in predict2b.dat. 

The files `predict*` are generated using the indicated strategies, marking the final 
element of each line with a number between 0 and 1. This number represents the predicted 
probability of buy : 1 is a certain buy, 0 is a certain no buy. To convert to a binary 
classification, simply select a threshold between 0 and 1. Then mark the lines with p_buy 
greater than the threshold as a buy and those less as a no-buy. Note that different choices
of threshold will correpond to different amounts of false positives, false negatives,
true negatives, and true positives. A higher threshold will produce fewer false positives but
more false negatives. The overall p_buy in the training data is ~0.23. A threshold of ~0.4
is suggested. 

The `scorer.py` script is used to evaluate the strategies, by training against either half or all 
the training data and then evaulating the perfomrance of each strategy using either the other half
of the training data or all the training data as the source of truth. 
-----------
The `*.png` files are the plots generated to analyze the training data and understand
the performance of the strategies. 

See comments in the Strat1.py and Strat2.py scripts for more information about the 
method, assumptions, and intermediate results. 

