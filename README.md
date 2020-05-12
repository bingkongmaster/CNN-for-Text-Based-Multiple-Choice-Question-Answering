# CS489-CNN for multiple choice question answering

Project based on paper CNN for Text-Based Multiple Choice Question Answering. Akshay Chaturvedi, Onkar Pandit and Utpal Garain. ACL 2018, [Github](https://github.com/akshay107/CNN-QA)

## Dependencies

1. Python 2.7
2. Keras v2 with Theano (v 0.9.0) backend
3. PyLucene 6.5.0 http://lucene.apache.org/pylucene/ 
4. Pickle, NLTK, numpy, json, gensim

Pylucene is needed for query expansion based paragraph selection. (Only for TQA)

## Before training

TQA dataset can be downloaded from http://data.allenai.org/tqa/. SciQ dataset can be downloaded from http://data.allenai.org/sciq/. Once downloaded, extract the folders in the data subdirectory of TQA and SciQ.

Word Vectors can be downloaded from https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit.  

Fasttext file can be downloaded from https://fasttext.cc/docs/en/english-vectors.html

Place the files in vec folder.

## Training

Run the file tqa_system.py, sciq_system.py to start training. 

## Evaluation

For TQA dataset, once the model is trained, modify tqa_system.py depending on which split you want to evaluate and then run result.py. First evaluate the trained model on train set using different thresholds. Once the threshold is fixed, evaluate the model on other splits.

For SciQ dataset, the model can be evaluated by simply modifying and running sciq_system.py since the dataset has no forbidden questions.
