"""
pageLinks: a list of links to news pages
extLinks: a list of links to web pages which hopefully direct to more news pages
"""

from html.parser import HTMLParser
import re
import urllib.request
import urllib.error
import random


class ParseState:
    READ_LINK = 1
    READ_DATA = 2
    READ_ALL = 3


class LinkCategory:
    USELESS = 0
    DATA_LINK = 1
    EXT_LINK = 2


class BlockType:
    NULL = 0
    TITLE = 1
    CONTENT = 8
    CONTENT_TEXT = 9
    CONTENT_IMG_TEXT = 10
    CONTENT_STRONG = 11


class Crawler(HTMLParser):

    prefix_count = {}
    junk_prefix = set()

    def __init__(self):
        super().__init__()
        self.pageLinks = set()
        self.extLinks = set()
        self.data = {}
        self.extended = []
        self.useful_page = set()
        self.useful_ext = set()
        self.address = ''
        self.state = ParseState.READ_ALL
        self.currentType = BlockType.NULL
        self.metaNames = ["keywords", "description", "publishdate"]

    def read_rand(self):
        """
        read a random link in self.pageLinks
        """
        self.address = self.pageLinks.pop()
        while self.address in self.data:
            self.address = self.pageLinks.pop()
        self.data[self.address] = {"content": ""}
        page = urllib.request.urlopen(self.address, timeout=1)

        self.state = ParseState.READ_ALL
        s = page.read()
        d = s.decode('gbk')
        self.useful_page = set()
        self.useful_ext = set()
        self.feed(d)
        if self.state & ParseState.READ_LINK:
            self.store_links()

    def extend(self):
        """
        read a page from self.extLinks and extract its links
        """
        self.address = self.extLinks.pop()
        while self.address in self.extended:
            self.address = self.extLinks.pop()
        self.extended.append(self.address)
        page = urllib.request.urlopen(self.address, timeout=1)

        self.state = ParseState.READ_LINK
        s = page.read()
        d = s.decode('gbk')
        self.useful_page = set()
        self.useful_ext = set()
        self.feed(d)
        self.store_links()

    def store_links(self):
        if len(self.useful_page) >= 5:
            self.pageLinks |= self.useful_page
            self.extLinks |= self.useful_ext

    def error(self, message):
        print(message)

    def handle_starttag(self, tag, attr):
        if self.state & ParseState.READ_LINK:
            for (key, val) in attr:
                if key == 'href':
                    if len(val) <= 1:
                        continue
                    link = self.format_link(val)
                    cat = Crawler.categorize_link(link)
                    if cat == LinkCategory.DATA_LINK and \
                            link not in self.data and \
                            link not in self.pageLinks:
                        self.useful_page.add(link)
                    elif cat == LinkCategory.EXT_LINK and \
                            link not in self.extended and \
                            link not in self.extLinks:
                        self.useful_ext.add(link)

        if self.state & ParseState.READ_DATA:
            attributes = {k: v for (k, v) in attr}
            if tag == "meta":
                if "name" in attributes and attributes["name"] in self.metaNames:
                    self.data[self.address][attributes["name"]] = attributes["content"]
            elif tag == "title":
                self.currentType = BlockType.TITLE
            elif tag == "div":
                if "class" in attributes:
                    classes = attributes["class"].split(" ")
                    if "text_con" in classes or "content" in classes:
                        self.currentType = BlockType.CONTENT
                    elif "banner02" in classes or "edit" in classes or "box_down" in classes:
                        self.currentType = BlockType.NULL
            elif tag == "p" and (self.currentType & BlockType.CONTENT):
                if "class" in attributes and "pictext" in attributes["class"].split(" "):
                    self.currentType = BlockType.CONTENT_IMG_TEXT
                else:
                    self.currentType = BlockType.CONTENT_TEXT
            elif tag == "strong" and (self.currentType & BlockType.CONTENT):
                self.currentType = BlockType.CONTENT_STRONG

    def handle_endtag(self, tag):
        if (self.state & ParseState.READ_DATA) and (self.currentType & BlockType.CONTENT):
            self.currentType &= BlockType.CONTENT_TEXT
        else:
            self.currentType = BlockType.NULL

    def handle_data(self, data):
        if self.currentType == BlockType.TITLE:
            data = Crawler.format_data(data)
            if len(data) <= 1:
                return
            self.data[self.address]["title"] = data
        elif self.currentType == BlockType.CONTENT_TEXT:
            data = Crawler.format_data(data)
            if len(data) <= 1:
                return
            self.data[self.address]["content"] += data + "\n"
        elif self.currentType == BlockType.CONTENT_IMG_TEXT:
            data = Crawler.format_data(data)
            if len(data) <= 1:
                return
            self.data[self.address]["content"] += "图片：" + data + "\n"
        elif self.currentType == BlockType.CONTENT_STRONG:
            data = Crawler.format_data(data)
            if len(data) <= 1:
                return
            self.data[self.address]["content"] += "<strong>" + data + "</strong>" + "\n"

    def format_link(self, link):
        if '\\' in link:
            l = link.split('\\')
            for i in range(1, len(l)):
                l[i] = l[i][1:]
            link = ''.join(l)
        if link[0] == '/':
            link = re.findall(r"^http://[^/]+", self.address)[0] + link
        return link

    @staticmethod
    def extract_prefix(link):
        return re.sub(r'http://([^.]+)\..+', r'\1', link)

    @staticmethod
    def format_data(data):
        return re.sub(r"[\n\s]", "", data)

    @staticmethod
    def categorize_link(link):
        """
        returns:
        0 for useless link
        1 for link to other news
        2 for link to root pages
        """
        if re.fullmatch(r"http://\w+\.people\.com\.cn/n\d/\d+/\d+/.\d+-\d+\.html?",
                        link):
            # if re.match(r"http://(renshi|leaders|bbs|health|www|pic|capital|hlj)", link):
            #     return LinkCategory.USELESS
            # elif re.match(r"http://..\.", link):
            #     return LinkCategory.USELESS
            if Crawler.extract_prefix(link) in Crawler.junk_prefix:
                return LinkCategory.USELESS
            return LinkCategory.DATA_LINK
        elif re.fullmatch(r"http://.+\.people\.com\.cn/?.*/", link):
            return LinkCategory.EXT_LINK
        else:
            return LinkCategory.USELESS
