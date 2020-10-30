import os
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

auth = HTTPBasicAuth()

app.secret_key = 'sasdfdfsw322'

UPLOAD_FOLDER = os.environ.get('UPLOAD_PATH')

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

username = os.environ.get('LOGIN')

password = os.environ.get('PASSWORD')

users = {
    username: generate_password_hash(password)
}


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if username == '' or password == '':
    @app.route('/')
    def none_var():
        return ("не заданы переменные окружения")


@app.route('/')
@auth.login_required
def hello():
    flash('hello')
    list_of_files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        list_of_files.append(filename)
    return render_template("index.html",
                           list_of_files=list_of_files,
                           UPLOAD_FOLDER=UPLOAD_FOLDER)


@app.route('/upload', methods=['GET', 'POST'])
@auth.login_required
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            print(file.filename)
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('upload_file',
                                    filename=filename))
        else:
            flash('not allowed file')
            return redirect(request.url)
    return render_template("form.html")


@app.route('/files/<path:filename>', methods=['GET', 'POST'])
@auth.login_required
def download(filename):
    return send_from_directory(directory=UPLOAD_FOLDER, filename=filename)
