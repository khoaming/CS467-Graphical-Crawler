import random
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from collections import deque

def tagVisible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def prependHttp(url):
    if not url.startswith('http'):
        url = 'http://' + url
    return url

def tryUrl(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
        }
        page = requests.get(url, headers=headers)
        page.raise_for_status()
        soup = BeautifulSoup(page.text, "lxml")
        return soup
    except (requests.HTTPError, requests.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException) as e: # skip unreadable urls
        raise ValueError

class Node:

    def __init__(self, id, title, url, depth):
        self.id = id
        self.title = title
        self.url = url
        self.depth = depth

class Crawler:

    def __init__(self, options_data):
        self.startUrl = prependHttp(options_data.get('website'))
        self.mode = options_data.get('traversal')
        self.steps = options_data.get('steps')
        self.keyWord = options_data.get('keyword')
        self.toCrawl = deque([])
        self.result = {'nodes': [], 'links': []}
        self.visited = []
        self.numNodes = 0

    def start(self):
        startNode = Node(self.numNodes, 'Start', self.startUrl, 0)
        self.appendNode(startNode, startNode)

        if self.mode == 'breadth':
            self.bfs()
        if self.mode == 'depth':
            self.dfs()

        return (self.result)

    def bfs(self):
        while len(self.toCrawl) > 0:
            cur = self.toCrawl.popleft()

            if cur.depth == self.steps: return

            url = prependHttp(cur.url)
            try:
                soup = tryUrl(url)

                if self.keyWord and self.foundKeyWord(cur, soup): return

                links = soup.findAll("a", href=True)
                self.visited.append(cur.url)
            except ValueError:
                pass
            # crawl all unvisited links
            for link in links:
                if link.get('href') and link.get('href').startswith('http'):
                    title = link.string
                    url = link['href']
                    if url not in self.visited:
                        childNode = Node(self.numNodes, title, url, cur.depth + 1)
                        self.appendNode(cur, childNode)

    def dfs(self):
        while len(self.toCrawl) > 0:
            cur = self.toCrawl.popleft()

            if cur.depth == self.steps: return
            url = prependHttp(cur.url)
            try:
                soup = tryUrl(url)
                if self.keyWord and self.foundKeyWord(cur, soup): return

                links = soup.findAll("a", href=True)
                self.visited.append(cur.url)
            except ValueError:
                pass

            gotLink = False
            #remove all links without http
            links = [link for link in links if link.get('href') and link.get('href').startswith('http')]
            # find a random link that has not been visited and crawl it
            while not gotLink:
                if not len(links): # in case there is no link
                    break
                i = random.randint(0, len(links) - 1)
                link = links[i]
                if link.get('href') and link.get('href').startswith('http'):
                    title = link.string
                    url = link['href']
                    if url not in self.visited:
                        childNode = Node(self.numNodes, title, url, cur.depth + 1)
                        self.appendNode(cur, childNode)
                        gotLink = True

    def foundKeyWord(self, cur, soup):
        texts = soup.findAll(text=True)
        visible_texts = filter(tagVisible, texts)

        for t in visible_texts:
            if self.keyWord.lower() in t.strip().lower():
                self.result['keyword_node'] = cur.id
                return True
        return False

    def appendNode(self, parentNode, childNode):
        self.numNodes += 1
        self.toCrawl.append(childNode)

        title = childNode.title if childNode.title else 'No Title'
        self.result['nodes'].append({
            'id': childNode.id,
            'url': childNode.url,
            'title': title,
            'depth': childNode.depth
        })

        if parentNode.id != childNode.id:
            self.result['links'].append({
                'source': parentNode.id,
                'target': childNode.id,
                'distance': childNode.depth - parentNode.depth
            })
