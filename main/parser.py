from bs4 import BeautifulSoup
import re
from flask import Markup

def parse(text):
    soup = BeautifulSoup(text, 'html.parser')
    list_all_allowed = soup.find_all('b')
    list_all_allowed += soup.find_all('em')
    for i in range(1,6):
        list_all_allowed += soup.find_all(f'h{i}')
    list_all = soup.find_all()
    for tag in list_all:
        if not tag in list_all_allowed:
            tag.replaceWith(Markup.escape(tag))
        else:
            tag.attrs.clear()
        
    return Markup(soup)
