###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required # Here, too
from flask_sqlalchemy import SQLAlchemy
import requests
import json

## App setup code
app = Flask(__name__)
app.debug = True

## All app.config values
app.config['SECRET_KEY'] = 'hard to guess string from si364'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://avaweiner@localhost/avawMidterm"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

## Statements for db setup (and manager setup if using Manager)
db = SQLAlchemy(app)


######################################
######## HELPER FXNS (If any) ########
######################################
api_key = "nazpgms5bqejgj1fwolg1c6w"



##################
##### MODELS #####
##################

class Name(db.Model):
    __tablename__ = "names"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))

    def __repr__(self):
        return "{} (ID: {})".format(self.name, self.id)

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer,primary_key=True)
    listingID = db.Column(db.Integer)
    title = db.Column(db.String)
    price = db.Column(db.String)
    url = db.Column(db.String)
    favorites = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Product %r>' % self.title

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __repr__(self):
        return '<User %r>' % self.name


###################
###### FORMS ######
###################

class NameForm(FlaskForm):
    name = StringField("Please enter your name.",validators=[Required()])
    submit = SubmitField("Submit")

class EtsyForm(FlaskForm):
    keyword = StringField("What would you like to search Etsy for?", validators=[Required()])
    min_price = StringField("What is the minimum price you would pay? (no '$')", validators=[Required()])
    max_price = StringField("What is the maximum price you would pay? (no '$')", validators=[Required()])
    submit = SubmitField("Submit")

    def validate_min_price(self, field):
        if '$' in self.min_price.data:
            raise ValidationError("Your minimum price was not valid because it included $.")

    def validate_max_price(self, field):
        if '$' in self.max_price.data:
            raise ValidationError("Your maximum price was not valid because it included $.")



#######################
###### VIEW FXNS ######
#######################

@app.route('/')
def home():
    form = NameForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
    if form.validate_on_submit():
        name = form.name.data
        newname = Name(name)
        db.session.add(newname)
        db.session.commit()
        return redirect(url_for('all_names'))
    return render_template('base.html',form=form)

@app.route('/names')
def all_names():
    names = Name.query.all()
    return render_template('name_example.html',names=names)

@app.route('/etsy')
def etsy_search():
    form = EtsyForm()
    return render_template('etsyform.html', form=form)

@app.route('/etsy_results', methods = ["POST"])
def etsy_results():
    form = EtsyForm()
    if request.method == 'POST' and form.validate_on_submit():
        keyword = form.keyword.data
        min = form.min_price.data
        max = form.max_price.data
        base_url = "https://openapi.etsy.com/v2/listings/active?"
        params_d = {}
        params_d['keywords'] = keyword
        params_d['limit'] = 5
        params_d['min_price'] = float(min)
        params_d['max_price'] = float(max)
        params_d['api_key'] = api_key
        req = requests.get(base_url, params = params_d)
        r = json.loads(req.text)['results']
        results = []
        for p in r:
            product_exists = db.session.query(Product.id).filter_by(listingID=p['listing_id']).scalar()
            if product_exists:
                product = Product.query.filter_by(listingID=p['listing_id']).first()
                user = User.query.filter_by(id = product.user_id).first()
                url = product.url
                user_exists = db.session.query(User.id).filter_by(id=p['user_id']).scalar()
                if user_exists:
                    u = User.query.filter_by(id = p['user_id']).first()
                    user = u.name
                else:
                    url2 = "https://openapi.etsy.com/v2/users/{}".format(p['user_id'])
                    params_2 = {'api_key' : api_key}
                    req2 = requests.get(url2, params = params_2)
                    user = json.loads(req2.text)['results'][0]['login_name']
                    u = User(id = p['user_id'], name=user)
                    db.session.add(u)
                    db.session.commit()
            else:
                product = Product(title=p['title'], listingID=p['listing_id'], price=p['price'], url=p['url'], favorites=p['num_favorers'])
                db.session.add(product)
                db.session.commit()
                user_exists = db.session.query(User.id).filter_by(id=p['user_id']).scalar()
                if user_exists:
                    u = User.query.filter_by(id = p['user_id']).first()
                    user = u.name
                else:
                    url2 = "https://openapi.etsy.com/v2/users/{}".format(p['user_id'])
                    params_2 = {'api_key' : api_key}
                    req2 = requests.get(url2, params = params_2)
                    user = json.loads(req2.text)['results'][0]['login_name']
                    u = User(id = p['user_id'], name=user)
                    db.session.add(u)
                    db.session.commit()
                url = product.url
            results.append((product.title, user, url))
        return render_template('etsy_results.html', results=results)

    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("ERRORS IN FORM SUBMISSION: " + str(errors))

    return redirect(url_for('etsy_search'))

@app.route('/all_products')
def see_all_products():
    all_products = []
    for product in Product.query.all():
        name = product.title
        cost = product.price
        url = product.url
        all_products.append((name,cost,url))
    return render_template('all_products.html', all_products=all_products)

@app.route('/all_users')
def see_all_users():
    users = User.query.all()
    return render_template('all_users.html', users = users)

@app.route('/favorite')
def favorite_product():
    fav = Product.query.order_by(Product.favorites.desc()).first()
    # fav_user = (User.query.filter_by(id= Product.user_id).first()).name
    return render_template('favorite_product.html', p=fav, user="test name")

## Code to run the application...

# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
if __name__ == '__main__':
    db.create_all()
    app.run(use_reloader=True,debug=True)
