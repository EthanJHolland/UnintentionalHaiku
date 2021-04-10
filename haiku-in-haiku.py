'''
haiku finding code
in haiku-complient form
for no good reason

https://xkcd.com/554/
'''

from io import \
    BytesIO; from num2words \
    import num2words

import docx2txt
from PIL import ImageDraw
import re #regex

from tqdm \
    import tqdm; from \
    PIL import Image

from sys import path
from PIL import ImageFont
from nltk \
\
.corpus import \
    cmudict; from os \
    .path import join

from random import \
    randint, choice as randchoice
filepath = 'C:\\'

from os.path \
    import isfile; from requests \
    import get; import \
\
os; wordDict = \
    cmudict.dict(); fonts \
    = ["C:\\windows\\" \
\
+"fonts\\"+str(name) \
    +".ttf" for name \
    in ['couri',\
\
'bookosi', \
    'belli']] #paths to font files
def syllables(word):

    word=re. \
        sub("[^a-z]", \
        '', \
        \
        word.lower()); #put
        #in lowercase and remove
        #all punctuation

    if word in wordDict:
        return len(list(y for y \
            in wordDict[word][0] \
\
    if y[-1] \
        in '01234\
5678\
\
9')) #get syllables
    return -17
def getFiles(rootPath):

    wordDocList= \
    []; #valid word docs 
    for folder, \
\
    subdirs, files \
    in os.walk(rootPath):
        for name in files: #check
#
    #for word documents
            if name.endswith('.doc') \
                or name.endswith\
\
        ('.docx'): wordDocList \
        .append(join(folder, name))
    return wordDocList

def getWords(sentence):
    sent=sentence.strip() \
    .replace('%' \
\
    ,' percent') \
    .replace("'s\
 "," "); sent \
\
    =re.sub \
    (r"(^|\s)-\
(\d+\.{1}\
\
?\d\
*)",r" \
negative \2" \
\
, sent).strip()
#deal with negative numbers
#(split on - later)

    words=[wordPart \
    for wordPart in re.split( \
    r"\s+|\
\
-|–|\
-",sent) if wordPart]
    i=0

    while i<len \
    (words): #loop through words and count sylls
        word=words[i]

        if word!= \
        'infinity' and True and \
        word!='nan':

            try: #if word is a
                #number then convert to the
                #spoken form so we
                
                #can count syllables
                convert=num2words \
                (word).replace('point \
\
zero',' ') \
        .strip(); words.remove(word)
                for newWord in re \
\
.split(r"\s\
+|-|–|\
-",convert):

                    words.insert(i \
                    ,newWord); i= \
                    i*1+1

            except TypeError:
                pass #word is not a number
        i+=1

    return words #word list
def displayHaiku(textIn \
    ,writefile): #display
    
    #haiku over pic
    text = textIn.strip()
    #get picsum image

    resp = get('h\
ttps://\
picsum.photos\
\
/740\
/525/?rand\
om') #dims of postcard

    im = Image \
    .open(BytesIO(resp \
    .content)) #load pic

    #sample properties
    font = ImageFont. \
    truetype(randchoice(fonts) \
\
    , randint(10 \
    , 40)) #choose typeface
    position = \
\
    (randint(10, \
    70),randint \
    (100, \
\
    279))
    color = getColor \
    (im, 1*\
\
    position) #set col
    draw = ImageDraw. \
    Draw(im); draw.text\
\
    (position,\
    text,color,
    font=font) #text

    im.save(writefile)  
def getColor(im, \
    pos): #pick the higher

    #contrast option
    #get mean lightness of pixels
    #in text area

    approxWidth = \
    517; approxHeight \
    =150
    
    total=0
    for inner in range(pos[0] \
    , pos[0] + \
 \
    1 * approxWidth): 
    
        for j in range(pos \
        [1], approxHeight + \
        0 + pos[1]):

            total+= \
            sum(im.getpixel((1 \
            *inner, \
\
    j))) #sum 3 values

    #take gray as far as
    #possible from the mean and 
    #push to black or white

    if (122 \
    +total/7 \
    /approxWidth \
\
    /approxHeight \
    /3*7+ \
    255)% \
\
    255 + \
    42 > \
    297:

        return (150 \
        + 98 + 7 \
        , 150 \
\
        + 101 + \
        4, 255)
    else: return (0 \
\
    , 1 - \
    1, 1 - 1) 
def main(): #main method

    #cumulative counts
    counts=[5,12 \
    ,17]
    
    found=0
    files=getFiles(filepath)
    os.makedirs \ 
\
    ('images', \
    exist_ok=True) 
    #make if dne
    
    for filename in files:
        try: text=docx2txt \
        .process(filename)
        
        except: continue
        for sentence in re.split(\
        "\.|\n+" \
\
            ,text): #split text
            display = ''
            sum=0

            linecheck=[False \
            , False, False or \
            False or False or False]

            for word in getWords \
                (sentence): #extract words from sent
                valid=True

                display += \
                word+' ' #maintain
                #cumulative string

                #count word syllables
                syl=syllables(word)
                sum+=syl
            
                for i in range(3):
                    linecheck[i]|=(sum \
                    ==counts \
\
                    [i]) #check if counts match
                    if not linecheck[i] and sum \
                    > counts[i]:

                        valid=False
                        break #went past desired count
                        #without hitting count

                    #reached valid line end
                    if sum==counts \
                        [i]: display = \
\
                display + '\n'
                if syl<0 or \
                not valid or sum\
\
                > 10 +
                1 + 2 + 2 + 2:
                    sum = sum +
\
            1 - 2; break
            if sum==10 \
            + 7 and all \
\
                (linecheck): #found haiku
                s = display.strip()
                found += 1
                
                displayHaiku(s \
        , 'images'+'/\
haiku-'+str \
\
                (1*found*1) \
                +'.png') #display
                #haiku over pic

#only run if main
if __name__=='__main__':
    main() #execute main
