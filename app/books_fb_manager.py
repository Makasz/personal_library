from app.models import Books
from app.loginform import form
from app.loginform import RegistrationForm, BookForm, SearchBookForm, LendBookToForm
book = Books(isbn=form.isbn.data,
             title=form.title.data,
             author_name=form.author_name.data,
             author_surname=form.author_surname.data,
             owner=form.owner.data,
             status=form.status.data,
             current_owner=form.current_owner.data,
             img_url=form.img_url.data,
             description=form.description.data,
             )
db.session.add(book)
db.session.commit()