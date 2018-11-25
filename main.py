from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import desc

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Admin@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key='y337kGcys&zP3B'

class Blog(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(120))
    body=db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title=title
        self.body=body
        self.owner_id=owner

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(120), unique=True)
    password=db.Column(db.String(120))
    #a foreign key relationship key
    blogs = db.relationship('Blog', backref='owner')


    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['index', 'login','signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect ('/login')

@app.route('/index')
def index():
    users=User.query.all()
    return render_template('index.html', users=users)


username_error=""
password_error=""
verify_error=""

@app.route('/login', methods=['POST', 'GET'])
def login():
    
    # First check for request type(get or post), 
    # On get request just render login form,
    # On post request, get data out of request and login user
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']

        # Get user from database first from database as requested. 
        # It will get all things in a row associated with that item.
        user=User.query.filter_by(username=username).first()
        # check if user exist
        if user and user.password==password:
            session['username'] = user.username
            return redirect('/newpost')
            # For wrong password entered
        elif username=="" or user is None:
            flash ("Username does not exist")
            return render_template('login.html')

        elif user.password != password or password=="":
            flash ("Username and password does not match")
            return render_template('login.html')
    
  
    
    return render_template('login.html')    


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        verify=request.form['verify']

        if username=="" or password=="" or verify=="":
            flash ("Don't leave any field blank")
            return render_template('signup.html', error="Don't leave any field blank"  )
        if password != verify:
            flash("password verification wrong")
            return render_template('signup.html', verify_error="password verification wrong"  )
        if len(username)<3 or len(password)<3:
            flash("invalid username or password less than 3 characters"  )
            return render_template('signup.html')

    
        existing_username=User.query.filter_by(username=username).first()

        if not existing_username:
            new_user=User(username, password)
            db.session.add(new_user)
            db.session.commit()
            # Remember the user is logged in until logged out
            session['username'] = new_user.username
            return redirect('/newpost')
        else:
            flash ("Username already exists")
            return render_template('signup.html', error="Username already exists"  )

    return render_template('signup.html')



@app.route('/logout')
def logout():
    # Delete session
    del session['username']
    return redirect ('login.html')


@app.route("/newpost", methods=['POST', 'GET'])
def newpost():
    
    if request.method == 'POST':
        title=request.form.get('title')
        body=request.form.get('body')
        # handle errors
        if title=="":
            title_error = "Please write title for the post."
            return redirect('/newpost?body='+body + '&title_error='+title_error)
        if body=="":
            body_error = "It should not be left empty."
            return redirect('/newpost?title=' +title + '&body_error='+body_error)
        # Gets the email of current logged in user. Filtered by email and get first one.
        owner = User.query.filter_by(username=session['username']).first()
        
        db.session.add(Blog(title=title, body=body, owner=owner.id))
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
    owner_id=""
    
    if len(request.args)==0:    
        blogs = Blog.query.order_by(desc(Blog.id)).all()
        users=User.query.all()
                
        #singleblog= Blog.query.filter_by(id=owner_id).first()

            
        return render_template('blog.html', base_title="Build a Blog", blogs=blogs, users=users)

    else:
        blog_id=int(request.args.get('id'))
        blog=Blog.query.get(blog_id)
        owner_id=Blog.query.get(owner_id)
        
        user=User.query.filter_by(id=blog.owner_id).first()
        username=user.username
        return render_template('single-post.html', base_title=blog.title, blog=blog, 
            owner_id=blog.owner_id, username=username)

@app.route('/singleUser')
def singleUser():
    user_id=request.args.get('uid')
    #user=User.query.filter_by(id=user_id).first()
    user = User.query.filter_by(id=user_id).first()
    username=user.username
    blogs=user.blogs
    return render_template('singleUser.html', blogs=blogs, username=username)

    



if __name__ == '__main__':
    app.run()