from flask import Flask
from flask.templating import render_template
from flask import Flask, render_template, jsonify, request,redirect,flash, Markup,url_for, session, flash
from datetime import date, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import DataError, IntegrityError, AmbiguousForeignKeysError
from sqlalchemy.orm.exc import UnmappedInstanceError
from flask import *  
from sqlalchemy import text

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:Admin@123@localhost/final'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = b'hkahs3720/'

db = SQLAlchemy(app)

class users(db.Model):
    userid=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String,nullable=False)  
    password=db.Column(db.String,nullable=False)  


class book(db.Model):
	isbn = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(200), nullable = False)
	desc = db.Column(db.String(200), nullable = False)
	genre = db.Column(db.String(200), nullable = False)
	author = db.Column(db.String(200), nullable = False) 

class borrow(db.Model):
	borrowid = db.Column(db.Integer, primary_key = True)
	bisbn = db.Column(db.Integer, db.ForeignKey('book.isbn'))
	bname = db.Column(db.String(200), nullable = False)
	mid = db.Column(db.Integer, db.ForeignKey('users.userid'))
	mname = db.Column(db.String(200), nullable = False)



@app.route('/')
def index():
    session['username']=None
    session['userid']= None
    session['password']= None
    return render_template("index.html")


@app.route("/userLogin", methods=["POST"])
def userLogin():
    session['username']=None
    session['userid']= None
    session['password']= None
    return render_template("userLogin.html")

    
@app.route("/userDashboard.html", methods=["POST"])
def userDashboard():
    if session['username']!=None:
       return render_template("userDashboard.html")
    unam = request.form.get("username")
    pwd = request.form.get("password")
    
    ulist = users.query.filter_by(username=unam).first()
    
    if ulist!=None and ulist.password==pwd:
        session['username']= ulist.username
        session['userid']= ulist.userid
        session['password']= ulist.password
        return render_template("userDashboard.html")
    else:  
        return render_template("index.html")


@app.route("/viewCatalog", methods=["POST"])
def viewCatalog():
    library = book.query.all()
    return render_template("viewLibrary.html",book=library)



@app.route("/userDashboard/viewLibrary", methods=["POST"])
def viewLibrary():
    library = book.query.all()
    return render_template("viewLibrary.html",book=library)

@app.route("/userDashboard/borrowedbook", methods=["POST"])
def borrowedbook():
    book = borrow.query.filter_by(mid=session['userid'])
    return render_template("borrowedBooks.html",data=book)

@app.route("/userDashboard/userDetails", methods=["POST"])
def userDetails():
    return render_template("userDetails.html")

@app.route("/index.html", methods=["POST"])
def logOut():
    session['username']=None
    session['userid']= None
    session['password']= None
    return render_template("index.html")

@app.route("/admin/addBook/addBookInto", methods=["POST"])
def addBookInto():
    isbn=request.form.get("isbn")
    title=request.form.get("title")
    author=request.form.get("author")
    year=request.form.get("year")
    genre=request.form.get("genre")
    db.execute("INSERT INTO booklist (isbn, title,author, publishyear,genre) VALUES (:isbn, :title,:author,:publishyear,:genre)",
            {"isbn": isbn, "title": title, "author":author,"publishyear":year,"genre":genre}) 
    db.commit() 
    # return render_template("addBookInto.html")
    return render_template("admin.html")


@app.route("/admin/addBook", methods=["POST"])
def addBook():
    return render_template("addBook.html")

@app.route("/admin/addUser", methods=["POST"])
def addUser():
    return render_template("addUser.html")

@app.route("/admin/addUser/success", methods=["POST"])
def addUserInto():
    userID=request.form.get("userid")
    userName=request.form.get("username")
    password=request.form.get("password")
    db.execute("INSERT INTO users  VALUES (:userID, :userName,:password)",
            {"userID": userID, "userName": userName, "password":password}) 
    db.commit() 
    return render_template("addUserInto.html")
    # return render_template("success.html")

@app.route("/admin/deletemember", methods=["POST"])
def deletemember():
    return render_template("deletemember.html")
    
@app.route("/admin/deletemember/deletememberInto", methods=["POST"])
def deletememberInto():
    userID=request.form.get("userid")
    users.query.filter(text(userID)).delete()
    db.commit()
    return render_template("admin.html")


@app.route("/admin/removebook", methods=["POST"])
def removebook():
    return render_template("removebook.html")

@app.route("/admin/removebook/removebookInto", methods=["POST"])
def removebookInto():
    isbn=request.form.get("isbn")
    book.query.filter(isbn).delete()
    db.commit()
    return render_template("admin.html")


@app.route("/admin/issueBook", methods=["POST"])
def issueBook():
    return render_template("issueBook.html")

@app.route("/admin/issueBook/issueBookInto", methods=["POST"])
def issueBookInto():
    title=request.form.get("title")
    username=request.form.get("userName")
    db.execute("INSERT INTO borrow  VALUES (:title, :userName,)",
            {"title": title, "userName": username}) 
    db.commit() 
    return render_template("admin.html")

@app.route("/admin/returnBook", methods=["POST"])
def returnBook():
    return render_template("returnBook.html")


@app.route("/admin/returnBook/returnBookInto", methods=["POST"])
def returnBookInto():
    username=request.form.get("username")
    title=request.form.get("title")
    borrow.query.filter(title,username).delete()
    db.commit()
    return render_template("admin.html")


@app.route("/admin.html", methods = ['GET', 'POST'])
def admin_login():
    return render_template("admin.html")

@app.route("/addbook.html", methods = ['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        try:
            isbn = request.form['isbn']
            name = request.form['name']
            desc = request.form['desc']
            genre = request.form['genre']
            author = request.form['author']
            todo = book(isbn = isbn, name = name, desc = desc, genre = genre, author = author)
            db.session.add(todo)
            db.session.commit()
            flash("Book Added Sucessfully")
            return render_template("admin.html")
        except DataError:
            flash("Invalid Credentials")
            return render_template('admin.html')
        except IntegrityError:
            flash("Invalid Credentials")
            return render_template('admin.html')
        except AmbiguousForeignKeysError:
            flash("Invalid Credentials")
            return render_template('admin.html')
        except UnmappedInstanceError:
            flash("Invalid Credentials")
            return render_template('admin.html')
    return render_template("addbook.html")

@app.route("/removebook.html", methods = ['GET', 'POST'])
def remove_book():
    if request.method == 'POST':
        try:
            isbn = request.form['isbn']
            todo = book.query.filter_by(isbn=isbn).first()
            db.session.delete(todo)
            db.session.commit()
            flash("Book Removed Sucessfully")
            return render_template("admin.html")
        except DataError:
            flash("Invalid Credentials")
            return render_template('admin.html')
        except IntegrityError:
            flash("Invalid Credentials")
            return render_template('admin.html')
        except AmbiguousForeignKeysError:
            flash("Invalid Credentials")
            return render_template('admin.html')
        except UnmappedInstanceError:
            flash("Invalid Credentials")
            return render_template('admin.html')
    return render_template("removebook.html")




@app.route("/issuebook.html", methods = ['GET', 'POST'])
def issue_book():
    if request.method == 'POST':
        try:
            borrowid = request.form['borrowid']
            bisbn = request.form['bisbn']
            bname = request.form['bname']
            mid = request.form['mid']
            mname = request.form['mname']
            todo = borrow(borrowid = borrowid, bisbn = bisbn, bname = bname, mid = mid, mname = mname)
            db.session.add(todo)
            db.session.commit()
            flash("Book Issued Sucessfully")
            return render_template("admin.html")
        except DataError:
            flash("Invalid Credentials")
            return render_template('admin.html')
        except IntegrityError:
            flash("Invalid Credentials")
            return render_template('admin.html')
        except AmbiguousForeignKeysError:
            flash("Invalid Credentials")
            return render_template('admin.html')
        except UnmappedInstanceError:
            flash("Invalid Credentials")
            return render_template('admin.html')
    return render_template("issuebook.html")

@app.route("/returnbook.html", methods = ['GET', 'POST'])
def return_book():
    if request.method == 'POST':
        try:
            borrowid = request.form['borrowid']
            todo = borrow.query.filter_by(borrowid=borrowid).first()
            db.session.delete(todo)
            db.session.commit()
            flash("Book Returned Sucessfully")
            return render_template("admin.html")
        except DataError:
            flash("Invalid Credentials")
            return render_template('admin.html')
        except IntegrityError:
            flash("Invalid Credentials")
            return render_template('admin.html')
        except AmbiguousForeignKeysError:
            flash("Invalid Credentials")
            return render_template('admin.html')
        except UnmappedInstanceError:
            flash("Invalid Credentials")
            return render_template('admin.html')
    return render_template("returnbook.html")


@app.route("/addmember.html", methods = ['GET', 'POST'])
@app.route("/index.html", methods = ['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        
        try:
            userid = request.form['userid']
            username = request.form['username']
            password = request.form['password']
            todo = users(userid = userid, username = username, password = password)
            db.session.add(todo)
            db.session.commit() 
            flash("Member Added Sucessfully")
            return render_template("admin.html")
        except DataError:
            flash("Invalid Credentials")
            return render_template('admin.html')
        except IntegrityError:
            flash("Invalid Credentials")
            return render_template('admin.html')
        except AmbiguousForeignKeysError:
            flash("Invalid Credentials")
            return render_template('admin.html')
        except UnmappedInstanceError:
            flash("Invalid Credentials")
            return render_template('admin.html')
 
    return render_template("addmember.html")

@app.route("/deletemember.html", methods = ['GET', 'POST'])
def delete_member():
    if request.method == 'POST':
        try:
            userid = request.form['userid']
            todo = users.query.filter_by(userid=userid).first()
            db.session.delete(todo)
            db.session.commit()
            flash("Member Removed Sucessfully")
            return render_template("admin.html")
        except DataError:
            flash("Invalid Credentials")
            return render_template('admin.html')
        except UnmappedInstanceError:
            flash("Invalid Credentials")
            return render_template('admin.html')
        except IntegrityError:
            flash("Invalid Credentials")
            return render_template('admin.html')
        except AmbiguousForeignKeysError:
            flash("Invalid Credentials")
            return render_template('admin.html')
    return render_template("deletemember.html")

if(__name__ == "__main__"):
    app.run(debug=True)
