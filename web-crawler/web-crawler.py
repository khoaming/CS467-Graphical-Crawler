import json
import requests
from bs4 import BeautifulSoup


class Node:
    counter = 0

    def __init__(self, title, url):
        self.id = Node.counter
        self.title = title
        self.url = url
        Node.counter += 1


startUrl = "http://oregonstate.edu//"
limit = 1   # Used for breadth search, depth level
mode = 2    # 1 = breadth search, 2 = depth search
nodesPerLevel = 10
nodesMaxDepth = 3
searchKeyWord = ''
page = requests.get(startUrl)
soup = BeautifulSoup(page.content, "html.parser")
links = soup.findAll("a")
result = {'nodes': [], 'links': []}

if mode == 1:
    nodesPerLevel = 10  # breadth search, max 10 child nodes linked to parent node
if mode == 2:
    nodesPerLevel = 1   # depth search, max 1 child node linked to parent node
    nodesMaxDepth = 20  # depth search, max nodes of depth
    limit = 20


def appendNode(parentNode, childNode, depth):
    result['nodes'].append({
        'id': childNode.id,
        'url': childNode.url,
        'title': childNode.title,
        'depth': depth
    })
    if parentNode.id != childNode.id:
        result['links'].append({
            'source': parentNode.id,
            'target': childNode.id,
            'distance':result['nodes'][childNode.id]['depth'] - result['nodes'][parentNode.id]['depth']
        })

def crawlPage(parentNode, limit, depth):
    if not limit > 0 and mode == 1:
        return
    if depth > nodesMaxDepth and mode == 2:
        return
    # print(parentNode.id)
    # print(limit)
    # print(depth)
    page = requests.get(parentNode.url)
    soup = BeautifulSoup(page.content, "html.parser")
    links = soup.findAll("a")
    nodesFound = []
    global nodesPerLevel
    for link in links:
        if len(nodesFound) >= nodesPerLevel:
            break
        if  link.get('href') and link.get('href').startswith('http'):
            title = link.string
            url = link['href']
            currentNode = Node(title, url)
            appendNode(parentNode, currentNode, depth)
            nodesFound.append(currentNode)
            if mode == 2:   # Depth search
                crawlPage(currentNode, limit-1, depth+1)
    if mode == 1:   # Breadth search
        for node in nodesFound:
            crawlPage(node, limit-1, depth+1)

startNode = Node('Start', startUrl)
appendNode(startNode, startNode, 1)
crawlPage(startNode, limit, 2)


print(json.dumps(result))
