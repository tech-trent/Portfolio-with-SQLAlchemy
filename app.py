
import forms
import models
import datetime

from peewee import IntegrityError

from flask import (
    flash,
    Flask,
    redirect,
    render_template,
    request,
    url_for
)

app = Flask(__name__)
app.secret_key = "oiu34whta0puiwfvnaesiprb4ug43wguio4w3egjk"


errmsg = """One or more entries was invalid, probably the date you entered or
 your number of hours. Please correct it and try again."""


@app.before_request
def beforeRequest():

    # Runs before each request.

    models.db.connect()


@app.after_request
def afterRequest(response):

    # Runs after each request, returns response object.

    models.db.close()
    return response


@app.route('/')
def index():

    # One of the 2 routes to the home page.

    # Since strftime is used twice within the HTML,
    # I decided to send the entire
    # function to the template for reusability.

    return render_template('index.html',
                           db=models.Entry.select()
                           .order_by(models.Entry.date),
                           strftime=datetime.datetime.strftime)


@app.route('/entries')
def entries():

    # Identical to the / route

    return render_template('index.html',
                           db=models.Entry.select()
                           .order_by(models.Entry.date),
                           strftime=datetime.datetime.strftime)


@app.route('/entries/new', methods=['POST', 'GET'])
def new():
    form = forms.EntryForm()
    if form.validate_on_submit():
        try:
            models.Entry.create(
                title=form.title.data,
                date=form.date.data,
                time=form.time.data,
                learned=form.learned.data,
                resources=form.resources.data
            )
            flash("Entry saved!")
            return redirect(url_for('index'))
        except IntegrityError:
            flash(errmsg)
    elif request.method == "POST":
        flash(errmsg)
    return render_template('new.html', form=form)


@app.route('/entries/<int:ID>')
def detail(ID):

    # Renders the detail template in a very similar way to the homepage.
    # Passes in the strftime function for the same reasons.
    # Only passes in a single entry from the database,
    # as defined by the ID number in the URL.

    return render_template('detail.html',
                           entry=models.Entry.get_by_id(ID),
                           strftime=datetime.datetime.strftime)


@app.route('/entries/<int:ID>/edit', methods=['POST', 'GET'])
def edit(ID):

    # Allows the user to edit an entry using most of the same syntax as the "new" route,
    # except the create query is replaced by an update query,
    # as is the attached flash message.

    entry = models.Entry.get_by_id(ID)
    form = forms.EntryForm()
    if request.method == "GET":
        form.date.data = entry.date
        form.learned.data = entry.learned
        form.resources.data = entry.resources
    if form.validate_on_submit():
        try:
            models.Entry.update(
                title=form.title.data,
                date=form.date.data,
                time=form.time.data,
                learned=form.learned.data,
                resources=form.resources.data
            ).where(models.Entry.ID == entry.ID).execute()
            flash("Entry updated!")
            return redirect(url_for('index'))
        except IntegrityError:
            flash(errmsg)
    elif request.method == "POST":
        flash(errmsg)
    return render_template('edit.html',
                           entry=entry,
                           form=form)


@app.route('/entries/<int:ID>/delete')
def delete(ID):

    # Deletes the record with an ID equal to the one passed to the URL,
    # sends a flash message and redirects the user to the homepage.

    models.Entry.get_by_id(ID).delete_instance()
    flash("Entry deleted!")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=8000)
