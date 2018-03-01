# -*- coding: utf-8 -*-
import requests
import threading


class Check(object):
    def __init__(self, urls, p):
        self.urls = set(urls.split('\n'))
        self.p = p
        self.dic = dict()
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 5.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
        self.lock = threading.Lock()

    def check_one(self, url):
        try:
            html = requests.get(url, headers=self.headers, timeout=4).text
        except:
            self.lock.acquire()
            self.dic[url] = 'bad url'
        else:
            s = html.find(self.p)
            self.lock.acquire()
            self.dic[url] = 'true' if s > -1 else 'false'
        self.lock.release()

    def run(self):
        threads = []
        for url in self.urls:
            if url != '':
                t = threading.Thread(target=self.check_one, args=(url,))
                threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return self.dic


if __name__ == '__main__':
    u = 'shai\nshooooooo\nhttp://www.stopfollow.com/\nhttps://tool.lu/'
    p = 'href="http://www.miibeian.gov.cn/"'
    k = Check(u,p)
    print(k.run())

