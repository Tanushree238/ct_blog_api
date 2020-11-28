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
	print(form)
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