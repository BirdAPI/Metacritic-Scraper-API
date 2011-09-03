#!/usr/bin/python

from datetime import datetime
from BeautifulSoup import BeautifulSoup
import urllib2
import sys
import re
import os

class SearchResult:
    def __init__(self):
        self.id = None
        self.title = None
        self.type = None
        self.link = None
        self.platform = None
        self.metascore = None
        self.release_date_text = None
        self.release_date = None
        self.esrb = None
        self.publisher = None
        self.index = None
        self.page = None
        self.summary = None
        self.user_score = None
        self.runtime = None
 
    #FIND: self.([^ ]+) = None
    #REPLACE: self.\1, 
    def __repr__(self):
        return repr([ self.id, self.title, self.type, self.link, self.platform, self.metascore, self.release_date_text, self.release_date, self.esrb, self.publisher, self.index, self.page, self.summary, self.user_score, self.runtime ])

        
class Metacritic:

    @staticmethod
    def search(query):
        url = get_search_url(query)
        html = get_html(url)
        if not html:
            return None
        soup = BeautifulSoup(html)
        i = 0
        page = 0
        allresults = []
        results = soup.findAll("li", "result")
        for result in results:
            res = SearchResult()
            result_type = result.find("div", "result_type")
            if result_type:
                strong = result_type.find("strong")
                if strong:    
                    res.type = strong.text.strip()
                span = result.find("span", "platform")
                if span:    
                    res.platform = span.text.strip()
                    
            product_title = result.find("h3", "product_title")
            if product_title:
                a = product_title.find("a")
                if a:
                    res.link = "www.metacritic.com" + a["href"]
                    res.id = a["href"][1:].replace("/", "_")
                    res.title = a.text.strip()
            
            metascore = result.find("span", "metascore")
            if metascore:
                res.metascore = metascore.text.strip()
            
            res.release_date_text = get_li_span_data(result, "release_date")
            if res.release_date_text:
                try:
                    res.release_date = datetime.strptime(res.release_date_text, '%B %d, %Y')
                except:
                    res.release_date = None 
                    
            res.esrb = get_li_span_data(result, "maturity_rating")
            
            res.publisher = get_li_span_data(result, "publisher")
            
            deck = result.find("p", "deck")
            if deck:
                res.summary = deck.text.strip()
            
            res.user_score = get_li_span_data(result, "product_avguserscore")
            
            res.runtime = get_li_span_data(result, "runtime")
            
            res.index = i
            res.page = page
            allresults.append(res)
            i = i + 1
        return allresults
                        
                
               
def get_li_span_data(node, data_name):
    li = node.find("li", data_name)
    if li:
        data = li.find("span", "data")
        if data:
            return data.text.strip()
    return None
    
def get_search_url(query):
    return "http://www.metacritic.com/search/all/%s/results?sort=relevancy" % query.replace(" ", "+")

def get_html(url):
    try:
        request = urllib2.Request(url)
        request.add_header("User-Agent", "Mozilla/5.001 (windows; U; NT4.0; en-US; rv:1.0) Gecko/25250101")
        html = urllib2.urlopen(request).read()
        return html
    except:
        print "Error accessing:", url
        return None 
    
def main():
    print "__main__"
    if len(sys.argv) == 2:
        results = Metacritic.search(sys.argv[1])
        for result in results:
            print result, "\n"

if __name__ == "__main__":
    main()
    