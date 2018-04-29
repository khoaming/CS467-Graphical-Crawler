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


startUrl = "https://jsonformatter.curiousconcept.com/"
limit = 1
nodesPerLevel = 10
page = requests.get(startUrl)
soup = BeautifulSoup(page.content, "html.parser")
links = soup.findAll("a")
result = {'nodes': [], 'links': []}


def appendNode(parentNode, childNode, group):
    result['nodes'].append({
        'id': childNode.id,
        'url': childNode.url,
        'title': childNode.title,
        'group': group
    })
    # result['nodes'][parentNode.id]['links'].append(childNode.id)

def crawlPage(parentNode, limit, group):
    if not limit > 0:
        return
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
            appendNode(parentNode, currentNode, group)
            nodesFound.append(currentNode)
    for node in nodesFound:
        crawlPage(node, limit-1, group+1)

startNode = Node('Start', startUrl)
appendNode(startNode, startNode, 1)
crawlPage(startNode, limit, 2)


print(json.dumps(result))
