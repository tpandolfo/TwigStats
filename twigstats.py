import sys
import html
from html.parser import HTMLParser
import urllib.request
import re

def sumList(l):
    ret = 0
    for i in l:
        ret += i
    return ret


class TwigChapter:

    def __init__(self):
        self.wordCount = 0
        self.title = ""
        self.arcNum = 0
        self.chapterNum = 0
    
    

#Custom HTMLParser to extract only the text of the story from the Twig website.
class TwigWordCount(HTMLParser):

    twigUrl = 'https://twigserial.wordpress.com/'

    def __init__(self):
        HTMLParser.__init__(self)
        self.wordCount = 0
        self.wordCountForChapter= 0
        self.inPost = False
        self.inTitle = False
        self.inChapter = False
        self.inParagraph = False
        self.chapters = []
    
    def handle_starttag(self, tag, attrs):
        if not self.inChapter:
            # Get chapter title and arc number.
            if (tag == 'h1' and len(attrs) == 1):
                if (attrs[0][0] == 'class' and attrs[0][1] == 'entry-title'):
                    self.inTitle = True               
            # Recognize that we've hit a chapter.
            if (tag == 'div' and len(attrs) == 1):
                if (attrs[0][0] == 'class' and attrs[0][1] == 'entry-content'):
                    self.inChapter = True
                    #print("In a chapter now!")
        if self.inChapter:
            # Recognize that we've hit a <p>
            if (tag == 'p'):
                self.inParagraph = True
            # Ignore <p>s with <a>s in them
            if (tag == 'a'):
                self.inParagraph = False
        
    def handle_endtag(self, tag):
        if self.inTitle:
            if (tag == 'h1'):
                self.inTitle = False
        if self.inChapter:
            if (tag == 'div'):
                self.inChapter = False
                self.wordCount += self.wordCountForChapter
                self.currentChapter.wordCount = self.wordCountForChapter
                self.chapters.append(self.currentChapter)
                self.wordCountForChapter = 0
                print("Processed " + str(len(self.chapters)) + " chapters...", end='\r')
        if self.inParagraph:
            if (tag == 'p'):
                self.inParagraph = False

    def handle_data(self, data):
        # Get the raw text, handle special unicode chars that Python doesn't recognize.
        text = html.unescape(data).replace(r'\xc2\xa0', '')
        if self.inTitle:
            self.currentChapter = TwigChapter()
            self.currentChapter.title = text
        if self.inParagraph:
            for word in text.split():
                # Handle char sequences that aren't words like '-'
                if re.search('[a-zA-Z0-9]', word) != None:
                    self.wordCountForChapter += 1

    def readAllTwig(self):
        pageNum = 1
        while (True):
            #Get webpage
            try:
                with urllib.request.urlopen(self.twigUrl + 'page/' + str(pageNum)) as page:
                    self.feed(str(page.read()))
                pageNum += 1
                self.reset()
            except urllib.error.HTTPError:
                break
            
        # Processing/sorting
        self.chapters.reverse()
        chapterCount = len(self.chapters)
        sortedChapters = sorted(self.chapters, key= lambda chapter: chapter.wordCount)
        longestChapter = sortedChapters[chapterCount - 1]
        shortestChapter = sortedChapters[0]
        chapterLengths = list(map(lambda chapter: chapter.wordCount, sortedChapters))

        # Spaces included to overwrite previous print
        print("Word count complete!                     ")
        print("\n")

        # Some stats
        print("Final Word Count: " + str(self.wordCount))
        print("Final Chapter Count: " + str(chapterCount))
        print("Longest Chapter: " + longestChapter.title + " (" + str(longestChapter.wordCount) + " words)")
        print("Shortest Chapter: " + shortestChapter.title + " (" + str(shortestChapter.wordCount) + " words)")
        print("Mean Chapter Length: " + str(int(float(sumList(chapterLengths))/float(chapterCount))))
        print("Median Chapter Length: " + str(chapterLengths[int(float(chapterCount - 1)/2.0)]))
        

twc = TwigWordCount()
twc.readAllTwig()
input()

