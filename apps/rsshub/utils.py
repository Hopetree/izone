# -*- coding: utf-8 -*-
from datetime import datetime


class RSSResponse(object):
    def __init__(self, title='', link='', items=None):
        self.title = title
        self.link = link
        self.items = items or []
        self.update = datetime.now().strftime("%a, %d %b %Y %H:%M:%S") + ' +0800'

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def as_dict(self):
        data = {
            'title': self.title,
            'link': self.link,
            'update': self.update,
            'items': self.items
        }
        return data
