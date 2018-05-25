import crawler
import os
from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from collections import deque
import random

TEMPLATE_DIR = os.path.abspath('templates')
STATIC_DIR = os.path.abspath('static')
app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='/static')

@app.route('/')
def form():
    return send_file('templates/index.html')

@app.route('/results')
def redirect_to_home():
    return redirect(url_for('form'))

@app.route('/<path:template>.html')
def send_template(template):
    template_file = '{}.html'.format(os.path.join(TEMPLATE_DIR,template))
    return send_file(template_file)


@app.route('/process-options', methods=['POST'])
def process_options():
    options_data = {}
    options_data["website"] = request.form.get("website")

    #validate traversal method
    if request.form.get("traversal") == "breadth" or request.form.get("traversal") == "depth":
        options_data["traversal"] = request.form.get("traversal")
    else:
        return 'Invalid traversal method', 400

    #validate step number    
    try:
        options_data["steps"] = int(request.form.get("steps"))
        if options_data["steps"] > 5 or options_data["steps"] < 1:
            return 'Steps out of range', 400
    except ValueError:
        return 'Steps is not a valid value', 400

    options_data["keyword"] = request.form.get("keyword")
    if options_data["keyword"] == "":
        options_data["keyword"] = None

    try:
        crawler = Crawler(options_data)
        result = crawler.start()
        # result = crawler.startCrawl(options_data)
    except ValueError:
        #invalid url
        return 'Invalid URL provided', 400
    print(jsonify(result))
    return jsonify(result), 200

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]', 'p']:
        return False
    if isinstance(element, Comment):
        return False
    return True

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
    except requests.exceptions.HTTPError:
        # raise ValueError
        pass


if __name__ == '__main__':
    app.run(debug=True)
