from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import datetime

# to get the transaction date and time
now = datetime.datetime.now()

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/")
@login_required
def index():
    
    # get the rows from companies table
    rows = db.execute( "SELECT * FROM companies WHERE id = :id", id = session["user_id"] )
    
    total_cash = 0
    
    # update each symbol's price and total in companies
    for row in rows:
        symbol = row["symbol"]
        shares = row["shares"]
        stock = lookup(symbol)
        total = shares * stock["price"]
        total_cash += total
        db.execute( "UPDATE companies SET price = :price, total = :total WHERE id = :id AND symbol = :symbol", price = stock["price"], total = total, id = session["user_id"], symbol = symbol )
    
    
    
    # get the remaining cash from users table
    user = db.execute( "SELECT * FROM users WHERE id = :id", id = session["user_id"] )

    
    
    cash = float(user[0]["cash"])
    
    # add cash to total cash
    total_cash += cash
    
    # usd cash and total cash
    cash = usd(cash)
    total_cash = usd(float(total_cash))
    
    # get the data from updated companies table
    rows = db.execute( "SELECT * FROM companies WHERE id = :id", id = session["user_id"] )
    
    return render_template( "index.html", rows = rows, cash = cash, total = total_cash )
    
    
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""
    
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol")

        # ensure number of shares was submitted
        elif not request.form.get("shares"):
            return apology("must provide number of shares")
            
        # store the number of shares and symbol 
        sym = request.form.get("symbol")
        no = request.form.get("shares")
        # convert into integer
        no = int(no)
        
        
        # check for proper usage of shares and symbol
        if no < 0:
            return apology("Invalid shares!")
        if not lookup(sym):
            return apology("Invalid symbol!")
        
        # convert into float
        no = float(no)
            
        cash = db.execute("SELECT * FROM users WHERE id = :id", id = session["user_id"])
        # lookup for the symbol
        rate = lookup(sym) 
        
        # check whether user can afford the buy
        if cash[0]["cash"] < rate["price"] * no:
            return apology("Cannot Afford.")
        
        
        # insert the buy in history table
        db.execute( "INSERT INTO history( id, symbol, shares, price, time ) VALUES( :id, :sym, :no, :price, :time )", id = session["user_id"], sym = rate["symbol"], no = no, price = rate["price"], time = now.strftime("%Y-%m-%d %H:%M:%S"))
        
        # subtract user's cash in users table
        db.execute( "UPDATE users SET cash = cash - :price WHERE id = :id", price = rate["price"] * no, id = session["user_id"] )
        
        shares = db.execute( "SELECT * FROM companies WHERE id = :id AND symbol = :sym", id = session["user_id"], sym = rate["symbol"] )
        
        # if the number of previously bought shares of that company is zero
        if not shares:
            db.execute( "INSERT INTO companies( name, shares, price, total, symbol, id ) VALUES( :name, :shares, :price, :total, :symbol, :id )", name = rate["name"], shares = no, price = rate["price"], total=no * rate["price"], symbol=rate["symbol"], id=session["user_id"] )
            
        # else just increase values in companies table
        else:
            db.execute( "UPDATE companies SET shares = shares + :no, total = total + :total WHERE id = :id AND symbol = :sym", no = no, total = rate["price"] * no, id = session["user_id"], sym = rate["symbol"] )
        
        return redirect(url_for("index"))

    else:
        return render_template("buy.html")
        

@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    
    # get the rows of that user from history table
    rows = db.execute( "SELECT * FROM history WHERE id = :id", id = session["user_id"] )
    
    return render_template( "history.html", rows = rows )

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    
    if request.method == "POST":
        
        # lookup for the symbol
        quote = lookup(request.form.get("quote"))
        
        if not quote:
            return apology("Invalid Symbol!")
    
        # when the symbol is correct return the quote
        return render_template("quoted.html", sym = quote)
    else:
        return render_template("quote.html")
    

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    
    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")
            
        # ensure password was entered again
        elif not request.form.get("password1"):
            return apology("must re-enter password")
            
        # ensure that the passwords match
        if request.form.get("password") != request.form.get("password1"):
            return apology("Passwords doesn't match!")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username is available
        if len(rows) == 1: 
            return apology("Sorry, username already taken.")

        
        # insert data into the database
        user = db.execute("INSERT INTO users ( username, hash ) VALUES( :username, :pwhash )", username = request.form.get("username"), pwhash = pwd_context.encrypt(request.form.get("password")))
        
        # remember which user has logged in
        session["user_id"] = user
        
        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
    

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol")

        # ensure number of shares was submitted
        elif not request.form.get("shares"):
            return apology("must provide number of shares")
            
        # store the number of shares and symbol 
        sym = request.form.get("symbol")
        no = request.form.get("shares")
        
        # convert into integer
        no = int(no)
        rate = lookup(sym)
        
        # check for proper usage of shares and symbol
        if no < 0:
            return apology("Invalid shares!")
        if not rate:
            return apology("Invalid symbol!")

            
        cash = db.execute("SELECT * FROM companies WHERE id = :id AND symbol = :sym", id = session["user_id"], sym = rate["symbol"] )
        
        # if that symbol or that much shares isn't owned
        if not cash:
            return apology("Shares of that company not owned!")
        elif cash[0]["shares"] < no:
            return apology("That many shares not owned!")
            
            
        # insert the sell in history table
        db.execute( "INSERT INTO history( id, symbol, shares, price, time ) VALUES( :id, :sym, :no, :price, :time )", id = session["user_id"], sym = rate["symbol"], no = -no, price = rate["price"], time = now.strftime("%Y-%m-%d %H:%M:%S"))
        
        # add user's cash in users table
        db.execute( "UPDATE users SET cash = cash + :price WHERE id = :id", price = rate["price"] * no, id = session["user_id"] )
        
        # retrieve data from companies table
        shares = db.execute( "SELECT * FROM companies WHERE id = :id AND symbol = :sym", id = session["user_id"], sym = rate["symbol"] )
        
        
        # incase shares got over delete that companies's row
        if shares[0]["shares"] - no == 0:
            db.execute( "DELETE FROM companies WHERE id = :id AND symbol = :sym", id = session["user_id"], sym = rate["symbol"] )
        
        
        # else just update it
        else:
            db.execute( "UPDATE companies SET shares = shares - :no, total = total - :total WHERE id = :id AND symbol = :sym", no = no, total = rate["price"] * no, id = session["user_id"], sym = rate["symbol"] )
        
        return redirect(url_for("index"))
        
    else:
        return render_template("sell.html")
        
        
@app.route("/reset_password", methods=["GET", "POST"])
@login_required
def reset_password():
    """Reset password."""

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure new password was submitted
        if not request.form.get("password1"):
            return apology("must provide new password")

        # ensure new password was submitted again
        elif not request.form.get("password2"):
            return apology("must provide new password again")
            
            
        # ensure that the passwords match
        if request.form.get("password1") != request.form.get("password2"):
            return apology("Passwords doesn't match!")


        
        # insert data into the database
        db.execute( "UPDATE users SET hash = :pwhash WHERE id = :id", pwhash = pwd_context.encrypt(request.form.get("password1")), id = session["user_id"])
        
        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("reset.html")