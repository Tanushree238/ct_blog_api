from app import app,db
from app.models import *
from flask import redirect,render_template,url_for, jsonify, request,flash,session, make_response
from flask_cors import cross_origin
from PIL import Image as pil_img

@app.route("/", methods=["GET","POST"] )
def home():
	return "Hello"


@app.route("/register_user", methods=["POST"], endpoint="register_user" )
@cross_origin()
def register_user():
	form=request.json
	user_obj=User(
			username=form["username"],
			name=form["name"],
			email=form["email"],
			contact=form["contact"],
			bio=form["bio"]
			)
	user_obj.set_password(form["password"])
	db.session.add(user_obj)
	db.session.commit()
	token = user_obj.get_login_token()
	return jsonify({'status':'success','token':token})


@app.route("contact_validation",methods=["POST"],endpoint="contact_validation")
def contact_validation():
	data = request.json
	user = User.query.filter_by(contact=data['contact']).first()
	if user==None:
		return jsonify({'status':'valid'})
	else:
		return jsonify({'status':'invalid'})


@app.route("username_validation",methods=["POST"],endpoint="username_validation")
def username_validation():
	data = request.json
	user = User.query.filter_by(username=data['username']).first()
	if user==None:
		return jsonify({'status':'valid'})
	else:
		return jsonify({'status':'invalid'})


@app.route("email_validation",methods=["POST"],endpoint="email_validation")
def email_validation():
	data = request.json
	user = User.query.filter_by(email=data['email']).first()
	if user==None:
		return jsonify({'status':'valid'})
	else:
		return jsonify({'status':'invalid'})


@app.route("/validate_login_token", methods=["POST"], endpoint="validate_login_token" )
@cross_origin()
def validate_login_token():
	form=request.json
	user=User.verify_login_token(form["token"])
	if user:
		return jsonify({'status':'valid'})
	else:
		return jsonify({'status':'invalid'})


@app.route("/login_user", methods=["POST"], endpoint="login_user" )
@cross_origin()
def login_user():
	form=request.json
	user=User.query.filter_by(username=form["username"]).first()
	if user and user.check_password(form["password"]):
		token = user.get_login_token()
		return jsonify({'status':'success','msg':'','token':token})
	else:
		return jsonify({'status':'error','msg':'Incorrect Username or Password! Please try again.'})


@app.route("/create_post", methods=["POST"], endpoint="create_post" )
@cross_origin()
def create_post():
	form=request.json
	user=User.query.filter_by(username=form["username"]).first()
	post_obj=Post(
			title=form["title"],
			content=form["content"],
			user_id=user.id,
			privacy=form["privacy"]
			)
	db.session.add(post_obj)
	db.session.commit()
	return jsonify({'status':'success','msg':'Post created successfully!'})


@app.route("/follow_user", methods=["POST"], endpoint="follow_user" )
@cross_origin()
def follow_user():
	form=request.json
	follower=User.query.filter_by(username=form["follower"]).first()
	following=User.query.filter_by(username=form["following"]).first()
	follow=Follow(
			follower_id=follower.id,
			followed_id=following.id
			)
	db.session.add(follow)
	db.session.commit()
	return jsonify({'status':'success','msg':'{} is now following {}'.format(follower.username,following.username)})

# Users followed by User(username)
@app.route("/following_users", methods=["POST"], endpoint="following_users" )
@cross_origin()
def following_users():
	form=request.json
	user=User.query.filter_by(username=form["username"]).first()
	following_users=[]
	for following_user in user.following.all():
		user={}
		user["username"]=following_user.following_user_obj.username
		user["name"]=following_user.following_user_obj.name
		following_users.append(user)
	return jsonify({'status':'success','following_users':following_users})

# Users following User(username)
@app.route("/followers", methods=["POST"], endpoint="followers" )
@cross_origin()
def followers():
	form=request.json
	user=User.query.filter_by(username=form["username"]).first()
	followers=[]
	for follower in user.follower.all():
		user={}
		user["username"]=follower.following_user_obj.username
		user["name"]=follower.following_user_obj.name
		followers.append(user)
	return jsonify({'status':'success','followers':followers})


@app.route("/is_following", methods=["POST"], endpoint="is_following" )
@cross_origin()
def is_following():
	form=request.json
	follower=User.query.filter_by(username=form["username"]).first()
	following=User.query.filter_by(username=form["is_following"]).first()
	follow_obj=Follow.query.filter_by(follower_id=follower.id,followed_id=following.id).first()
	if follow_obj:
		return jsonify({'is_following':'True'})
	else:
		return jsonify({'is_following':'False'})


@app.route("/like_post", methods=["POST"], endpoint="like_post" )
@cross_origin()
def like_post():
	form=request.json
	user=User.query.filter_by(username=form["username"]).first()
	post=Post.query.filter_by(id=form["post_id"]).first()
	post_like_obj=PostLike(
			user_id=user.id,
			post_id=post.id
			)
	db.session.add(post_like_obj)
	db.session.commit()
	return jsonify({'status':'success','msg':'{} liked post {}'.format(user.username,post.title)})


@app.route("/comment_post", methods=["POST"], endpoint="comment_post" )
@cross_origin()
def comment_post():
	form=request.json
	user=User.query.filter_by(username=form["username"]).first()
	post=Post.query.filter_by(id=form["post_id"]).first()
	post_comment_obj=PostComment(
			user_id=user.id,
			post_id=post.id,
			comment=form["comment"]
			)
	db.session.add(post_comment_obj)
	db.session.commit()
	return jsonify({'status':'success','msg':'{} commmented on post {}'.format(user.username,post.title)})


@app.route("/home_feed", methods=["POST"], endpoint="home_feed" )
@cross_origin()
def home_feed():
	form=request.json
	user=User.query.filter_by(username=form["username"]).first()
	posts=[]
	for follower in user.following.all():
		for follower_post in follower.follower_user_obj.post.all():
			if follower_post.privacy!="Only Me":
				post={}
				post["title"]=follower_post.title
				post["content"]=follower_post.content
				post["likes"]=follower_post.like.count()
				post["created_on"]=follower_post.created_on
				posts.append(post)
	posts.sort(reverse=True,key=lambda x: x["created_on"])
	return jsonify({'status':'success','posts':posts})


@app.route("/explore_feed", methods=["GET"], endpoint="explore_feed" )
@cross_origin()
def explore_feed():
	all_posts=Post.query.filter_by(privacy="public").limit(100)
	posts=[]
	for post in all_posts:
			valid_post={}
			valid_post["title"]=post.title
			valid_post["content"]=post.content
			valid_post["likes"]=post.like.count()
			valid_post["created_on"]=post.created_on
			posts.append(valid_post)
	posts.sort(reverse=True,key=lambda x: x["created_on"])
	return jsonify({'status':'success','posts':posts})
