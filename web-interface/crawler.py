import random
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from collections import deque
import multiprocessing, os
from invoke import run

def tagVisible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]', 'p']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def prependHttp(url):
    if not url.startswith('http'):
        url = 'http://' + url
    return url

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
        self.toCrawl = multiprocessing.Queue()
        self.result = {'nodes': [], 'links': []}
        self.visited = []
        self.numNodes = 0

    def start(self):
        print(self.startUrl)
        print(self.mode)
        print(self.steps)
        print(self.keyWord)

        os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
        run("echo $OBJC_DISABLE_INITIALIZE_FORK_SAFETY")
        startNode = Node(self.numNodes, 'Start', self.startUrl, 0)
        self.appendNode(startNode, startNode)

        if self.mode == 'breadth':
            p = multiprocessing.Process(target=self.bfs, args=(self.toCrawl,))
            p.start()
            p.join()
            # self.bfs()
        if self.mode == 'depth':
            self.dfs()

        print (self.result)
        return (self.result)

    def bfs(self, q):
        while not q.empty():
            cur = q.get()
            print("cur: " + cur.url)

            if cur.depth == self.steps: return

            url = prependHttp(cur.url)
            soup = self.tryUrl(url)
            print("depth: " + str(cur.depth))

            if self.keyWord and self.foundKeyWord(cur, soup): return
            print("cur: " + cur.url)

            links = soup.findAll("a", href=True)
            self.visited.append(cur.url)
            print("links: " + links)

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
            soup = tryUrl(url)

            if self.keyWord and self.foundKeyWord(cur, soup): return

            links = soup.findAll("a", href=True)
            self.visited.append(cur.url)

            gotLink = False

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
            if self.keyWord in t.strip():
                self.result['keyword_node'] = cur.id
                return True
        return False

    def appendNode(self, parentNode, childNode):
        self.numNodes += 1
        self.toCrawl.put(childNode)

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

    def tryUrl(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
            }
            print("HEADER")
            page = requests.get(url, headers=headers)
            # #check for valid domain
            # page.raise_for_status()
            # try:
            #     soup = BeautifulSoup(page.content, "lxml")
            #     return soup
            # except:
            #     pass
            print("PAGE")
            soup = BeautifulSoup(page.text, "lxml")
            return soup
        except: # skip unreadable urls
            pass
        # except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        #     raise ValueError
