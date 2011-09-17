#!/usr/bin/python

from datetime import datetime
from BeautifulSoup import BeautifulSoup
from pprint import pprint
import urllib2
import sqlite3
import sys
import re
import os

TYPES = [ 'all', 'movie', 'album', 'tv', 'person', 'video', 'company' ]

class MetacriticInfo:
    def __init__(self):
        self.id = None
        self.title = None
        self.type = None
        self.link = None
        self.boxart = None
        self.system = None
        self.publisher = None
        self.publisher_link = None
        self.release_date_text = None
        self.release_date = None
        self.metascore = None
        self.metascore_count = None
        self.metascore_desc = None
        self.user_score = None
        self.user_count = None
        self.user_score_desc = None
        self.summary = None
        self.esrb = None
        self.official_site = None
        self.developer = None
        self.genres = None
        self.num_players = None
        self.esrb_reason = None
        self.sound = None
        self.connectivity = None
        self.resolution = None
        self.num_online = None
        self.customization = None

class SearchResult:
    def __init__(self):
        self.id = None
        self.title = None
        self.type = None
        self.link = None
        self.system = None
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
        
class Metacritic:

    @staticmethod
    def search(query, type="all"):
        url = get_search_url(query, type)
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
                    res.system = span.text.strip()
                    
            product_title = result.find("h3", "product_title")
            if product_title:
                a = product_title.find("a")
                if a:
                    res.link = "http://www.metacritic.com" + a["href"]
                    res.id = a["href"][1:].replace("/", "_")
                    res.title = a.text.strip()
            
            metascore = result.find("span", "metascore")
            if metascore:
                res.metascore = metascore.text.strip()
            
            res.release_date_text = get_li_span_data(result, "release_date")
            if res.release_date_text:
                try:
                    res.release_date = datetime.strptime(res.release_date_text, '%b %d, %Y')
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

    @staticmethod
    def get_info(id):
        url = get_details_url(id)
        html = get_html(url)
        if not html:
            return None
        soup = BeautifulSoup(html)
        prod = MetacriticInfo()
        prod.id = id
        
        og_type = soup.find("meta", attrs={"name":"og:type"})
        if og_type:
            prod.type = og_type["content"].strip()
            
        og_image = soup.find("meta", attrs={"name":"og:image"})
        if og_image:
            prod.boxart = og_image["content"].strip()
        
        product_title = soup.find("div", "product_title")
        if product_title:
            a = product_title.find("a")
            if a:
                prod.link = "http://www.metacritic.com" + a["href"]
                prod.title = a.text.strip()
        
        platform = soup.find("span", "platform")
        if platform:
            a = platform.find("a")
            if a:
                prod.system = a.text.strip()
        
        publisher = soup.find("li", "publisher")
        if publisher:
            a = publisher.find("a")
            if a:
                prod.publisher = a.text.strip()
                prod.publisher_link = "http://www.metacritic.com" + a["href"]
        
        prod.release_date_text = get_li_span_data(soup, "release_data")
        if prod.release_date_text:
            try:
                prod.release_date = datetime.strptime(prod.release_date_text, '%b %d, %Y')
            except:
                prod.release_date = None        
        
        metascore = soup.find("div", "feature_metascore")
        if metascore:
            score_value = metascore.find("span", "score_value")
            if score_value:
                prod.metascore = score_value.text.strip()
            count = metascore.find("span", "count")
            if count:
                a = count.find("a")
                if a:
                    span = a.find("span")
                    if span:
                        prod.metascore_count = span.text.strip()
            desc = metascore.find("span", "desc")
            if desc:
                prod.metascore_desc = desc.text.strip()

        avguserscore = soup.find("div", "feature_userscore")
        if avguserscore:
            score_value = avguserscore.find("span", "score_value")
            if score_value:
                prod.user_score = score_value.text.strip()
            count = avguserscore.find("span", "count")
            if count:
                a = count.find("a")
                if a:
                    prod.user_count = a.text[:a.text.find(" ")]
            desc = avguserscore.find("span", "desc")
            if desc:
                prod.user_score_desc = desc.text.strip()                
        
        product_summary = soup.find("div", "product_summary")
        if product_summary:
            data = product_summary.find("span", "data")
            if data:
                prod.summary = data.text.strip()
        
        product_details = soup.findAll("div", "product_details")
        for pd in product_details:
            table = pd.find("table")
            if table:
                trs = table.findAll("tr")
                for tr in trs:
                    process_tr(prod, tr)
        
        return prod        
                
def process_tr(prod, tr):
    th = tr.find("th")
    td = tr.find("td")
    th_val = th.text.replace(":", "").strip()
    td_val = td.text.strip()
    
    if th_val == "Rating":
        prod.esrb = td_val
    elif th_val == "Official Site":
        prod.official_site = td_val
    elif th_val == "Developer":
        prod.developer = td_val
    elif th_val == "Genre(s)":
        prod.genres = td_val
    elif th_val == "Number of Players":
        prod.num_players = td_val
    elif th_val == "ESRB Descriptors":
        prod.esrb_reason = td_val
    elif th_val == "Sound":
        prod.sound = td_val
    elif th_val == "Connectivity":
        prod.connectivity = td_val
    elif th_val == "Resolution":
        prod.resolution = td_val
    elif th_val == "Number of Online Players":
        prod.num_online = td_val
    elif th_val == "Customization":
        prod.customization = td_val
        
def get_li_span_data(node, data_name):
    li = node.find("li", data_name)
    if li:
        data = li.find("span", "data")
        if data:
            return data.text.strip()
    return None
    
def get_search_url(query, type="all"):
    return "http://www.metacritic.com/search/%s/%s/results?sort=relevancy" % (type, query.replace(":", "").replace("-", "").replace("_", "").replace(" ", "+"))

def get_details_url(id):
    return "http://www.metacritic.com/%s/details" % id.replace("_", "/")
    
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
    elif len(sys.argv) == 3:
        results = Metacritic.search(sys.argv[1], sys.argv[2])
    else:
        return
    for result in results:
        pprint(vars(result))
        print ""
        pprint(vars(Metacritic.get_info(result.id)))
        print ""

if __name__ == "__main__":
    main()
    