import json
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]', 'p']:
        return False
    if isinstance(element, Comment):
        return False
    return True

class Node:
    counter = 0

    def __init__(self, title, url):
        self.id = Node.counter
        self.title = title
        self.url = url
        Node.counter += 1


startUrl = "https://www.imdb.com/"
limit = 1   # Used for breadth search, depth level
mode = 2    # 1 = breadth search, 2 = depth search
nodesPerLevel = 10
nodesMaxDepth = 10
nodesTotalMax = 20
searchKeyWord = 'support'
page = requests.get(startUrl)
soup = BeautifulSoup(page.content, "lxml")
links = soup.findAll("a")
result = {'nodes': [], 'links': []}
nodesDict = {}

if mode == 1:
    nodesPerLevel = 10  # breadth search, max 10 child nodes linked to parent node
if mode == 2:
    nodesPerLevel = 2   # depth search, max children nodes linked to parent node
    nodesMaxDepth = 10  # depth search, max nodes of depth
    limit = 20


def appendNode(parentNode, childNode, depth):
    result['nodes'].append({
        'id': childNode.id,
        'url': childNode.url,
        'title': childNode.title,
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

def crawlPage(parentNode, limit, depth):
    # print("CRAW PAGE: " + parentNode.url)
    if not limit > 0 and mode == 1:
        # print("limit > 0")
        return
    if depth > nodesMaxDepth and mode == 2:
        # print("depth > nodesMaxDepth")
        return
    if len(nodesDict) >= nodesTotalMax:
        # print(">= nodesTotalMax")
        return
    # print(parentNode.id)
    # print(limit)
    # print(depth)
    page = requests.get(parentNode.url)
    # print(page.content)
    soup = BeautifulSoup(page.content, "lxml")
    links = soup.findAll("a")
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    # print(u" ".join(t.strip() for t in visible_texts))
    for t in visible_texts:
        if searchKeyWord and searchKeyWord in t.strip():
            # print(parentNode.url)
            # print(t.strip())
            # print("FOUND KEYWORD")
            parentNode.keyword = searchKeyWord
            result['keyword_node'] = parentNode.id
            return

    nodesFound = []
    global nodesPerLevel
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
            if mode == 2:   # Depth search
                # print("Should crawl page: " + currentNode.url)
                crawlPage(currentNode, limit-1, depth+1)
    if mode == 1:   # Breadth search
        for node in nodesFound:
            crawlPage(node, limit-1, depth+1)

startNode = Node('Start', startUrl)
appendNode(startNode, startNode, 1)
crawlPage(startNode, limit, 2)


print(json.dumps(result))
