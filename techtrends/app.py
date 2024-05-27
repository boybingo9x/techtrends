import sqlite3
import os
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
import sys

logging.basicConfig(
    level=logging.DEBUG,  # Set the desired log level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Define the log format
    stream=sys.stdout  # Output logs to STDOUT
)
logging.captureWarnings(True)

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    app.config['connection_count'] = app.config['connection_count'] + 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['connection_count'] = 0
# app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        logging.error('Article with id %s does not exist!',post_id)
        return render_template('404.html'), 404
    else:
        logging.debug('Article %s retrieved!',post["title"])
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logging.debug("About page rendered!")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            logging.debug('Article %s created!',title)
            return redirect(url_for('index'))

    return render_template('create.html')

# Define healthz endpoint
@app.route('/healthz')
def healthz():
    try:
        connection = get_db_connection()
        connection.cursor()
        connection.execute("SELECT * FROM posts")
        connection.close()
        return {"result": "OK - healthy"}
    except Exception:
        return {"result": "ERROR - unhealthy"}, 500

# Define metrics endpoint
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute("SELECT * FROM posts").fetchall()
    connection.close()
    post_count = len(posts)
    data = {"db_connection_count": app.config['connection_count'], "post_count": post_count}
    return data

def initialize_logger():
    log_level = os.getenv("LOGLEVEL", "DEBUG").upper()
    log_level = (
        getattr(logging, log_level)
        if log_level in ["CRITICAL", "DEBUG", "ERROR", "INFO", "WARNING",]
        else logging.DEBUG
    )

    logging.basicConfig(
        format='%(levelname)s:%(name)s:%(asctime)s, %(message)s',
                level=log_level,
    )

# start the application on port 3111
if __name__ == "__main__":
    ## stream logs to a file
    initialize_logger()
    app.run(host='0.0.0.0', port='3111', debug=True)
