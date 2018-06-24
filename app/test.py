from flask_mail import Message
from app import mail
from app import app
msg = Message('test subject', sender=app.config['ADMINS'][0],
    recipients=['your-email@example.com'])
msg.body = 'text body'
msg.html = '<h1>HTML body</h1>'

mail.connect('smtp.gmail.com', '587')
mail.send(msg)