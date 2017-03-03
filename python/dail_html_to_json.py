# -*- coding: utf-8 -*-

# import relevant libraries
import re
import json
import glob

def find_speaker_position(doc):
    """
    Function to extract all questioner/speaker tags that appear in page.
    Speaker tags identify when one politicians stops talking and another begins.
    This enables me to break the document into chunks of text.
    
    
    Keyword arguments:
    doc -- full html document containing legislatvie
    
    Returns:
    speakertags -- a list of speaker tags
    locations -- a list of the locations of the speaker tags in the document 
    """
    speakertags =[]
    locations =[]
    matches = re.finditer(r'<font color="#990000">.*?</font>|<span class="speaker">.*?</span>', doc,  re.DOTALL)
    for match in matches:
        # pass matches that are a minister, the prime minister, or deputy prime minister
        if 'font' in match.group(0) and any(k in match.group(0) for k in ['Minister', 'Taoiseach', 'naiste']):
            pass
        else:
        # get tags if not a minister, the prime minister, or deputy prime minister
            speakertags.append(match.group(0))
            locations.append(match.start(0))
    speakertags.append('<!--/div-->') ## add div tag as anchor
    return speakertags, locations

def get_date(doc):
    """
    Function to extract date from document name
    
    Keyword arguments:
    doc -- full html document containing legislative text
    
    Returns:
    day -- the date of the document
    """
    day = re.search(r'dail(\d{8})', doc).group(1)
    return day

def find_header(doc):
    """
    Function to get header of documents
    
    Keyword arguments:
    doc -- full html document containing legislative text
    
    Returns:
    docheader -- the text of the document header
    """
    docheader = re.search('<h1>.*?</h1>', doc, re.DOTALL).group(0)
    docheader = re.sub('<.*?>', ' ', docheader, 0, re.DOTALL)
    return docheader

def find_member(text):
    """
    Function to extract speaker memberid
    
    Keyword arguments:
    text -- id of speaker from chunk of text containing legislative text, html tags, and links
    
    Returns:
    memberid -- the id code for the speaker
    """
    memberid = re.search(r'MemberID=(\d+)', text).group(1)
    return memberid

def extract_text(text):
    """
    Function to grab relevant legislative text from chunk of text containing legislative text, html tags, and links
    
    Keyword arguments:
    text -- id of speaker from chunk of text containing legislative text, html tags, and links
    
    Returns:
    chunk -- returns text excluding html tags, irrelevant procedural statements
    """
    chunk = re.sub('<i><a.*?</i>|</a><i>.*?</i>|<i>.*?</i></p>', ' ', text) ## these tags usually used for time
    chunk = re.sub('<b>Deputy.*?</b>', ' ', chunk) ## remove name of dep
    chunk = re.sub('<a.*?</a>', ' ', chunk) ## remove everything inside <a> tags
    chunk = re.sub('<span.*?</span>', ' ', chunk) ## remove everything inside <span> tags
    chunk = re.sub('<table.*?</table>', ' ', chunk, 0, re.DOTALL) ## remove tables
    chunk = re.sub('<font color="blue".*?</font>', ' ', chunk) ## remove everything inside <font color='blue'> tags
    chunk = re.sub('<.*?>', ' ', chunk) ## remove remaining html tags
    chunk = re.sub('&nbsp;', ' ', chunk) ## remove newline indicator
    ## remove irrelevant procedural statements
    chunk = re.sub('</a>(Question|Amendment) put.*?</p>|</a>(Question|Amendment) again.*?</p>|(Question|Amendment) declared.*?</p>', ' ', chunk)
    chunk = re.sub('</a>The D&aacute;il divided:.*?</p>|</a>Tellers:.*?</p>' ,' ', chunk) ## re
    chunk = re.sub('</a>(The D&aacute;il|Debate) adjourned.*?</p>', ' ', chunk)
    chunk = ' '.join(chunk.split())
    return chunk


def find_comments(doc):
    """
    Function to find html snippet comments in text.
    Snippet tags identify when one politicians stops talking and another begins.
    This enables me to break the document into chunks of text.
    
    Keyword arguments:
    doc -- full html document containing legislative text
    
    Returns:
    comments -- returns list of snippet tags
    """
    comments  = re.findall(r'<!-- Snippet[^>]*>', doc)
    comments.append('<!--/div-->') ## add div tag as anchor
    return comments

def find_type(comment):
    '''
    Function to fin the snippet comment type.
    The type provides information about the text. For instance type 4 indicates a headers, 6 a question etc.
    
    Keyword arguments:
    comment -- Snippet comment string created from above function
    
    Returns:
    texttype -- digit indicating type
    '''
    texttype = re.search(r'type: (\d+)', comment).group(1)
    return texttype

def extract_old_format(doc, date, head, filename):
    '''
    Function to extract member ID, text type, and text from raw html pages that have old format (before sept 2012).
    
    Keyword arguments:
    doc -- full html document containing legislative text
    date -- date for document
    head -- document header
    filename -- filename for document
    
    Returns:
    date.jsonl - jsonl file containing relevant legislative text and corresponding metadata for each day
    missing.txt - 
    '''
    alltexts = [] # list for storing relevant text
    missing = [] # list for keeping account of html docs that don't contain relevant text
    doc = re.sub('<span class="column".*?</span>', ' ', doc) # remove html span class="column" tags
    speakers, positions = find_speaker_position(doc) ## get speaker
    if len(positions) == 0:
        pass
        print 'No relevant text in document'
        missing.append(filename)
    else:
        for i, j, k in zip(speakers, speakers[1:], positions): 
            expression = '(?<='+i+').*?(?='+j+')'
            exp = re.compile(expression, re.DOTALL)
            section = re.search(exp, doc[k-2:]).group(0)
            try:
                textdic = {}
                textdic['member'] = find_member(section)
                textdic['date'] = date
            except:
                continue
            textdic['text'] = extract_text(section)
            if '<font color' in i and 'Written' in head:
                textdic['type']  = 'WrittenQs'
            elif 'speaker' in i and 'Written' in head:
                textdic['type'] = 'WrittenAns'
            elif '<font color' in i and 'Question' in head:
                textdic['type'] = 'OralQs'
            else:
                textdic['type'] = 'Speech'
            alltexts.append(textdic)
        ## Write to file
        fname = "json/"+str(date)+".jsonl"
        with open(fname, 'a+') as f:
            for t in alltexts:
                f.write(json.dumps(t, ensure_ascii=False)+"\n")
    mname = "missing.txt"
    with open(mname, 'a+') as miss:
        for m in missing:
            miss.write(m+"\n")
    print "File Done..."           
        
def extract_new_format(doc, date, head):
    '''
    Function to extract member ID, text type, and text from raw html pages that have old format.
    '''
    alltexts = []
    doc = re.sub('<span class="column".*?</span>', ' ', doc)
    comments  =  find_comments(doc)
    for i, j in zip(comments, comments[1:]):
        expression = '(?<='+i+').*?(?='+j+')'
        exp = re.compile(expression, re.DOTALL)
        section = re.search(exp, doc).group(0)
        try:
            textdic = {}
            textdic['member'] = find_member(section)
            textdic['date'] = date
        except:
            continue
        textdic['text'] = extract_text(section)
        if find_type(i)=='5' and 'Written' in head:
            textdic['type'] = 'WrittenQs'
        elif find_type(i)=='7' in i and 'Written' in head:
            textdic['type'] = 'WrittenAns'
        elif find_type(i)=='5' in i and 'Question' in head:
            textdic['type'] = 'OralQs'
        else:
            textdic['type'] = 'Speech'
        alltexts.append(textdic)
        print "File done..."
    ## Write to file
    fname = "json/"+str(date)+".jsonl"
    with open(fname, 'a+') as f:
        for t in alltexts:
            f.write(json.dumps(t, ensure_ascii=False)+"\n")
            
def html_to_json(html):
    print html
    docname = html
    html = open(html, 'r').read()
    html = re.sub('[\(\)]', '', html)
    header = find_header(html)
    date = get_date(html)
    if int(date) < 20120918:
        extract_old_format(doc=html, date=date, head=header, filename = docname)
    else:
        extract_new_format(doc=html, date=date, head=header)
        
## Loop through folders and documents and information from html
for year in range(2007, 2016+1):
    for txt in sorted(glob.glob('html/'+str(year)+'/*')):
        html_to_json(txt)