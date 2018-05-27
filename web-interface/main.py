import os
from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
import crawler

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
        crawler_obj = crawler.Crawler(options_data)
        result = crawler_obj.start()
    except ValueError:
        #invalid url
        return 'Invalid URL provided', 400
    print(jsonify(result))
    return jsonify(result), 200


if __name__ == '__main__':
    app.run(debug=True)
