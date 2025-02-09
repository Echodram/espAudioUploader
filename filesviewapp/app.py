from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

BASE_DIRECTORY = 'shared'

@app.route('/')
def index():
    return list_files(BASE_DIRECTORY)

@app.route('/files')
def list_files(directory):
    items = os.listdir(directory)
    files = [item for item in items if os.path.isfile(os.path.join(directory, item))]
    folders = [item for item in items if os.path.isdir(os.path.join(directory, item))]
    return render_template('index.html', files=files, folders=folders, current_directory=directory)

@app.route('/files/<path:filename>')
def download_file(filename):
    return send_from_directory(os.path.dirname(filename), os.path.basename(filename), as_attachment=True)

@app.route('/folder/<path:foldername>')
def open_folder(foldername):

    directory = os.path.join(BASE_DIRECTORY, foldername)
    return list_files(directory)

if __name__ == '__main__':
    app.run(debug=True)