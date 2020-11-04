#You may need to enable these two commandes if your punkt isn't installed
#once dowloaded and installed nltk will work perfectly fine
#1- import nltk
#2- nltk.download('punkt')

'''
    Imports:
        -requests: to lunch url requests and exceptions
        -bs4: web scrapper used to parse and extract data from websites
        -nltk.ngrams: funct to create multiple requests with ngram combinations
        -word_tokenize: we use to tokenize (split) our texts into a list of words
        -time: we use sleep funct to wait for the network issues to be dealed with
        -re.sub: function that alllow as to delete portions of text that are or not in the text
        -io: used to open and write into files if needed
        -langdetect: detecting search language to determin how the output text will be cleaned
        -json: for json files management and saving results
    ---------
    Variables returned:
        -a Python Dictionnary is returned as a json file in the same path as this code file
    ---------
    Structure of the file:
        -Containes one function generate a corpora from the search engine google.com
'''

import urllib
import requests
from bs4 import BeautifulSoup
from nltk import ngrams
from nltk.tokenize import word_tokenize
from time import sleep
from re import sub
import io
import json
from langdetect import detect

#funct to generate grams from original keywords chain
def getGrams(KeyChain):
    Lang = detect(KeyChain)
    NewKeyChains = [] # a list to store new combinations
    Splited = KeyChain.split() #spliting keywords into individual words
    Grams = list(ngrams(Splited,3)) #using nltk ngrams funct to create combinations of window = 3
    #looping over grams to concatinate them
    for Gram in Grams:
        #new key variable
        NewKey = ""
        #looping over words inside the gram
        for item in Gram:
            #concatination using the "+" sign to use diractly in google's query
            NewKey = NewKey + item + "+"
        #deleting last "+" sign from the new chain
        NewKey = NewKey[:len(NewKey)-1]
        #saving query in the list
        NewKeyChains.append(NewKey)
    
    #testing if the combinations list is empty (could be if the keywords.splited length was less than 3)
    if NewKeyChains == []:
        #if so, we diractly replace wites with "+" sign and return the final resutl
        return KeyChain.replace(" ","+")
    else:
        #if not, we return the list
        return NewKeyChains, Lang

#getting links from google search
def getGoogleLinks(Grams):
    # desktop user-agent
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
    LinksList = [] #list to store links reutnred

    #looping over the combinations created above
    for Gram in Grams:
        #for each one we performe a google search
        Url = f"https://google.com/search?q={Gram}"
        Headers = {"user-agent": USER_AGENT}
        Response = requests.get(Url, headers=Headers)

        #if response granted, we proceede to extraction
        if Response.status_code == 200:
            #creating a bs4 obj
            soup = BeautifulSoup(Response.content, "html.parser")
            #links are stored in <div class="r"> ... </div> so we loop over that div items
            for rDiv in soup.find_all('div', class_='r'):
                #for each one, we find all links
                Link = rDiv.find_all('a')
                if Link:
                    #if list is not empty we test if the has not being stored and if it's not a youtube video since there's no text data to extract
                    if Link[0]['href'] in LinksList or "youtube" in Link[0]['href']:
                        continue
                    else:
                        #otherwise, we return the link from the <a href="link"> 
                        LinksList.append(Link[0]['href'])
                        #waiting for 1 second to avoing spaming the search engine
                        sleep(1)

    #returning context variable in django
    return LinksList

#funct to get data from links
def Scrapper(Links, Lang):
    Corpora = {}#variable returned as context in django
    
    #other variables needed
    Count = 1
    Articles = {}
    GroupedText = ""

    # desktop user-agent
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
    Headers = {"user-agent": USER_AGENT}

    #looping over links returned from the searchs
    for Link in Links:
        #trying to lunch requests
        try:    
            #if response is granted we proceed to text extraction
            Response = requests.get(Link, headers=Headers)
            if Response.status_code == 200:
                #creating a bs4 obj
                soup = BeautifulSoup(Response.content, "html.parser")
                #finding all paragraphes in <p>...</p>
                Paragraphes = soup.find_all('p')
                #looping over poaragraphes returned
                for Paragraphe in Paragraphes:
                    #cleaning data
                    if Lang == "ar":
                        Articles[Count] = sub(r'[^\u0600-\u06ff\u0750-\u077f\ufb50-\ufbc1\ufbd3-\ufd3f\ufd50-\ufd8f\ufd50-\ufd8f\ufe70-\ufefc\uFDF0-\uFDFD]+',' ',Paragraphe.getText())
                    else:
                        Articles[Count] = sub(r'[^A-Za-z]+',' ',Paragraphe.getText())                        
                    #saving a globale groupes texted for further uses
                    GroupedText = GroupedText + " " +  Articles[Count]
                    Count = Count + 1
                    #waiting for 1 second to avoing spaming the search engine
                    sleep(1)                        
        #otherwise, some exceptions need to be handled
        except requests.exceptions.MissingSchema:
            continue
        except requests.exceptions.InvalidSchema:
            continue
        except requests.exceptions.ConnectionError:
            continue
    #Computing the number of diffrent words in the corp we just created
    GlobalWolrdsList = word_tokenize(GroupedText)
    DIffWordsList = []
    for Word in GlobalWolrdsList:
        if Word in DIffWordsList:
            continue
        else:
            DIffWordsList.append(Word)

    #Finihing other keys values that might be needed        
    
    Corpora["WordsCount"] = len(word_tokenize(GroupedText))
    Corpora["DiffWordsCount"] = len(DIffWordsList)
    Corpora["Source"] = "Web"
    Corpora["ArticlesCount"] = Count
    Corpora["Articles"] = Articles
    
    #returning varibale as context in django
    return Corpora
#Scap and save .. 
def toJson(Keychain, Name):
    #Scrapping the web 
    Grams, Lang = getGrams(Keychain)
    Corpora = Scrapper(GetGoogleLinks(Grams), Lnag)


    #Saving into a json file
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    my_file = os.path.join(THIS_FOLDER, Name + '.json')

    write_file = open(my_file, "w")
    json.dump(Corpora, write_file, indent=2)
    write_file.close()

