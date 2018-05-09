import os
from flask import Flask, render_template, request, send_file

TEMPLATE_DIR = os.path.abspath('templates')
STATIC_DIR = os.path.abspath('static')
app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='/static')

@app.route('/')
def form():
    print(TEMPLATE_DIR)
    return send_file('templates/index.html')

@app.route('/<path:template>.html')
def send_template(template):
    template_file = '{}.html'.format(os.path.join(TEMPLATE_DIR,template))
    print(template_file, flush=True)
    return send_file(template_file)
 
@app.route('/process-options', methods=['POST'])
def process_options():
    options_data = {}
    options_data["website"] = request.form.get("website")
    # validate_website()
    options_data["traversal"] = request.form.get("traversal")
    options_data["steps"] = request.form.get("steps")
    options_data["keyword"] = request.form.get("keyword")

    # run_crawler(options_data)
    print(options_data)
    return '', 200



if __name__ == '__main__':
    app.run(debug=True)