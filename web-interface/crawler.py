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


nodesPerLevel = 10
nodesMaxDepth = 10
nodesTotalMax = 20
searchKeyWord = 'support'
nodesDict = {}
result = {}


def startCrawl(options_data):
    global result
    global nodesPerLevel
    global nodesMaxDepth
    global nodesTotalMax
    global nodesDict

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

    # f = open('static/data.json', 'w')
    # print(json.dumps(result), file=f)
    with open('static/data.json', 'w') as f:
        json.dump(result, f)
        f.close()
    return result

def appendNode(parentNode, childNode, depth):
    global result
    global nodesDict
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

if __name__ == "__main__":
    options_data = {
        "website": "www.google.com",
        "traversal": "breadth",
        "steps": 2,
    }
    startCrawl(options_data)
