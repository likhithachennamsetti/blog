from flask import Flask,render_template,url_for,request,redirect,url_for,flash,session
import mysql.connector
from cmail import sendmail
from otp import genotp
app=Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

mydb=mysql.connector.connect(host='localhost',user='root',password='system',db='likhi')
with mysql.connector.connect(host='localhost',user='root',password='system',db='likhi'):   
    cursor=mydb.cursor(buffered=True)
    cursor.execute("create table if not exists forms(userame varchar(50) primary key,mobile varchar(50) unique,email varchar(200),address varchar(150),password varchar(50))")
mycursor=mydb.cursor()
@app.route('/form',methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form.get('username')
        mobile=request.form.get('mobile')
        email=request.form.get('email')
        address=request.form.get('address')
        password=request.form.get('password')
        otp=genotp()
        sendmail(to=email,subject="Thanks for registration",body=f'otp is :{otp}')
        return render_template('verification.html',username=username,mobile=mobile,email=email,address=address,password=password,otp=otp)
    return render_template('registration.html')
@app.route('/otp/<username>/<mobile>/<email>/<address>/<password>/<otp>',methods=['GET','POST'])
def otp(username,mobile,email,address,password,otp):
    if request.method=='POST':
        uotp=request.form['uotp']
        if otp==uotp:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('insert into forms values(%s,%s,%s,%s,%s)',[username,mobile,email,address,password])
            mydb.commit()
            cursor.close()
            return redirect(url_for('login'))
    return render_template('verification.html',username=username,mobile=mobile,email=email,address=address,password=password,otp=otp)
@app.route('/login',methods=['GET','POST'])
def login(): 
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(*) from forms where username=%s && password=%s',[username,password])
        data=cursor.fetchone()[0]
        print(data)
        if data==1:
            session['username']=username
            if not session.get(session['username']):
                session[session['username']]={}
            return redirect(url_for('homepage'))
        else:
            return 'Invalid Username and password'
    return render_template('login.html')
@app.route('/logout')
def logout():
    if session.get('username'):
        session.pop('username')
    return redirect(url_for('login'))
@app.route('/')
def homepage():
    return render_template('homepage.html')
@app.route('/addpost' ,methods=['GET','POST'])
def add_post():
    if request.method=='POST':
        title=request.form['title']
        content=request.form['content']
        slug=request.form['slug']
        print(title)
        print(content)
        print(slug)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('insert into post(title, content, slug) values(%s,%s,%s)',[title,content,slug])
        mydb.commit()
        cursor.close()
    return render_template('add_post.html')
#create admin page
@app.route('/admin')
def admin():
    return render_template('homepage.html')
#view post
@app.route('/view_post')
def view_post():
    cursor=mydb.cursor(buffered=True)
    cursor.execute("select *from post")
    post=cursor.fetchall()
    print(post)
    cursor.close()
    return render_template('view_post.html',post=post)
@app.route('/delete_post/<int:id>',methods=['POST'])
def delete_post(id):
    print(id)
    cursor=mydb.cursor(buffered=True)
    cursor.execute('select *from post where id=%s',(id,))
    post=cursor.fetchone()
    cursor.execute("delete from post where id=%s",(id,))
    print(post)
    mydb.commit()
    cursor.close()
    return redirect(url_for('view_post'))
@app.route('/update_post/<int:id>',methods=['GET','POST'])
def update_post(id):
    print(id)
    if request.method=='POST':
        title=request.form["title"]
        content=request.form['content']
        slug=request.form['slug']
        print(title)
        print(content)
        print(slug)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('UPDATE post set title=%s,content=%s,slug=%s where id=%s' ,(title,content,slug,id))
        mydb.commit()
        cursor.close()
        return redirect(url_for('view_post'))
    else:
        cursor = mydb.cursor(buffered=True)
        cursor.execute('select * from post where id=%s',(id,))
        post=cursor.fetchone()
        cursor.close()
        return render_template('update_post.html',post=post)
app.run(debug=True,use_reloader=True)

