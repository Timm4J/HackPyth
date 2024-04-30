from ticket import app, db
from flask import render_template, request, flash, url_for, redirect
from sqlalchemy import text
import os
from nanoid import generate
nanoidSize = 10
picturesFolder =  os.path.join(os.path.dirname(os.path.abspath(__file__)), "static","uploads")

@app.route('/')
def homePage():
    keks = request.cookies.get("name")
    print("routes.py", "homePage()", "cookie=", keks)
    if not keks:
        print("No cookie")
        return redirect(url_for('login_page'))
    
    # redirect zu myrRcipes mit cookie
    return redirect(url_for('myRecipes'))



@app.route('/tickets')
def ticketsPage():
    stmt = f"select * from bugitems"
    result = db.session.execute(text(stmt))
    itemsquery = result.fetchall()
    print(itemsquery)
    return render_template('tickets.html', items=itemsquery)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        print(username)
        print(password)

        if username is None or isinstance(username, str) is False or len(username) < 3:
            print("Not valid")
            #flash(f"Username is not valid", category='warning')
            return render_template("login.html")

        if password is None or isinstance(password, str) is False or len(password) < 3:
            print("wrong password")
            #flash(f"Password not valid")
            return render_template("login.html")

        stmt = f"select userName from user where userName = '{username}' and userPassword = '{password}'"
        res = db.session.execute(text(stmt))
        user = res.fetchall()

        if user:
            #flash("Unknown user or invalid pasword")
            #flash(f"You are now logged in {user}", category="success")

            # cookie setzen und weiterleiten
            resp = redirect("/recipes")
            resp.set_cookie("name", username)
            return resp
            

    return render_template("login.html")


@app.route('/logout')
def logout():
    resp = redirect("/login")
    resp.set_cookie("name", "", expires=0)
    return resp


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmPassword = request.form.get("confirmPassword")

        print(email)
        print(username)
        print(password)
        print(confirmPassword)

        if username is None or isinstance(username, str) is False or len(username) < 3:
            print("Register: Username nto valid")
            #flash("Username not valid", category="danger")

        if email is None or isinstance(email, str) is False or len(email) < 3:
            print("Register:  not valid")
            #flash("Username not valid", category="danger")
            return render_template("register.html")

        if password is None or isinstance(password, str) is False or len(password) < 3 or password != confirmPassword:
            print("Register:  not valid")
            #flash("Username not valid", category="danger")
            return render_template("register.html")

        stmt = f"select * from user where userName = '{username}'"
        res = db.session.execute(text(stmt))
        item = res.fetchone()
        print(item)

        if item is not None:
            #flash("Username already exists, please choose another one")
            print("Register: username already exists")
            return render_template("register.html")

        stmt = f"insert into user (userMail,userName,userPassword) values('{email}', '{username}', '{password}')"
        res = db.session.execute(text(stmt))
        db.session.commit()  # WICHTIG
        #flash("Erfolgreich registriert")

        resp = redirect("/recipes")
        resp.set_cookie("name", username)
        return resp

    return render_template("register.html")


@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")


# neue route zu recipe
@app.route('/recipes')
def recipe():
    keks = request.cookies.get("name")
    print("routes.py", "recipe()","cookie=",keks)

    sql = "select * from recipes"
    result = db.session.execute(text(sql))
    recipes = result.fetchall()

    return render_template('recipes.html', cookie=keks, items=recipes)

# neue route für new_recipe
@app.route('/new_recipe', methods=['GET', 'POST'])
def newRecipe():
    keks = request.cookies.get("name")
    print("routes.py", "newRecipe()","cookie=",keks)

    if request.method == "GET":
        if not keks:
            return redirect(url_for('login_page'))
        return render_template('new_recipe.html', cookie=keks)

    if request.method == "POST":
        
        title = request.form.get("title")
        description = request.form.get("description")
        imageFile = request.files.get('image')
        print(imageFile)
        nanoid = generate(size=nanoidSize)
        filename = nanoid + ".jpg"
        fullfilename = picturesFolder + "\\" + filename
        #fileURL = f"pictures/{imageFile.filename}"
        imageFile.save(fullfilename)

        stmt = f"insert into recipes (title, description, image, creator) values ('{title}', '{description}', 'static/uploads/{filename}', '{keks}')"
        res = db.session.execute(text(stmt))
        db.session.commit()

        return redirect(url_for('recipe'))

    return render_template('new_recipe.html', cookie=keks)


@app.route('/myrecipes')
def myRecipes():
    keks = request.cookies.get("name")
    print("routes.py", "myRecipes()","cookie=",keks)

    if not keks:
        return redirect(url_for('login_page'))

    stmt = f"select * from recipes where creator = '{keks}'"
    res = db.session.execute(text(stmt))
    items = res.fetchall()

    return render_template('recipes.html', cookie=keks, items=items, own_recipes=True)


# route zum deleten eines Rezepts
@app.route('/delete_recipe/<int:id>')
def deleteRecipe(id):
    keks = request.cookies.get("name")
    print("routes.py", "deleteRecipe()","cookie=",keks)

    if not keks:
        return redirect(url_for('login_page'))

    stmt = f"select * from recipes where id = {id}"
    res = db.session.execute(text(stmt))
    recipe = res.fetchone()

    if recipe.creator != keks:
        return redirect(url_for('myRecipes'))

   

    stmt = f"delete from recipes where id = {id}"
    res = db.session.execute(text(stmt))
    db.session.commit()

    return redirect(url_for('myRecipes'))

# Route zum anzeigen eines Rezepts
@app.route('/recipe/<int:id>')
def showRecipe(id):
    keks = request.cookies.get("name")
    print("routes.py", "showRecipe()","cookie=",keks)

    if not keks:
        return redirect(url_for('login_page'))

    stmt = f"select * from recipes where id = {id}"
    res = db.session.execute(text(stmt))
    recipe = res.fetchone()

    return render_template('recipe_detail.html', cookie=keks, item=recipe)
