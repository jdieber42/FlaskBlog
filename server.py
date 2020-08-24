import sqlite3
from sqlite3 import Error
from flask import Flask, render_template, redirect, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'


class BlogForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    text = TextAreaField('Text', validators=[DataRequired()])
    submit = SubmitField('Create')


""" ---------- web routing part ---------- """


@app.route('/create', methods=['GET', 'POST'])
def login():
    form = BlogForm()
    if form.validate_on_submit():
        # the transformation from data into blog data and vice versa could be solved better
        insert_blog({'title': form.title.data, 'text': form.text.data, 'author': form.author.data})
        return redirect('/blogs')
    return render_template('create.html', title='Create Blog', form=form)


@app.route('/delete/<int:blog_id>')
def delete(blog_id):
    delete_blog_by_id(blog_id)

    return redirect('/blogs')


@app.route('/')
@app.route('/blogs')
def blogs():
    posts = get_all_blogs()

    return render_template('blogs.html', posts=posts)


@app.route('/blog/<int:blog_id>')
def blogpost(blog_id):
    post = get_blog_by_id(blog_id)

    return render_template('single.html', post=post)


@app.route('/contact')
def contact():
    return render_template('contact.html')


""" ---------- database part ---------- """


def create_connection():
    """ create a database connection to a SQLite database
    :return:
    """
    conn = None
    try:
        conn = sqlite3.connect(r"db\blog.db")
        print(sqlite3.version)
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def setup_db():
    """ sets up the database by using the create statements
    :return:
    """

    sql_create_blogs_table = """ CREATE TABLE IF NOT EXISTS blogs (
                                id integer PRIMARY KEY AUTOINCREMENT,
                                title text NOT NULL,
                                text text NOT NULL,
                                author text NOT NULL,
                                blog_date timestamp
                            ); """
    try:
        conn = create_connection()
        # create tables
        if conn is not None:
            # create projects table
            create_table(conn, sql_create_blogs_table)

            # add some test blogs for the showcase if there aren't any
            blogs = get_all_blogs()
            if blogs is not None and len(blogs) == 0    :
                insert_blog({'title': 'Create a new Flask Blog',
                             'text': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Molestiae ut ratione similique temporibus tempora dicta soluta? Qui hic, voluptatem nemo quo corporis dignissimos voluptatum debitis cumque fugiat mollitia quasi quod. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Molestiae ut ratione similique.',
                             'author': 'Jörg Dieber'})
                insert_blog({'title': 'I used a template for this blog',
                             'text': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Molestiae ut ratione similique temporibus tempora dicta soluta? Qui hic, voluptatem nemo quo corporis dignissimos voluptatum debitis cumque fugiat mollitia quasi quod. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Molestiae ut ratione similique.',
                             'author': 'Jörg Dieber'})
                insert_blog({'title': 'The persitance was done with sqlight',
                             'text': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Molestiae ut ratione similique temporibus tempora dicta soluta? Qui hic, voluptatem nemo quo corporis dignissimos voluptatum debitis cumque fugiat mollitia quasi quod. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Molestiae ut ratione similique.',
                             'author': 'Jörg Dieber'})
                insert_blog({'title': 'I hope this is the example you wanted',
                             'text': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Molestiae ut ratione similique temporibus tempora dicta soluta? Qui hic, voluptatem nemo quo corporis dignissimos voluptatum debitis cumque fugiat mollitia quasi quod. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Molestiae ut ratione similique.',
                             'author': 'Jörg Dieber'})
                insert_blog({'title': 'DB Getting Start',
                             'text': 'It creates some test blog entries if the database does not contain any blog entries. You can also reset the database by deleting the file db/blog.db.',
                             'author': 'Jörg Dieber'})
        else:
            print("Error! Cannot create blogs table.")
    except Error as e:
        print(e)
    finally:
        conn.close()


def insert_blog(blog):
    """
    Create a new blog entry into the blogs table
    :param blog:
    :return: blog id
    """
    sql = ''' INSERT INTO blogs(title,text,author,blog_date)
              VALUES(?,?,?,datetime('now')) '''
    try:
        conn = create_connection()

        if conn is not None:
            cur = conn.cursor()
            cur.execute(sql, (str(blog['title']), str(blog['text']), str(blog['author'])))
            conn.commit()
        else:
            print("Error! Cannot create blog entry into database.")
    except Error as e:
        print(e)
    finally:
        conn.close()
    return cur.lastrowid


def get_all_blogs():
    """
    Query all rows in the blogs table
    :return: All blog entries from the database.
    """
    blogs = []
    try:
        conn = create_connection()

        if conn is not None:
            cur = conn.cursor()
            cur.execute("SELECT id,title,text,author,blog_date FROM blogs order by id desc")

            rows = cur.fetchall()
            for row in rows:
                blogs.append({'id': row[0], 'title': row[1], 'text': row[2], 'author': row[3], 'blog_date': row[4]})
        else:
            print("Error! Cannot load blog entries from database.")
    except Error as e:
        print(e)
    finally:
        conn.close()

    return blogs


def delete_blog_by_id(id):
    """
    :param id: The database id of the blog to delete.
    Delete the blog with the given id.
    :return: The blog entry with the given id.
    """
    blog = None
    try:
        conn = create_connection()
        if conn is not None:
            cur = conn.cursor()
            cur.execute("DELETE FROM blogs where id=?", (id,))
            conn.commit()

        else:
            print("Error! Cannot delete single blog entry from database with id: " + str(id))
    except Error as e:
        print(e)
    finally:
        conn.close()
    return blog


def get_blog_by_id(id):
    """
    :param id: The database id of the blog to fetch.
    Query all rows in the blogs table
    :return: The blog entry with the given id.
    """
    blog = None
    try:
        conn = create_connection()
        if conn is not None:
            cur = conn.cursor()
            cur.execute("SELECT id,title,text,author,blog_date FROM blogs where id=?", (id,))

            row = cur.fetchone()

            if row:
                blog = {'id': row[0], 'title': row[1], 'text': row[2], 'author': row[3], 'blog_date': row[4]}
        else:
            print("Error! Cannot load single blog entry from database with id: " + str(id))
    except Error as e:
        print(e)
    finally:
        conn.close()
    return blog


if __name__ == '__main__':
    setup_db()
    app.run()
