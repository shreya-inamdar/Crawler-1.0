from sys import argv
from os import makedirs, unlink
from os.path import dirname, exists, isdir,splitext
from string import replace ,find, lower
from htmllib import HTMLParser
from urllib import urlretrieve
from urlparse import urlparse, urljoin
from formatter import DumbWriter, AbstractFormatter
from cStringIO import StringIO
#from HTMLParser import HTMLParser


class Retriever:
    '''
    responsibilities:
    download, parse and queue
    '''
    def __init__(self,url):
        '''
        contructor of class.Instantiates the Retriver object and stores the url and filename as local attributes
        '''
        self.url = url
        self.file = self.filename(url)

    def filename(self, url, deffile = 'index.html'):
        '''
        input: url
        removes the http prefix
        index.html will be the default file name for storage of the url:this can be overridden by passing arguments to filename()
        '''
        parsedurl = urlparse(url,"http:",0) #parse path
        path = parsedurl[1] + parsedurl[2]
        text = splitext(path)
        if text[1] == '': #no file, use default
            path  =  path + deffile
        else:
            path = path + '/' + deffile
        dir = dirname(path)
        if not isdir(dir):  #create a new directory if necessary
            if exists(dir): unlink(dir)
            makedirs(dir)
        return path

    def download(self): #download web page
        try:
            retval = urlretrieve(self.url,self.file)
        except IOError:
            retval = ('***ERROR invalid url "%s"'%self.url,)
        return retval

    def parseAndGetLinks(self): #parse HTML and getlinks
        self.parser = HTMLParser(AbstractFormatter(DumbWriter(StringIO())))
        #try:
        self.parser.feed(open(self.file).read())
        #except HTMLParseError:
        self.parser.close()

        self.parser.close()
        return self.parser.anchorlist

class Crawler:      #manage the entire crawling process
    
    count = 0  #static downloaded page counter

    def __init__(self,url):
        self.q = [url]      #queue for the links to be downloaded
        self.seen = []      #the list of seen(downloaded) urls
        self.dom = urlparse(url)[1]  #store the domain name for the downloaded links to maintain a record

    def getPage(self,url):
        '''
            instantiates the retrieve object and searches
        '''
        r = Retriever(url)
        retval = r.download()
        if retval[0] == '*': #error case donot parse
            print retval, 'skipping parse...'
            return
        Crawler.count = Crawler.count + 1
        print '\n(',Crawler.count,')'
        print 'URL: ',url
        print 'FILE: ',retval[0]
        self.seen.append(url)

        links = r.parseAndGetLinks()  #get and process links
        for eachLink in links:
            if eachLink[:4] != 'http' and find(eachLink,'://')== -1 :
                eachLink = urljoin(url,eachLink)
            print '* ',eachLink,

            if find(lower(eachLink),'mailto: ') != -1:
                print '.....discarded mail to link'
                continue

            if eachLink not in self.seen:
                if find(eachLink, self.dom) == -1:
                    print '...discarded, not in domain'
                else:
                    if eachLink not in self.q:
                        self.q.append(eachLink)
                        print '...new added to Q'
                    else:
                        print '...discarded already in Q'
            else:
                print '...discarded , already processed'

    def go(self):       #process links in queue
        '''
        starting method to the crawler..it loops so long as the queue is not empty or any other sentinel as provided...its work horse is getPage()
        '''
        while self.q:
            url = self.q.pop()
            self.getPage(url)

def main():
    if len(argv) > 1:
        url = argv[1]
    else:
        try:
            url  = raw_input('Enter starting URL: ')
        except (KeyboardInterrupt, EOFError):
            url = ''

    if not url: return
    robot = Crawler(url)
    robot.go()

if __name__ == '__main__':
    main()

