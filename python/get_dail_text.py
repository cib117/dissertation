# -*- coding: utf-8 -*-

# Import the required libraries
import re
import glob
import json
import unicodedata

# Function to extract date from document filename
def get_day(filename):
    day = re.search(r'\d{8}', filename).group(0)
    return int(day)

# Function to prepare text for analysis
def clean_text(t):
    t = unicodedata.normalize('NFD', t).encode('ascii', 'ignore') ## normalize unicode accents etc
    t = re.sub('&rsquo;|&rdquo;', '\'', t) ## replace certain characters with quote mark
    t = re.sub('&mdash;', '-', t) ## replace dash
    t = re.sub('&quot;', ' ', t) ## replace quotation 
    t = re.sub(r'http\S+"=', ' ',t) ## delete any links
    t = re.sub(r'\d+', ' ', t) ## delete numbers
    t = re.sub('[^a-zA-Z \']', ' ', t) ## only keep letters, ', and - characters
    t = t.lower() ## lower case everything
    t = ' '.join(t.split()) ## remove extra spaces
    return t
    

questions = []
speeches = []
qsdetails = []
spdetails = []
for doc in glob.glob('json/*.jsonl'):
    print doc
    date = get_day(doc)
    if date > 20110308 and date < 20160309:
        print "Processing text"
        with open(doc, 'r') as f:
            for line in f:
                dic = json.loads(line)
                if dic['type'] == 'WrittenQs' or  dic['type'] == 'OralQs':
                    text = clean_text(dic['text'])
                    questions.append(text)
                    qsdetails.append(str(dic['date']) +','+str(dic['member']))
                elif dic['type'] == 'Speech':
                    text = clean_text(dic['text'])
                    speeches.append(text)
                    spdetails.append(str(dic['date']) +','+str(dic['member']))
    else:
        print "Document not in required date range"

print len(speeches), len(spdetails)
print len(questions), len(qsdetails)

qsout = open('questionstext.txt', 'w')
for item in questions:
  qsout.write("%s\n" % item)
  
qsdout = open('questiondetails.txt', 'w')
for item in qsdetails:
  qsdout.write("%s\n" % item)

spout = open('speechestext.txt', 'w')
for item in speeches:
  spout.write("%s\n" % item)
  
spdout = open('speechdetails.txt', 'w')
for item in spdetails:
  spdout.write("%s\n" % item)