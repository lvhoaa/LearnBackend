import json

from db import db
from flask import Flask, request

db_filename = "auth.db"
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()


# generalized response formats
def success_response(data, code=200):
    return json.dumps(data), code
def failure_response(message, code=404):
    return json.dumps({"error": message}), code


def get_user_by_email(email):
    return User.query.filter(User.email ==email).first()

def get_user_by_session_token(session_token):
    return User.query.filter(User.session_token == session_token).first() 

def get_user_by_update_token(update_token):
    return User.query.filter(User.update_token ==update_token)

def extract_token(request):
    # Token is sent through the bearer in the header 
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return False, json.dumps({'error':'Missing auth header'})
    bearer_token = auth_header.replace("Bearer: ",'').strip()
    if not bearer_token:
        return False, json.dumps({'error':'Invalid auth header'})
    return True,bearer_token


@app.route("/")
def hello_world():
    return json.dumps({'Message':'Hello World!!'})


@app.route("/register/", methods=["POST"])
def register_account():
    body = json.loads(request.data)
    email = body.get('email')
    password = body.get('password')
    
    if email is None or password is None:
        return json.dumps({'error':'Invalid email or password'})
    
    # check if user exists already 
    optional_user =get_user_by_email(email)
    if optional_user:
        return json.dumps({'error':'User already exists error'})
    
    user = User(email=email,password = password)
    
    db.session.add(user)
    db.session.commit() 
    
    # session token sent back explicitly -- 
    return json.dumps({
        'Success':True,
        'session_token':user.session_token,
        'session_expiration': str(user.session_expiration),
        'update_token':user.update_token        
    })
    
@app.route("/login/", methods=["POST"])
def login():
    body = json.loads(request.data)
    email = body.get('email')
    password = body.get('password')
    
    user = get_user_by_email(email)
    
    success = user is not None and user.verify_password(password)
    if not success:
        return json.dumps({'error':"Invalid email or password"})
    return json.dumps({
        'Success':True,
        'session_token':user.session_token,
        'session_expiration': str(user.session_expiration),
        'update_token':user.update_token        
    })


@app.route("/session/", methods=["POST"])
def update_session():
    # Run update session WHEN client sends the update_token in the headers 
    success, update_token = extract_token(request)
    if not success:
        return update_token 
    user = get_user_by_update_token(update_token)
    if not user:
        return json.dumps({"error":"Invalid update token"})
    
    user.renew_session() #when updated: create new session
    db.session.commit()
    return json.dumps({
        'Success':True,
        'session_token':user.session_token,
        'session_expiration': str(user.session_expiration),
        'update_token':user.update_token        
    })


@app.route("/secret/", methods=["GET"])
def secret_message():
    success, session_token= extract_token(request)
    if not success:
        return session_token
    user=get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return json.dumps({'Error':'Invalid session token '})
    return json.dumps({'Message':"You've successfully implemented sessions!!"})
    

@app.route("/logout/", methods=["POST"])
def logout():
    """
    Endpoint for logging out a user
    """
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
