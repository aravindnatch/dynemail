from flask import Flask, render_template, redirect, request, session, make_response, send_file
from email.mime.text import MIMEText
import json
import smtplib
from PIL import Image, ImageDraw, ImageFont
import string
from random import *
import os
import sqlite3

app = Flask(__name__)

app.secret_key = b'dGFwZC53dGY='


@app.errorhandler(404) 
def notfound(e):
    return render_template("404.html") 

@app.route("/")
def index():
    dpl = request.args.get('dpl')
    err = request.args.get('err')
    p = []
    if dpl == '1':
        p.append(1)
        p.append(err)
    else:
        p.append(0)
    return render_template("index.html", p=p)

@app.route("/msgcb")
def msgcb():
    argData = {key:val for key, val in request.args.to_dict().items() if val != ""}
    fromemail = argData['fromemail']
    password = argData['password']
    toemail = argData['toemail']
    subject = argData['subject']
    premessage = argData['body']

    # generate unique message id
    while True:
        characters = string.ascii_letters + string.digits
        msgID =  "".join(choice(characters) for x in range(64))

        conn = sqlite3.connect('dyn.db')
        c = conn.cursor()
        c.execute("SELECT * FROM email WHERE msgID = ?", (msgID,))
        exist = c.fetchone()
        c.close()

        if exist == None:
            break

    # make text friendly
    char = 0
    split = ""
    for x in premessage.split():
        lenx = len(x)
        if char + lenx < 58:
            char+=lenx+1
            split += x + " "
        else:
            split += "\n" + x + " "
            char = lenx
    split = split.strip()

    # generate image from text
    img = Image.new('RGBA', (400, len(split.split('\n'))*20), (255,255,255,0))
    
    fnt = ImageFont.truetype('roboto.ttf', 15)
    d = ImageDraw.Draw(img)
    d.text((0,0), split, font=fnt, fill=(0, 0, 0))
    
    img.save(f'messages/{msgID}.png', 'PNG')

    # send email
    message = f"<html><img src='https://dynemail.aru.wtf/messages/{msgID}.png'/></html>"
    dynemail = MIMEText(message, "html")
    dynemail["From"] = fromemail
    dynemail["To"] = toemail
    dynemail["Subject"] = subject

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls() 
    try:
        server.login(fromemail, password)
    except:
        return redirect(f"/?dpl=1&err=Username+and+Password+not+accepted.+Learn+more+at+https://support.google.com/mail/?p=BadCredentials")

    server.sendmail(fromemail, toemail, dynemail.as_string())
    server.quit()

    # database entries
    conn = sqlite3.connect('dyn.db')
    c = conn.cursor()
    c.execute("INSERT INTO email (fromemail,toemail,subject,message,msgID,viewed) VALUES (?,?,?,?,?,?)", (fromemail,toemail,subject,premessage,msgID,0))
    conn.commit()
    c.close()

    return redirect(f"/edit/{msgID}")

@app.route("/edit/<msgID>")
def edit(msgID):
    conn = sqlite3.connect('dyn.db')
    c = conn.cursor()
    msgInfo = []
    for row in c.execute("SELECT * FROM email WHERE msgID = ?", (msgID,)):
        msgInfo = row

    c.close()

    try:
        msgInfo[5] = int(msgInfo[5])
    except:
        pass

    return render_template("edit.html", msgInfo=msgInfo)

@app.route("/editmsgcb")
def editmsgcb():
    premessage = request.args.get('body')
    msgID = request.args.get('msgID')

    # make text friendly
    char = 0
    split = ""
    for x in premessage.split():
        lenx = len(x)
        if char + lenx < 58:
            char+=lenx+1
            split += x + " "
        else:
            split += "\n" + x + " "
            char = lenx
    split = split.strip()

    # generate image from text
    img = Image.new('RGBA', (400, len(split.split('\n'))*20), (255,255,255,0))
    
    fnt = ImageFont.truetype('roboto.ttf', 15)
    d = ImageDraw.Draw(img)
    d.text((0,0), split, font=fnt, fill=(0, 0, 0))
    
    img.save(f'messages/{msgID}.png', 'PNG')

    conn = sqlite3.connect('dyn.db')
    c = conn.cursor()
    c.execute("UPDATE email SET message = ? WHERE msgID = ?", (premessage,msgID))
    conn.commit()
    c.close()

    return redirect(f"/edit/{msgID}")
 
@app.route("/messages/<msgID>")
def img(msgID):
    msgID = msgID[:-4]
    conn = sqlite3.connect('dyn.db')
    c = conn.cursor()
    msgInfo = []
    for row in c.execute("SELECT * FROM email WHERE msgID = ?", (msgID,)):
        msgInfo = row
    c.close()

    if msgInfo[5] != "1":
        conn = sqlite3.connect('dyn.db')
        c = conn.cursor()
        c.execute("UPDATE email SET viewed = ? WHERE msgID = ?", ("1",msgID))
        conn.commit()
        c.close()

    return send_file(f'messages/{msgID}.png', mimetype='image/png')