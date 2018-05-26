import json
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from collections import deque
import random

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]', 'p']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def validateUrl(url):
    if not url.startswith('http'):
        url = 'http://' + url
    return url

def tryUrl(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
        }
        page = requests.get(url, headers=headers)
        #check for valid domain
        page.raise_for_status()
        return page.content
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        raise ValueError

class Node:
    counter = 0

    def __init__(self, id, title, url, depth):
        self.id = id
        self.title = title
        self.url = url
        self.depth = depth

class Crawler:

    def __init__(self, options_data):
        self.startUrl = options_data.get('website')
        self.mode = options_data.get('traversal')
        self.steps = options_data.get('steps')
        self.searchKeyWord = options_data.get('keyword')

    def start(self):
        self.toCrawl = deque([])
        self.result = {'nodes': [], 'links': []}
        self.visited = []
        self.numNodes = 0
        print(self.startUrl)
        print(self.mode)
        print(self.steps)
        print(self.searchKeyWord)

        startNode = Node(self.numNodes, 'Start', self.startUrl, 0)
        self.numNodes += 1
        self.appendNode(startNode, startNode)
        # newNode = Node(self.numNodes, 'dume', 'www.haha.com')
        # self.numNodes += 1
        # self.appendNode(startNode, newNode, 1)
        # crawlPage(mode, startNode, 1)
        if self.mode == 'breadth':
            self.bfs()
        if self.mode == 'depth':
            self.dfs()
        print (self.result)
        # print (self.visited)
        # print (self.toCrawl)
        return (self.result)

    def bfs(self):

        while len(self.toCrawl) > 0:
            cur = self.toCrawl.popleft()
            print (cur.url)
            print (cur.depth)
            if cur.depth == self.steps: return

            url = cur.url
            url = validateUrl(url)

            content = tryUrl(url)
            try:
                soup = BeautifulSoup(content, "lxml")
            except:
                pass

            links = soup.findAll("a")

            # print links
            self.visited.append(cur)
            for link in links:
                if link.get('href') and link.get('href').startswith('http'):
                    title = link.string
                    url = link['href']
                    if url not in self.visited:
                        childNode = Node(self.numNodes, title, url, cur.depth + 1)
                        self.numNodes += 1
                        self.appendNode(cur, childNode)

    def dfs(self):

        while len(self.toCrawl) > 0:
            cur = self.toCrawl.popleft()
            print (cur.url)
            print (cur.depth)
            if cur.depth == self.steps: return

            url = cur.url
            url = validateUrl(url)
            print (url)
            content = tryUrl(url)
            try:
                soup = BeautifulSoup(content, "lxml")
            except:
                pass

            links = soup.findAll("a")
            print(links)
            self.visited.append(cur)

            gotLink = False

            while not gotLink:
                i = random.randint(0, len(links) - 1)
                link = links[i]
                if link.get('href') and link.get('href').startswith('http'):
                    title = link.string
                    url = link['href']
                    print (url)
                    if url not in self.visited:
                        childNode = Node(self.numNodes, title, url, cur.depth + 1)
                        self.numNodes += 1
                        self.appendNode(cur, childNode)
                        gotLink = True

    def appendNode(self, parentNode, childNode):
        self.toCrawl.append(childNode)

        title = childNode.title if childNode.title else 'No Title'
        self.result['nodes'].append({
            'id': childNode.id,
            'url': childNode.url,
            'title': title,
            'depth': childNode.depth
        })
        # print("Appending " + childNode.url)
        # self.visited.append(childNode.url)

        if parentNode.id != childNode.id:
            # print parentNode.id
            # print childNode.id
            # print self.result['nodes'][childNode.id]['depth']
            # print self.result['nodes'][parentNode.id]['depth']
            self.result['links'].append({
                'source': parentNode.id,
                'target': childNode.id,
                'distance': childNode.depth - parentNode.depth
            })

nodesPerLevel = 10
nodesMaxDepth = 10
nodesTotalMax = 20
nodesDict = {}
result = {}

def startCrawl(options_data):
    global result
    global nodesPerLevel
    global nodesMaxDepth
    global nodesTotalMax
    global nodesDict
    global searchKeyWord

    startUrl = options_data.get('website')
    mode = options_data.get('traversal')
    steps = options_data.get('steps')
    searchKeyWord = options_data.get('keyword')

    print(startUrl)
    print(mode)
    print(steps)
    print(searchKeyWord)

    if not startUrl.startswith('http'):
        startUrl = 'http://' + startUrl
    if mode == 'breadth':
        nodesPerLevel = 30          # breadth search, max 30 child nodes linked to parent node
        nodesMaxDepth = 1 + steps   # depth search, max nodes of depth
        nodesTotalMax = 50
    if mode == 'depth':
        nodesPerLevel = 1           # depth search, max children nodes linked to parent node
        nodesMaxDepth = 1 + steps   # depth search, max nodes of depth
        nodesTotalMax = 20
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
        }
        page = requests.get(startUrl, headers=headers)
        #check for valid domain
        page.raise_for_status()
    except requests.exceptions.HTTPError:
        raise ValueError
    soup = BeautifulSoup(page.content, "lxml")
    links = soup.findAll("a")
    result = {'nodes': [], 'links': []}
    nodesDict = {}
    Node.counter = 0
    startNode = Node('Start', startUrl)
    appendNode(startNode, startNode, 1)
    crawlPage(mode, startNode, 2)
    return result

def appendNode(parentNode, childNode, depth):
    global result
    global nodesDict
    title = childNode.title if childNode.title else 'No Title'
    result['nodes'].append({
        'id': childNode.id,
        'url': childNode.url,
        'title': title,
        'depth': depth
    })
    # print("Appending " + childNode.url)
    nodesDict[childNode.url] = childNode
    if parentNode.id != childNode.id:
        result['links'].append({
            'source': parentNode.id,
            'target': childNode.id,
            'distance':result['nodes'][childNode.id]['depth'] - result['nodes'][parentNode.id]['depth']
        })

def crawlPage(mode, parentNode, depth):
    global nodesMaxDepth
    global nodesTotalMax
    global nodesPerLevel
    global result
    global nodesDict
    # print("CRAWL PAGE: " + parentNode.url)
    # if not limit > 0 and mode == 'breadth':
    #     # print("limit > 0")
    #     return
    if depth > nodesMaxDepth:
        # print("depth > nodesMaxDepth")
        return
    # if len(nodesDict) >= nodesTotalMax:
    #     # print(">= nodesTotalMax")
    #     return
    # print(parentNode.id)
    # print(limit)
    # print(depth)
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
    }
    page = requests.get(parentNode.url, headers=headers)
    # print(page.content)
    soup = BeautifulSoup(page.content, "lxml")
    links = soup.findAll("a")

    if searchKeyWord:
        texts = soup.findAll(text=True)
        visible_texts = filter(tag_visible, texts)
        # print(u" ".join(t.strip() for t in visible_texts))
        for t in visible_texts:
            if searchKeyWord in t.strip():
                # print(parentNode.url)
                # print(t.strip())
                # print("FOUND KEYWORD")
                # parentNode.keyword = searchKeyWord
                result['keyword_node'] = parentNode.id
                return

    nodesFound = []
    # print("Found links for url:" + parentNode.url)
    # print(links)
    for link in links:
        # print("Parent url:" + parentNode.url)
        # print("CHECKING LINK: " + str(link))
        # print( str(len(nodesFound)) + " >= " + str(nodesPerLevel))
        if len(nodesFound) >= nodesPerLevel:
            break
        if  link.get('href') and link.get('href').startswith('http'):
            title = link.string
            url = link['href']
            if url in nodesDict:        # Skip url already visited
                # print("already visited: " + url)
                continue
            currentNode = Node(title, url)
            appendNode(parentNode, currentNode, depth)
            nodesFound.append(currentNode)
            if mode == 'depth':   # Depth search
                # print("Should crawl page: " + currentNode.url)
                crawlPage(mode, currentNode, depth+1)
    if mode == 'breadth':   # Breadth search
        for node in nodesFound:
            crawlPage(mode, node, depth+1)

# if __name__ == "__main__":
#     options_data = {
#         "website": "www.google.com",
#         "traversal": "breadth",
#         "steps": 2,
#     }
#     startCrawl(options_data)
