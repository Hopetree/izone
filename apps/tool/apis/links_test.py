# -*- coding: utf-8 -*-
import requests

def check_links(urls,p):
    ret = dict()
    links = urls.split('\n')
    for link in links:
        try:
            html = requests.get(link,timeout=4).text
        except:
            ret[link] = 'bad link'
        else:
            s = html.find(p)
            if s > -1:
                ret[link] = 'true'
            else:
                ret[link] = 'false'
    return ret

if __name__ == '__main__':
    u = 'shai\nshooooooo\nhttp://www.stopfollow.com/\nhttps://tool.lu/'
    p = 'href="http://www.miibeian.gov.cn/"'
    check_links(u,p)
