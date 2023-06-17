import webbrowser
from flask import Flask, Response, redirect, render_template, request, url_for
from face_rec import generate_frame, mark_attendance, face_detected
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import os

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/face_recognition_project'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False    
db = SQLAlchemy(app)

# Mail Configuration
app.config['MAIL_SERVER'] ='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'your_gmail'
app.config['MAIL_PASSWORD'] = 'your_gmail_app_password'   # can be generated through your gmail account
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail=Mail(app);

# File Configuration
app.config['UPLOAD_FOLDER'] = 'D:\\Attendance-system-based-on-Face-Recognition-master\\static\\images\\Student images'

detected_face = ''

class Student(db.Model):
    univ_id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(30),nullable=False)
    email = db.Column(db.String(30),nullable=False)
    father = db.Column(db.String(30),nullable=False)
    attendance = db.Column(db.Integer,default=0)
    dob = db.Column(db.DateTime,nullable=True)
    gen = db.Column(db.String(2), nullable=False)
    ph_no = db.Column(db.String(10),nullable=False)
    course = db.Column(db.String(20), nullable=False)
    sem = db.Column(db.Integer,nullable=False)
    sec = db.Column(db.String(2),nullable=False)
    croll_no = db.Column(db.Integer,nullable=False)
    address = db.Column(db.String(40),nullable=False)
    city = db.Column(db.String(20),nullable=False)
    state = db.Column(db.String(20),nullable=False)
    zipcode = db.Column(db.Integer,nullable=False)
    university = db.Column(db.String(30),nullable=False)

class Admin(db.Model):
    admin_id=db.Column(db.String(30),primary_key=True)
    name=db.Column(db.String(30),nullable=False)


@app.route("/", methods=["GET", "POST"])
def home():
    if(request.method=="POST"):
        searchtext=request.form.get('query')
        if(searchtext=='mark attendance'):
            return render_template('face_detect.html')
        elif(searchtext=='contact us'):
            return render_template('contact.html')
        elif(searchtext=='login'):
            return render_template('login.html')
        else:
            webbrowser.open_new_tab("https://www.google.com/search?q="+searchtext)
            return render_template('index.html')
    else:
        return render_template('index.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route('/face_detect')
def face_detect():
    return render_template('face_detect.html')

@app.route('/video/<string:user>')
def video(user):
    return Response(generate_frame(user),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detect/<string:user>')
def detect(user):
    global detected_face
    if user == 'student':
        print("Face Detected : ",face_detected())
        stu_details = None
        detected_face = face_detected()
        if detected_face != '':
            print("no im here")
            stu_details = Student.query.filter_by(univ_id=detected_face).first()
            print(stu_details)
            return render_template('profile.html',stu_details = stu_details)
        else:
            print("Im here")
            return render_template('face_detect.html', noface = True)
            # return render_template('profile.html',stu_details = stu_details)
    elif user == 'admin':
        print("Face Detected : ",face_detected())
        admin = None
        detected_face = face_detected()
        if detected_face != '':
            print("no im here")
            admin = Admin.query.filter_by(admin_id=detected_face).first()
            print(admin)
            return render_template('userhome.html',admin=admin)
        else:
            print("Im here")
            return render_template('login.html', noface = True)
            # return render_template('profile.html',stu_details = stu_details)
    else:
        return redirect(url_for('home'))


@app.route('/mark')
def mark():
    print(detected_face)
    res = mark_attendance(detected_face)
    # curr_student = ''
    curr_student = Student.query.filter_by(univ_id=detected_face).first()
    if res == 1:
        curr_student.attendance = curr_student.attendance + 1
        db.session.commit()
        # return "attendance marked"
        return render_template('profile.html', stu_details = curr_student, status = res)
    else:
        # return "attendance already marked"
        return render_template('profile.html', stu_details = curr_student, status = res)

@app.route("/add",methods=["GET","POST"])
def add():
    if(request.method=="POST"):
        luniv_id = request.form.get('UniversityId')
        lname=request.form.get('Name')
        lemail = request.form.get('Email')
        ldob=request.form.get('DOB')
        lgen = request.form.get('Gender')
        lfather=request.form.get('Guardian')
        laddress=request.form.get('Address')
        lmobile=request.form.get('Contact')
        lcity=request.form.get('City')
        lstate=request.form.get('State')
        lzip=request.form.get('Zip')
        luniversity=request.form.get('University')
        lcourse=request.form.get('Course')
        lsem=request.form.get("Semester")
        lsection=request.form.get('Section')
        lcroll_no=request.form.get('ClassRno')
        entry=Student(univ_id=luniv_id, name=lname, email=lemail, father=lfather, dob=ldob, gen=lgen, ph_no=lmobile, course=lcourse, sem=lsem, sec=lsection, croll_no=lcroll_no, university=luniversity, address=laddress, city=lcity, state=lstate, zipcode=lzip)
        db.session.add(entry)
        db.session.commit()
        lstpic=request.files['StudentPic']
        lstpic.save(os.path.join(app.config['UPLOAD_FOLDER'],luniv_id+'.jpg'))
        return render_template('add.html', status_add=True)
    else:
        return render_template('add.html')


@app.route("/update",methods=["GET","POST"])
def update():
    if(request.method=="POST"):
        luniv_id = request.form.get('UniversityId')
        lname=request.form.get('Name')
        lemail = request.form.get('Email')
        ldob=request.form.get('DOB')
        lgen = request.form.get('Gender')
        lfather=request.form.get('Guardian')
        laddress=request.form.get('Address')
        lmobile=request.form.get('Contact')
        lcity=request.form.get('City')
        lstate=request.form.get('State')
        lzip=request.form.get('Zip')
        luniversity=request.form.get('University')
        lcourse=request.form.get('Course')
        lsem=request.form.get("Semester")
        lsection=request.form.get('Section')
        lcroll_no=request.form.get('ClassRno')
        student=Student.query.filter_by(univ_id=luniv_id).first()

        if(not student ):
            return render_template('update.html', status_update=False)
        else:
            if(lname!=""):
                student.name=lname
            if(ldob!=""):
                student.dob=ldob
            if(laddress!=""):
                student.address=laddress
            if(lfather!=""):
                student.father=lfather
            if(lmobile!=""):
                student.ph_no=lmobile
            if(lcity!=""):
                student.city=lcity
            if(lzip!=""):
                student.zipcode=lzip
            if(lstate!=""):
                student.state=lstate
            if(luniversity!=""):
                student.university=luniversity
            if(lsection!=""):
                student.sec=lsection
            if(lcroll_no!=""):
                student.croll_no=lcroll_no
            if(lsem!=""):
                student.sem=lsem
            if(lcourse!=""):
                student.course=lcourse
            if(lemail!=""):
                student.email=lemail
            if(lgen != None):
                student.gen=lgen
            db.session.commit()
            return render_template('update.html', status_update=True)
    else:
        return render_template('update.html')


@app.route("/contact",methods=["GET","POST"])
def contact():
    if(request.method=="POST"):
        message=request.form.get('message')
        name=request.form.get('name')
        email=request.form.get('email')
        subject=request.form.get('subject')
        msg = Message(
                subject,
                sender ='sender@gmail.com',
                recipients = ['recipient@gmail.com']
               )
        msg.body='From : ('+email+" ) "+name+"\n\n"+"Message :"+message
        mail.send(msg)
        return render_template("contact.html")
    else:
        return render_template("contact.html")


if __name__ == '__main__':
    app.run(debug=True)
