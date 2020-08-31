import requests
from bs4 import BeautifulSoup
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
import threading
import mysql.connector
from mysql.connector import Error
from mysql.connector.connection import MySQLConnection
from mysql.connector import pooling
import time
start_time = time.time()
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import roc_auc_score
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display
import pickle
from bs4.element import Comment

class MultiThreadScraper:

    def __init__(self, base_url):

        self.base_url = base_url
        #self.domain_name = urlparse(base_url).netloc
        self.root_url = '{}://{}'.format(urlparse(self.base_url).scheme, urlparse(self.base_url).netloc)
        self.pool = ThreadPoolExecutor(max_workers=20)
        self.scraped_pages = set([])
        self.to_crawl = Queue()
        self.to_crawl.put(base_url)
        self.to_crawlLock = threading.Lock()
        # self.mydb = mysql.connector.connect(
        #       host="localhost",
        #       user="root",
        #       password="",
        #       database="search_database"
        #     )

        # self.mycursor = self.mydb.cursor()
        #self.mycursor.execute("CREATE TABLE sites (url VARCHAR(255), keywords TEXT)")
        self.niveLock = threading.Lock()

        self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="pynative_pool",
                                                                  pool_size=20,
                                                                  pool_reset_session=True,
                                                                  host='localhost',
                                                                  database='search_database',
                                                                  user='root',
                                                                  password='')

        training_data = pd.read_csv('trainData_v2.csv')
        training_data["label"]=9*[0] + 7 *[1] + 5*[2] + 9*[3] + 6 *[4] + 6*[5] + 9*[6]
        X_train = np.array(training_data["doc"])
        y_train = np.array(training_data["label"])

        self.cv = CountVectorizer(max_features= 2 ** 18 ,strip_accents='ascii', token_pattern=u'(?ui)\\b\\w*[a-z]+\\w*\\b', lowercase=True, stop_words='english')
        X_train_cv = self.cv.fit_transform(X_train)
        self.naive_bayes = MultinomialNB()
        self.naive_bayes.fit(X_train_cv, y_train)

    def tag_visible(self,element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True


    def is_valid(self,url):
        """
        Checks whether `url` is a valid URL.
        """
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    def parse_links_info(self, html,murl):
        soup = BeautifulSoup(html, 'lxml')
        if soup.title != None :
            title = str(soup.title.string)


            texts = soup.findAll(text=True)
            visible_texts = filter(self.tag_visible, texts)                
            text_from_html = u" ".join(t.strip() for t in visible_texts)
               
            X_test = np.array([text_from_html])

            self.niveLock.acquire()
            X_test_cv = self.cv.transform(X_test)
            predictions = self.naive_bayes.predict(X_test_cv)
            self.niveLock.release()

            Class = int(predictions[0])


            paragraph=""
            p=soup.find("p")
            if p != None :
                paragraph = p.text.strip()
            while len(paragraph)==0 :
                if p == None or p.find_next("p")==None:
                    break
                p=p.find_next("p")
                paragraph = p.text.strip()

            if len(paragraph) > 255 :
                paragraph = paragraph[:255] + "..."
            keywords = title
            for heading in soup.find_all("h1"):
                keywords = keywords + ' ' + heading.text.strip()


            for tag in soup.find_all('meta'):
                if 'name' in tag.attrs.keys() and tag.attrs['name'].strip().lower() in ['description', 'keywords']:
                    
                    keywords = keywords + ' ' + tag.attrs['content'].strip()



            sql = "INSERT INTO sites (class,url,title,keywords,first_par) VALUES (%s,%s, %s,%s,%s)"
            val = ( Class,murl,title , keywords,paragraph)

            try:

                connection_object = self.connection_pool.get_connection()
                if connection_object.is_connected():
                   # db_Info = connection_object.get_server_info()
                   # print("Connected to MySQL database using connection pool ... MySQL Server version on ",db_Info)

                   cursor = connection_object.cursor()
                   cursor.execute(sql, val)
                   connection_object.commit()
                   # record = cursor.fetchone()
                   # print ("Your connected to - ", record)

            except Error as err:

                    print(err)
                    # print("Error Code:", err.errno)
                    # print("SQLSTATE", err.sqlstate)
                    # print("Message", err.msg)

            finally:

                if(connection_object.is_connected()):
                    cursor.close()
                    connection_object.close()
                    #print("MySQL connection is closed")

        
        # links = soup.find_all('a', href=True)
        # for link in links:
        #     url = link['href']

        #     if url.startswith('//') or url.startswith(self.root_url):
        #         url = urljoin(self.root_url, url)
        #     elif url.startswith('#') or url.startswith('/'):
        #         #print(url)
        #         continue
        #     if url not in self.scraped_pages:
        #         self.to_crawlLock.acquire()
        #         self.to_crawl.put(url)
        #         self.to_crawlLock.release()

        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                # href empty tag
                continue
            href = urljoin(murl, href)
            parsed_href = urlparse(href)
            # remove URL GET parameters, URL fragments, etc.
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if not self.is_valid(href):
                # not a valid URL
                continue
            if href not in self.scraped_pages and href.startswith(self.root_url):
                self.to_crawlLock.acquire()
                self.to_crawl.put(href)
                self.to_crawlLock.release()





    def scrape_page(self, url):
        try:
            res = requests.get(url, timeout=(3, 30))
            
        except requests.RequestException:
            return
        if res and res.status_code == 200 and ("text/html" in res.headers["content-type"] or "application/pdf" in res.headers["content-type"] ):
            self.parse_links_info(res.text,url)
            
        return res


    def run_scraper(self):
        i=0
        with self.pool as ex :
            while i<1:
                try:
                    target_url = self.to_crawl.get(timeout=20)
                    if target_url not in self.scraped_pages :
                        i=i+1
                        #print(i,"Scraping URL: {}".format(target_url))
                        self.scraped_pages.add(target_url)
                        job = ex.submit(self.scrape_page, target_url)
                        
                except Empty:
                    return
                except Exception as e:
                    print(e)
                    continue
if __name__ == '__main__':

    s = MultiThreadScraper("https://www.w3schools.com/html/")
    s.run_scraper()
#print("--- %s seconds ---" % (time.time() - start_time))
    #print(s.root_url)
