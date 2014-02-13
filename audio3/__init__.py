#!/usr/bin/python
# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
import urllib2, urllib
from itertools import chain
import pickle

"""http://www.audio3.cz/find.asp?name=Karel+Gott&ctid=1&cr="""

"""http://www.audio3.cz/find.asp?name=P%F8i%20m%EC%20st%F9j&cr=Rad%F9za"""
"""http://www.audio3.cz/find.asp?name=TITLE&cr=RADUZA&id=EAN"""
""" div class="goodslist"
       div class="desc"
       div class="medium"
       div

"""
import re
from sets import Set
gidSearch = re.compile('gid=([0-9]+)')
nextSearch = re.compile("href=\"([^\"]+)\">Dal")
yearSearch = re.compile("[0-9]{1,2}\.[0-9]{1,2}\.([1,2][0-9]{3})")
typeRegexp = re.compile('icons/([^\.]+)\.')

def searchUrl(url):
    if not url:
        return ([],'')

    def parseGoodslist(goodslist):
        h3 = goodslist.find('h3')
        saleprice = goodslist.find('span')
        a = h3.a
        desc = a.string
        result = gidSearch.search(a['href'])
        if not result:
            return None
        gid = result.group(1)
        result = typeRegexp.search(str(goodslist))
        if not result:
            return None
        goodsType = result.group(1)
        
        year = None
        result = yearSearch.search(str(goodslist))
        if result:
            year = result.group(1)
        return (gid, "%s - %s, %s / %s" % (desc, goodsType, str(year), saleprice.string))
    
    data = urllib.urlopen(url)
    soup = BeautifulSoup(unicode(data.read(),'cp1250'))
    #import pdb; pdb.set_trace()
    #soup=pickle.load(open("soup.pickle","rb"))

    goodslists = soup and soup.findAll('div',{'class':'goodslist'})
    aux = [parseGoodslist(goodslist) for goodslist in goodslists]
    results = [ii for ii in aux if ii]
    
    nextResult = nextSearch.search(str(soup))
    nextUrl = nextResult and nextResult.group(1)
    return (results,nextUrl)

from mechanize import Browser
def searchByGoogle(ean=None, short=False):
    br = Browser()
    br.set_handle_robots(False)
    br.addheaders = [('User-agent','Firefox'),]
    br.open('http://www.google.com')
    br.select_form('f')
    query = str(ean) #" ".join([ str(ii) for ii in (ean,title,interpret) if ii ])
    br.form['q'] = "%s site:.audio3.cz" % (query,)
    br.submit()
    results = []
    audio3LinkRe = re.compile("http://www.audio3.cz/goods.asp\?.*gid=(.*)")
    searchResults = []
    if short:
	data = br.response().read()
	soup = BeautifulSoup(unicode(data,'cp1250'))
	resultSection = soup.find('div',{'id':'res'})
	results = resultSection.findAll('li',{'class':'g'})
	for result in results:
	    links = result.findAll('a',{})
	    for ll in links:
		reresult = audio3LinkRe.search(ll.get('href'))
		if reresult:
		    gid = reresult.group(1)
		    desc = "".join(map(str,result.contents))
		    searchResults.append((gid,desc))
		pass
	    pass
	pass
    else:
	for link in br.links():
	    siteMatch = audio3LinkRe.search( link.url )
	    if siteMatch:
		audio3detail = br.follow_link(link).get_data()
		soup = BeautifulSoup(unicode(audio3detail, 'cp1250'))
		img = soup.find('div',{'id':'img'})
		desc = soup.find('ul',{'id':'desc'})
		res = (siteMatch.group(1),"<style type='text/css'>.saleprice{color:red;font-weight:bold}</style><div style='float:left;margin-right:3em;'>%s</div><div>%s</div><a href='%s'>original link</a><hr/>" % (str(img),str(desc),link.url))
		searchResults.append(res)
	    pass
	pass
    return (searchResults,None)

def articleShortInfo(gid):
    link = "http://www.audio3.cz/goods.asp?gid=%s" % (str(gid),)
    audio3detail = urllib.urlopen(link).read()
    soup = BeautifulSoup(unicode(audio3detail, 'cp1250'))
    img = soup.find('div',{'id':'img'})
    desc = soup.find('ul',{'id':'desc'})
    result = "<style type='text/css'>.saleprice{color:red;font-weight:bold}</style><div style='float:left;margin-right:3em;'>%s</div><div>%s</div><a href='%s'>original link</a><hr/>" % (str(img),str(desc),link)
    return result

def search(interpret=None, title=None, ean=None):
    """
    search(interpret=u"neco",title=u"dalsiho",ean=u"cislo")
    """
    query={'cr':interpret and interpret.encode('cp1250'),
           'name': title and title.encode('cp1250'),
           'id': ean and ean.encode('cp1250')}
    
    queryParts=["%s=%s" % (key, urllib.quote(query[key])) for key in query if query[key] ]
    if not query:
        return searchUrl('')

    url = "http://www.audio3.cz/find.asp?" + "&".join(queryParts)
    return searchUrl(url)

class Detail:
    def __init__(self, gid):
        self.gid = gid
        url = "http://www.audio3.cz/goods.asp?gid=%s" % (self.gid,)
        data = urllib.urlopen(url)
        self.soup = BeautifulSoup(unicode(data.read(), 'cp1250'))

        #pickle.dump(self.soup,open("detail.soup.pickle",'wb'))
        #self.soup = pickle.load(open("detail.soup.pickle",'rb'))
        #import pdb; pdb.set_trace()

        self.detail = self.soup and self.soup.find('div',{'id':'in_centercol'})
        self.interpret = self.detail and self.detail.h2 and self.detail.h2.a and self.detail.h2.a.string
        self.title = self.detail and self.detail.h2 and len(self.detail.h2.contents) > 1 and self.detail.h2.contents[1]
        aux = re.search("^[\ \t]*-[\ \t]*(.*)$",str(self.title))
        if aux:
            self.title = unicode(aux.group(1),'cp1250')
            
        self.description = self.detail and self.detail.description and self.detail.description.string or ''
        self.tracklists = self.detail and self.detail.findAll('table',{'class':'tracklist'})
        
        aux = self.detail and self.detail.h2 and self.detail.find('div',{'id':'img'})
        self.imgUrl = aux and aux.find('img')['src']
        
        itemDesc = self.detail and self.detail.h2 and self.detail.find('ul',{'id':'desc'})
        result = yearSearch.search(str(itemDesc))
        self.year = None
        if result:
            self.year = result.group(1)
            
        self.type = self._getType(itemDesc)
        self.price = self._getPrice(itemDesc)
        self.ean = self._getEAN(itemDesc)
        self.publisher = self._getPublisher(itemDesc)
        pass
    
    #typeRegexp = re.compile('icons-([a-z]+)\.gif')
    def _getType(self,itemDesc):
        """ "Data/XSL/img/icons/icons/CD.gif" """
        result = typeRegexp.search(unicode(itemDesc))
        return result and result.group(1)
        
    
    priceRegexp = re.compile('([0-9]+)')
    def _getPrice(self,itemDesc):
        string = itemDesc and itemDesc.find('span',{'class':'saleprice'}).string or ''
        result = self.priceRegexp.search(string)
        return result and result.group(1)

    eanRegexp = re.compile('EAN/UPC:[\ ]*([^\ \t<]+)')
    def _getEAN(self,itemDesc):
        result = self.eanRegexp.search(unicode(itemDesc))
        return result and result.group(1)

    def _getPublisher(self, itemDesc):
        li = itemDesc and itemDesc.findAll('li')[3]
        return li and li.a and li.a.string
    
if __name__ == "__main__":
    (gids,nextUrl) = search(interpret=u"Radůza")
    print gids
    print nextUrl
    #
    # http://www.audio3.cz/goods.asp?gid=1042699
    #
    # pickle.dump(gids,open("gids.pickle",'wb'))
    # gids=pickle.load(open("gids.pickle","rb"))
    
    gid = gids and gids[0][0]

    detail = Detail(gid)
    import pdb; pdb.set_trace()
    print detail.title
    #print str(detail.__dict__)
