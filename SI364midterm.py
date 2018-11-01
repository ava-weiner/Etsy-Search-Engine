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

class Shop(db.Model):
    __tablename__ = "shops"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    products = db.Column(db.Integer)
    url = db.Column(db.String)

    def __repr__(self):
        return '<Shop %r>' % self.name

###################
###### FORMS ######
###################
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

class ShopForm(FlaskForm):
    keyword = StringField("What type of shop are you looking for?", validators=[Required()])
    submit = SubmitField("Submit")

#######################
###### VIEW FXNS ######
#######################
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

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
            user_exists = db.session.query(User.id).filter_by(id=p['user_id']).scalar()
            if user_exists:
                u = User.query.filter_by(id = p['user_id']).first()
                product_exists = db.session.query(Product.id).filter_by(listingID=p['listing_id']).scalar()
                if product_exists:
                    product = Product.query.filter_by(listingID=p['listing_id']).first()
                else:
                    product = Product(title=p['title'], listingID=p['listing_id'], price=p['price'], url=p['url'], favorites=p['num_favorers'], user_id = u.id)
                    db.session.add(product)
                    db.session.commit()
            else:
                url2 = "https://openapi.etsy.com/v2/users/{}".format(p['user_id'])
                params_2 = {'api_key' : api_key}
                req2 = requests.get(url2, params = params_2)
                user = json.loads(req2.text)['results'][0]['login_name']
                u = User(id = p['user_id'], name=user)
                db.session.add(u)
                db.session.commit()
                product = Product(title=p['title'], listingID=p['listing_id'], price=p['price'], url=p['url'], favorites=p['num_favorers'], user_id = u.id)
                db.session.add(product)
                db.session.commit()
            results.append((product.title, u.name, product.url))
        return render_template('etsy_results.html', results=results)

    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("ERRORS IN FORM SUBMISSION: " + str(errors))

    return redirect(url_for('etsy_search'))

@app.route('/etsy/<search>')
def etsy_search2(search):
    base_url = "https://openapi.etsy.com/v2/listings/active?"
    params_d = {}
    params_d['keywords'] = search
    params_d['limit'] = 5
    params_d['api_key'] = api_key
    req = requests.get(base_url, params = params_d)
    r = json.loads(req.text)['results']
    results = []
    for p in r:
        user_exists = db.session.query(User.id).filter_by(id=p['user_id']).scalar()
        if user_exists:
            u = User.query.filter_by(id = p['user_id']).first()
            product_exists = db.session.query(Product.id).filter_by(listingID=p['listing_id']).scalar()
            if product_exists:
                product = Product.query.filter_by(listingID=p['listing_id']).first()
            else:
                product = Product(title=p['title'], listingID=p['listing_id'], price=p['price'], url=p['url'], favorites=p['num_favorers'], user_id = u.id)
                db.session.add(product)
                db.session.commit()
        else:
            url2 = "https://openapi.etsy.com/v2/users/{}".format(p['user_id'])
            params_2 = {'api_key' : api_key}
            req2 = requests.get(url2, params = params_2)
            user = json.loads(req2.text)['results'][0]['login_name']
            u = User(id = p['user_id'], name=user)
            db.session.add(u)
            db.session.commit()
            product = Product(title=p['title'], listingID=p['listing_id'], price=p['price'], url=p['url'], favorites=p['num_favorers'], user_id = u.id)
            db.session.add(product)
            db.session.commit()
        results.append((product.title, u.name, product.url))
    return render_template('etsy_results.html', results=results)

@app.route('/search/shops', methods = ["GET"])
def shop_results():
    form = ShopForm(request.args)
    results = None
    if request.method == 'GET' and form.validate():
        keyword = form.keyword.data
        base_url = "https://openapi.etsy.com/v2/shops?"
        params_d = {}
        params_d['api_key'] = api_key
        params_d['keywords'] = keyword
        params_d['limit'] = 5
        req = requests.get(base_url, params = params_d)
        r = json.loads(req.text)['results']
        results = []
        for s in r:
            shop_exists = db.session.query(Shop.id).filter_by(id=s['shop_id']).scalar()
            if shop_exists:
                shop = Shop.query.filter_by(id = s['shop_id']).first()
            else:
                shop = Shop(id=s['shop_id'], name=s['shop_name'], products=s['listing_active_count'], url=s['url'])
                db.session.add(shop)
                db.session.commit()
            results.append((shop.name, shop.products, shop.url))
    print (results)
    return render_template('shopform.html', form=form, results=results)

@app.route('/all_shops')
def see_all_shops():
    shops = []
    for shop in Shop.query.all():
        shops.append((shop.name, shop.products, shop.url))
    return render_template('all_shops.html', shops = shops)

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
    users = []
    for user in User.query.all():
        use = user.name
        num = len(Product.query.filter_by(user_id = user.id).all())
        users.append((use, num))
    return render_template('all_users.html', users = users)

@app.route('/favorite')
def favorite_product():
    fav = Product.query.order_by(Product.favorites.desc()).first()
    return render_template('favorite_product.html', p=fav, user="test name")

## Code to run the application...

# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
if __name__ == '__main__':
    db.create_all()
    app.run(use_reloader=True,debug=True)
