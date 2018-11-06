from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import desc

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:Admin@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(120))
    body=db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title=title
        self.body=body

@app.route("/newpost", methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title=request.form['title']
        body=request.form.get('body')
        if title=="":

            title_error = "Please write title for the post."
            return redirect('/newpost?body='+body + '&title_error='+title_error)
        if body=="":
            body_error = "It should not be left empty."
            return redirect('/newpost?title=' +title + '&body_error='+body_error)

        db.session.add(Blog(title=title, body=body))
        
        db.session.commit()
        view=Blog.query.filter_by(title=title).order_by(desc(Blog.id)).first()
        blog_id=str(view.id)
        return redirect('/blog?id=' + blog_id)
    else:
        body = request.args.get('body')
        title = request.args.get('title')
        title_error=request.args.get('title_error')
        body_error = request.args.get('body_error')

        body='' if body is None else body
        title='' if title is None else title
        title_error='' if title_error is None else title_error
        body_error='' if body_error is None else body_error
        return render_template('newpost.html', base_title="Add a Blog Entry",body=body, 
                title=title, body_error=body_error, title_error=title_error)



@app.route("/blog")
def blog():
    if len(request.args)==0:    
        blogs = Blog.query.order_by(desc(Blog.id)).all()
        return render_template('blog.html', base_title="Build a Blog", blogs=blogs)
    else:
        blog_id=int(request.args.get('id'))
        blog=Blog.query.get(blog_id)

        return render_template('single-post.html', base_title=blog.title, blog=blog)



if __name__ == '__main__':
    app.run()