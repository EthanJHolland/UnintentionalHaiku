import os
import re
import sys
import nltk
import random
import docx2txt
import requests
from tqdm import tqdm
from io import BytesIO
from random import randint
from nltk.corpus import cmudict
from num2words import num2words
from os.path import isfile, join
from PIL import Image, ImageFont, ImageDraw 

wordDict = cmudict.dict() 
filepath = 'C:\\' #root folder - making this more specific will speed up file finding
fonts=["C:\\windows\\fonts\\{}.ttf".format(name) for name in ['couri','bookosi','belli']] #paths to font files

def countSyllables(word):
    word=re.sub(r"[^a-z]",'',word.lower())
    if word in wordDict:
        return len(list(y for y in wordDict[word][0] if y[-1] in '0123456789'))
    return -1

def getFiles(root=sys.path[0]):
    wordDocs=[]
    for path, subdirs, files in os.walk(root):
        for name in files:
            if name.endswith('.doc') or name.endswith('.docx'):
                wordDocs.append(os.path.join(path, name))
    return wordDocs

def getWords(sentence):
    sentence=sentence.strip().replace('%',' percent').replace("'s "," ")
    sentence=re.sub(r"(^|\s)-(\d+\.?\d*)",r" negative \2",sentence).strip() #deal with negative numbers (since we split on - later)
    words=[word for word in re.split(r"\s+|-|–",sentence) if word]
    i=0
    while i<len(words):
        word=words[i]
        if word!='infinity' and word!='nan': #ignore cases that break num2words
            try:
                #if word is a number, convert to the spoken form so we can count syllables
                conv=num2words(word).replace('point zero','').strip()
                words.remove(word)
                for newWord in re.split(r"\s+|-|–",conv):
                    words.insert(i,newWord)
                    i+=1
            except TypeError:
                pass #not a number
        i+=1
    return words

def displayHaiku(text,writefile):
    #get picsum image
    response = requests.get('https://picsum.photos/740/525/?random') #dimensions of a postcard
    img = Image.open(BytesIO(response.content))

    #generate properties
    font = ImageFont.truetype(random.choice(fonts), randint(30,40)) #choose typeface, font size from distributions
    position = (randint(10,70),randint(100,300)) #choose x,y coordinates
    color = getColor(img, position)

    #write text and save
    draw = ImageDraw.Draw(img)
    draw.text(position,text,color,font=font)
    img.save(writefile)  

def getColor(img, position):
    #get avg lightness of pixels in the approximate location of the text
    approxWidth=500
    approxHeight=150
    tot=0
    for i in range(position[0], position[0]+approxWidth):
        for j in range(position[1],position[1]+approxHeight):
            tot+=sum(img.getpixel((i,j))) #add r+g+b
    avg=tot/approxWidth/approxHeight/3

    #take gray as far as possible from avg and flatten to black or white
    if (avg+122)%255>122:
        return (255,255,255)
    else:
        return (0,0,0) 

def main(verbose=False):
    os.makedirs('images', exist_ok=True) #make images folder if doesn't already exist
    linecount=[5,12,17] #syllables after each line of a haiku
    found=0
    
    if verbose:
        print('looking for files (this may take a while)')
    files=getFiles(filepath)
    if verbose:
        print("found {} word documents".format(len(files)))
    for filename in files:
        try:
            text=docx2txt.process(filename)
        except:
            continue #corrupted file

        for sentence in re.split(r"\.|\n+",text):
            display='' #sentence formatted like a haiku
            linecheck=[False,False,False]
            sum=0
            for word in getWords(sentence):
                syllables=countSyllables(word)
                sum+=syllables
                display+=word+' '

                #verify that it is still a valid haiku
                valid=True
                for i in range(3):
                    linecheck[i]|=(sum==linecount[i])
                    if not linecheck[i] and sum>linecount[i]:
                        valid=False
                        break

                    if sum==linecount[i]:
                        display+='\n'
                if not valid or syllables<0 or sum>17:
                    sum=-1
                    break

            if sum==17 and all(linecheck): #found a haiku
                found+=1
                if verbose:
                    print("haiku {} ({})\n{}\n-".format(found,filename,display.strip()))
                displayHaiku(display.strip(),'images/haiku-{}.png'.format(found))

if __name__=='__main__':
    main()
