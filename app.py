import cv2
import os
from flask import *
import shutil
from flask_mail import Mail, Message
# from flask_ngrok import run_with_ngrok


app = Flask(__name__)
# run_with_ngrok(app)


mail = Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'eisprojectkle@gmail.com'
app.config['MAIL_PASSWORD'] = 'Password@2022'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


def generate_dataset(name):
    face_classifier = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    def face_cropped(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)
        
        if faces == ():
            return None
        for (x,y,w,h) in faces:
            cropped_face = img[y:y+h,x:x+w]
        return cropped_face
    
    cap = cv2.VideoCapture(0)
    img_id = 0
    
    while True:
        ret, frame = cap.read()
        if face_cropped(frame) is not None:
            img_id+=1
            face = cv2.resize(face_cropped(frame), (200,200))
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            if os.path.isdir('data') == False:
                os.mkdir('data')
            # os.chdir('data') 
            if os.path.isdir('./data/'+name)==False:
                os.mkdir('./data/'+name)    
            file_name_path = "data/"+name+"/"+name+"."+str(img_id)+".jpg"
            # file_name_path = "Images for visualization/"+str(img_id)+'.jpg'
            cv2.imwrite(file_name_path, face)
            cv2.putText(face, str(img_id), (50,50), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2 )
            
            cv2.imshow("Cropped_Face", face)
            if cv2.waitKey(1)==13 or int(img_id)==100:
                break
                
    cap.release()
    cv2.destroyAllWindows()
    return "Collecting samples is completed !!!"

def zipfolder(name):
    shutil.make_archive(name, 'zip', 'data/'+name)
    # os.removedirs('data/chetan')
    shutil.rmtree('data/'+name, ignore_errors=True)
    sendmail(name)
    # shutil.rmtree(name+'.zip')
    os.remove(name+'.zip')

@app.route('/captured:<name>')
def home(name):
    res = generate_dataset(name)
    zipfolder(name)
    return res + ' ' + name + ' images'

@app.route('/home',methods=['GET','POST'])
def start():
    if request.method == "POST":
        name = request.form.get('name')
        return redirect(url_for('home',name=name))
    return render_template('home.html')

def sendmail(name):
     msg = Message(
                name,
                sender ='eisprojectkle@gmail.com',
                recipients = ['eisprojectkle@gmail.com']
               )
     msg.body = name+' zip file attached in this mail'
     with app.open_resource(name+".zip") as fp:  
        msg.attach(name+".zip", "application/zip", fp.read()) 
     mail.send(msg)

@app.route('/')
def consent():
    return render_template('consent.html')

if __name__ == '__main__':
    app.run()