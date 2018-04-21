import json
import requests
from bs4 import BeautifulSoup


class Node:
    counter = 0

    def __init__(self, title, url):
        self.id = Node.counter
        self.title = title
        self.url = url
        self.links = []
        Node.counter += 1


startUrl = "https://jsonformatter.curiousconcept.com/"
limit = 1
page = requests.get(startUrl)
soup = BeautifulSoup(page.content, "html.parser")
links = soup.findAll("a")
result = {'node': []}


def appendNode(parentNode, childNode):
    result['node'].append({
        'id': childNode.id,
        'title': childNode.title,
        'url': childNode.url,
        'links': childNode.links
    })
    result['node'][parentNode.id]['links'].append(childNode.id)

def crawlPage(parentNode, limit):
    if not limit > 0:
        return
    page = requests.get(parentNode.url)
    soup = BeautifulSoup(page.content, "html.parser")
    links = soup.findAll("a")
    nodesFound = []
    for link in links:
        # print("\n")
        # print(link)
        if  link.get('href') and link.get('href').startswith('http'):
            title = link.string
            url = link['href']
            currentNode = Node(title, url)
            # print(currentNode.id)
            # print(currentNode.title)
            # print(currentNode.url)
            appendNode(parentNode, currentNode)
            nodesFound.append(currentNode)
    for node in nodesFound:
        crawlPage(node, limit-1)

startNode = Node('Start', startUrl)
appendNode(startNode, startNode)
crawlPage(startNode, limit)


print(json.dumps(result))
