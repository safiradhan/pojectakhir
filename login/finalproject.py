from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_cors import CORS, cross_origin
import base64
import uuid

cors_config = {
    "origins": ["http://127.0.0.1:5001"],
    "methods": ["GET", "POST", "PUT", "DELETE"]
}
app = Flask(__name__)
CORS(app, resources={
    r"/*": cors_config
})
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:postgres@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key= True, index=True)
    full_name = db.Column(db.String(100), nullable= False)
    user_name = db.Column(db.String(100), nullable= False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), default=False, unique=True)
    last_login = db.Column(db.DateTime, nullable=False)
    user_tweet = db.relationship('post', backref = 'ustweet', lazy = 'dynamic')
    user_follow = db.relationship('follow', backref = 'usfol', lazy = 'dynamic')
    user_favorite = db.relationship('report', backref = 'rep_us', lazy = 'dynamic')
    # user_aktivitas = db.relationship('aktivitas', backref = 'akt_us', lazy = 'dynamic')
class tweet(db.Model):
    tweet_id = db.Column(db.Integer, primary_key= True, index=True)
    content = db.Column(db.String(100), nullable= False)
    fav_tweet = db.relationship('favorite', backref = 'favtweet', lazy = 'dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable = False)

class follow(db.Model):
    follow_id = db.Column(db.Integer, primary_key= True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable = False)

class favorite(db.Model):
    favorite_id = db.Column(db.Integer, primary_key= True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable = False)
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.tweet_id'), nullable = False)

def get_hash(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def auth():
    token = request.headers.get('Authorization')
    token2 = token.replace("Basic ","")
    plain = base64.b64decode(token2).decode('utf-8')
    auth_data = plain.split(":")
    return auth_data

def get_username(auth_data):
    username = auth_data[0]
    return username

def data_user(auth_data):
    user = User.query.filter_by(user_name=auth_data[0]).first()
    a = False
    if user is None :
        return a 

def get_password(auth_data):
    user = User.query.filter_by(user_name=auth_data[0]).first()
    password = bcrypt.generate_password_hash(auth_data[1]).decode('utf-8')
    check = bcrypt.check_password_hash(user.password, password)
    return check #returns true if valid

def get_userData(id):
    return User.query.filter_by(user_id=id).first_or_404()

def return_user(u):
    return {'User id' : u.user_id,'Username':u.user_name,'Full name':u.full_name, 'Email' : u.email, 'user history': u.user_history}
############################################################ -endpoint user-  #################################################################

@app.route('/users/', methods=['POST'])
def create_user():
    data = request.get_json()
    if (not 'user_name' in data) or (not 'email' in data) or (not 'password' in data) or (not 'full_name' in data) :
        return jsonify({
            'error': 'Bad Request',
            'message': 'Data yang anda masukkan tidak tepat'
        }), 400
    if (len(data['user_name']) < 4) or (len(data['email']) < 4) or (len(data['password']) < 4) or (len(data['full_name']) < 4):
        return jsonify({
            'error' : 'Bad Request',
            'message' : 'Data yang anda masukkan salah'
        }), 400
    hash = get_hash(data['password'])
    u = User(
        user_name= data['user_name'],
        email= data['email'],
        full_name = data['full_name'],
        password= hash
    )
    db.session.add(u)
    db.session.commit()
    return return_user(u), 201

@app.route('/users/<id>/', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    user = get_userData(id)
    if 'full_name' in data:
        user.full_name=data['full_name']
    if 'user_name' in data:
        user.user_name=data['user_name']
    if 'email' in data:
        user.email=data['email']
    if 'user_history' in data:
        user.user_history=data['user_history']
    db.session.commit()

    return {
        'full_name': user.full_name,
        'user_id': user.user_id,
        'user_name': user.user_name,
        'email': user.email,
        'user_history': user.user_history,
        'password': user.password
    }

@app.route('/users/', methods = ["GET"])
def get_user():
    login = auth()
    if data_user(login): 
        return jsonify({
            'error' : 'Bad Request',
            'message' : 'Username is not registered'
            }), 400
    else:
        if get_password(login):
            return jsonify({
            'error' : 'Bad Request',
            'message' : 'Wrong Password'
            }), 400

@app.route('/users/<id>/', methods=['DELETE'])
def delete_user(id):
    login = auth()
    if data_user(login): 
        return jsonify({
            'error' : 'Bad Request',
            'message' : 'Username is not registered'
        }), 400
    else:
        if get_password(login): 
            return jsonify({
            'error' : 'Bad Request',
            'message' : 'Wrong Password'
        }), 400
        else:
            user = User.query.filter_by(user_id=id).first_or_404()
            db.session.delete(user)
            db.session.commit()
            return {'success': 'User data deleted successfully'}
############################################################ -endpoint follow- ################################################################
@app.route('/follow/', methods=['POST'])
def create_follow():
    login = auth()
    if data_user(login): 
        return jsonify({
            'error' : 'Bad Request',
            'message' : 'Username is not registered'
            }), 400
    else:
        if get_password(login):
            return jsonify({
            'error' : 'Bad Request',
            'message' : 'Wrong Password'
            }), 400
        else: 
            data = request.get_json()
            if not 'followers' in data:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'followers is not given'
                }), 400
            if not 'following' in data:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'following is not given'
                }), 400
            if not 'unfollow' in data:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'unfollow is not given'
                }), 400
            if len(data['followers']) < 0:
                return jsonify({
                    'error' : 'followers',
                    'message' : 'followers must contain a minimum of 0 letters'
                }), 400
            if len(data['following']) < 0:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'following must contain a minimum of 0 letters'
                }), 400
            if len(data['unfollow']) < 0:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'unfollow must contain a minimum of 0 letters'
                }), 400
            f = follow(
                    followers = data['followers'],
                    following = data['following'],
                    unfollow = data['unfollow'],
                    user_id = data['user_id']
                )
            db.session.add(f)
            db.session.commit()
            return  return_follow(f), 201

@app.route('/follow/<id>/', methods=['PUT'])
def update_follow(id):
    data = request.get_json()
    user = get_followData(id)
    if 'followers' in data:
        follow.followers=data['followers']
    if 'following' in data:
        follow.following=data['following']
    if 'unfollow' in data:
        follow.unfollow=data['unfollow']
    db.session.commit()

    return {
        'followers': follow.followers,
        'following': follow.following,
        'unfollow': follow.unfollow
    }
# @app.route('/follow/', methods = ["GET"])
# def get_user():
#     login = auth()
#     if data_user(login): 
#         return jsonify({
#             'error' : 'Bad Request',
#             'message' : 'Username is not registered'
#             }), 400
#     else:
#         if get_password(login):
#             return jsonify({
#             'error' : 'Bad Request',
#             'message' : 'Wrong Password'
#             }), 400

########################################## endpoint post 

@app.route('/post/', methods=['POST'])
def create_post():
    login = auth()
    if data_user(login): 
        return jsonify({
            'error' : 'Bad Request',
            'message' : 'Username is not registered'
            }), 400
    else:
        if get_password(login):
            return jsonify({
            'error' : 'Bad Request',
            'message' : 'Wrong Password'
            }), 400
        else: 
            data = request.get_json()
            if not 'post tweet' in data:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'post tweet is not given'
                }), 400
            if not 'like' in data:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'like is not given'
                }), 400
            if len(data['post tweet']) > 280:
                return jsonify({
                    'error' : 'post tweet',
                    'message' : 'post tweet must contain a maximal of 280 chars'
                }), 400
            # if len(data['like']) < 0:
            #     return jsonify({
            #         'error' : 'Bad Request',
            #         'message' : 'like must contain a maximum of 1 like/users'
            #     }), 400
            p = post( 
                    post_tweet = data['post tweet'],
                    like = data['like'],
                    user_id = data['user_id']
                )
            db.session.add(p)
            db.session.commit()
            return  return_post(p), 201

@app.route('/post/', methods=['PUT'])
def update_post():
    data = request.get_json()
    post = get_postData(id)
    if 'post tweet' in data:
        post.post_tweet=data['post tweet']
    if 'like' in data:
        post.like=data['like']
    p = post(
        post_tweet = data['post tweet'],
        like = data['like'],
        user_id = data['user_id']
    )
    db.session.commit()
    return  return_post(p), 201
######################################### 
@app.route('/aktivitas/', methods=['POST'])
def create_aktivitas():
    login = auth()
    if data_user(login): 
        return jsonify({
            'error' : 'Bad Request',
            'message' : 'Username is not registered'
            }), 400
    else:
        if get_password(login):
            return jsonify({
            'error' : 'Bad Request',
            'message' : 'Wrong Password'
            }), 400
        else: 
            data = request.get_json()
            if not 'list tweet' in data or not 'search user' in data or not 'search tweet' in data:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'Data yang anda masukan salah'
                }), 400
            if len(data['list tweet']) < 1:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'list_tweet must contain a maximal 1 chars'
                }), 400
            if len(data['search user']) < 1:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'search_user must contain a maximum of 1 chars'
                }), 400
            if len(data['search tweet']) < 1:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'search_tweet must contain a maximum of 1 chars'
                }), 400
            a = aktivitas( 
                    list_tweet = data['list tweet'],
                    search_user = data['search user'],
                    search_tweet = data['search tweet'],
                    user_id = data['user_id']
                    # post_id = data['post id']
                )
            db.session.add(a)
            db.session.commit()
            return  return_aktivitas(a), 201

@app.route('/aktivitas/<id>/', methods=['GET'])
def all_tweet():
    login = auth()
    if data_user(login): 
        return jsonify({
            'error' : 'Bad Request',
            'message' : 'Username is not registered'
            }), 400
    else:
        if get_password(login):
            return jsonify({
            'error' : 'Bad Request',
            'message' : 'Wrong Password'
            }), 400
        else: 
            data = request.get_json()
                # return the result
            return jsonify([
                {
                    'list tweet' : all_tweet.list_tweet,
                    'search_user' : all_tweet.search_user,
                    'search_tweet' : all_tweet.search_tweet
                    }
                    for akt in aktivitas.query.all()
                ]), 200
            return {
                    'message' : 'Wrong Password'
                }, 400

@app.route('/report/', methods=['POST'])
def create_reportdata():
    login = auth()
    if data_user(login): 
        return jsonify({
            'error' : 'Bad Request',
            'message' : 'Username is not registered'
            }), 400
    else:
        if get_password(login):
            return jsonify({
            'error' : 'Bad Request',
            'message' : 'Wrong Password'
            }), 400
        else: 
            data = request.get_json()
            if not 'post tweet' in data:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'post tweet is not given'
                }), 400
            if not 'popular user' in data:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'popular user is not given'
                }), 400
            if not 'popular tweet' in data:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'popular tweet is not given'
                }), 400
            if not 'innactive user' in data:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'innactive is not given'
                }), 400
            if len(data['popular tweet']) > 0:
                return jsonify({
                    'error' : 'post tweet',
                    'message' : 'post tweet must contain a maximal of 280 chars'
                }), 400
            if len(data['popular user']) < 0:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'like must contain a maximum of 1 like/users'
                }), 400
            if len(data['innactive user']) < 0:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'like must contain a maximum of 1 like/users'
                }), 400
            r = report( 
                    popular_tweet = data['popular'],
                    popular_user = data['popular user'],
                    innacative_user = data['innactive user'],
                    user_id = data['user_id']
                )
            db.session.add(r)
            db.session.commit()
            return  return_post(r), 201

@app.route('/report/', methods=['POST'])
def create_report():
    login = auth()
    if data_user(login): 
        return jsonify({
            'error' : 'Bad Request',
            'message' : 'Username is not registered'
            }), 400
    else:
        if get_password(login):
            return jsonify({
            'error' : 'Bad Request',
            'message' : 'Wrong Password'
            }), 400
        else: 
            data = request.get_json()
            if not 'popular user' in data:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'popular user tweet is not given'
                }), 400
            if not 'popular tweet' in data:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'popular tweet is not given'
                }), 400
            if not 'innactive user' in data:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'innactive user is not given'
                }), 400
            if len(data['popular user']) < 1:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'popular user must contain a maximal 1 chars'
                }), 400
            if len(data['popular tweet']) < 1:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'popular tweet must contain a maximum of 1 chars'
                }), 400
            if len(data['innactive user']) < 1:
                return jsonify({
                    'error' : 'Bad Request',
                    'message' : 'innactive user must contain a maximum of 1 chars'
                }), 400
            r = report(
                    popular_user = data['popular_user'],
                    popular_tweet = data['popular tweet'],
                    innactive_user = data['innactive user'],
                    user_id = data['user_id'],
                    post_id = data['post id']
                )
            db.session.add(r)
            db.session.commit()
            return  return_aktivitas(r), 201
####################

@app.route('/report/', methods=['GET'])
def popular_user():
    return jsonify([
        {
            'Username' : data.usfol.user_name,
            'Followers' : data.followers
        }
        for data in follow.query.filter(follow.followers > 1).order_by(follow.followers.desc()).limit(1)
    ]), 200

@app.route('/report/tweet/', methods=['GET'])
def popular_tweet():
    return jsonify([
        {
            'post tweet' : data.post_tweet,
            'Username' : data.uspost.user_name,
            'like' : data.like
        }
        for data in post.query.filter(post.like > 1).order_by(post.like.desc())
    ]), 200

# @app.route('/report/innactive/', methods=['GET'])
# def innactive_user():
#     return jsonify([
#         {
#             'user history' : data.user_history,

#         }
#         for data in User.query.filter(User.user_history > ).order_by(post.like.desc())
#     ]), 200


# if __name__ == '__main__':
    app.run(debug = True)