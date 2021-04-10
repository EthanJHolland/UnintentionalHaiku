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
default_filepath = 'C:\\' #root folder - making this more specific will speed up file finding
fonts=["C:\\windows\\fonts\\{}.ttf".format(name) for name in ['couri','bookosi','belli']] #paths to font files

def getFiles(root='C:\\', verbose=False):
    if verbose:
        print('looking for files (this may take a while)')

    wordDocs=[]
    for path, subdirs, files in tqdm(os.walk(root)):
        for name in files:
            if name.endswith('.doc') or name.endswith('.docx'):
                wordDocs.append(os.path.join(path, name))

    if verbose:
        print("found {} word documents".format(len(wordDocs)))
    return wordDocs

def extractTexts(files, verbose=False):
    #get texts from files
    if verbose:
        print('extracting text from files')

    texts = []
    for filename in files:
        try:
            texts.append((docx2txt.process(filename), filename))
        except:
            pass #corrupted file
    return texts

def extractHaiku(texts, verbose=False):
    haikus = []
    linecount=[5,12,17] #syllables after each line of a haiku

    for text, filename in texts:
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
                haikus.append(display.strip())

                if verbose:
                    print("___\nfrom:", filename)
                    print('haiku-', len(haikus) - 1, '.png')
                    print(display.strip())

    return haikus

def displayHaiku(haikus, directory='images', verbose=False):
    for index, text in enumerate(haikus):
        #get picsum image
        response = requests.get('https://picsum.photos/740/525/?random') #dimensions of a postcard
        img = Image.open(BytesIO(response.content))

        #generate properties
        font = ImageFont.truetype(random.choice(fonts), randint(30,40)) #choose typeface, font size from distributions
        position = (randint(10,70),randint(100,300)) #choose x,y coordinates
        color = getColor(img, position)

        #write text and save
        draw = ImageDraw.Draw(img)
        draw.text(position, text, color,font=font)
        img.save(os.path.join(directory,'haiku-{}.png'.format(index)))  

def countSyllables(word):
    word=re.sub(r"[^a-z]",'',word.lower())
    if word in wordDict:
        return len(list(y for y in wordDict[word][0] if y[-1] in '0123456789'))
    return -1

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
            except:
                pass #not a number
        i+=1
    return words

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
    filepath = sys.argv[1] if len(sys.argv) > 0 else default_filepath

    os.makedirs('images', exist_ok=True) #make images folder if doesn't already exist
    files = getFiles(filepath, verbose)  #get files
    texts = extractTexts(files, verbose) #extract text from files
    haiku = extractHaiku(texts, verbose) #extract haikus from text
    displayHaiku(haiku, 'images', verbose) #display found haiku over images and save in /images

if __name__=='__main__':
    main(True)