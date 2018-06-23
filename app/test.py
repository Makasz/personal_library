from app import db
from app.models import User
u = User(username='susan', email='susan@example.com')

u.set_password('mypassword')
print(u.check_password('mypassword'))
# db.session.add(u)
# db.session.commit()