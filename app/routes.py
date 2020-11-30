from app import app,db
from app.models import *
from flask import redirect,render_template,url_for, jsonify, request,flash,session, make_response, abort
from flask_cors import cross_origin
from PIL import Image as pil_img
import base64
from binascii import a2b_base64
from app.decorators import login_required

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
	if form["image"]["data"]:
		with open("static/profile_pic/{}.{}".format(form["username"], form["image"]["ext"]), "wb") as img:
			data = base64.b64decode(form["image"]["data"])
			img.write( data )

	user_obj.image = "{}.{}".format(form["username"], form["image"]["ext"])
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
@login_required
def create_post():
	form=request.json
	print(form)
	user = User.verify_login_token( request.headers["Authentication"] )
	if user:
		post_obj=Post(
				title=form["title"],
				content=form["content"],
				user_id=user.id,
				# privacy=form["privacy"]
				privacy="followers"
			)

		
		db.session.add(post_obj)
		db.session.commit()		

		if form["image1"]["data"] and form["image1"]["ext"]:
			with open("static/post_img/{}.{}".format(str(post_obj.id)+"_1", form["image1"]["ext"]), "wb") as img:
				data = base64.b64decode(form["image1"]["data"])
				img.write( data )
			postImgObj = PostImage(post_id=post_obj.id, image="{}.{}".format(str(post_obj.id)+"_2", form["image1"]["ext"]) )
			db.session.add(postImgObj)

		if form["image2"]["data"] and form["image2"]["ext"]:
			with open("static/post_img/{}.{}".format(str(post_obj.id)+"_2", form["image2"]["ext"]), "wb") as img:
				data = base64.b64decode(form["image2"]["data"])
				img.write( data )
			postImgObj = PostImage(post_id=post_obj.id, image="{}.{}".format(str(post_obj.id)+"_2", form["image2"]["ext"]) )
			db.session.add(postImgObj)

		if form["image3"]["data"] and form["image3"]["ext"]:
			with open("static/post_img/{}.{}".format(str(post_obj.id)+"_3", form["image3"]["ext"]), "wb") as img:
				data = base64.b64decode(form["image3"]["data"])
				img.write( data )
			postImgObj = PostImage(post_id=post_obj.id, image="{}.{}".format(str(post_obj.id)+"_3", form["image3"]["ext"]) )
			db.session.add(postImgObj)

		db.session.commit()

		return jsonify({'status':'success','msg':'Post created successfully!'})
	abort(554)



@app.route("/validate_email", methods=["POST"], endpoint="validate_email")
@cross_origin()
def validate_email():
	form = request.json
	if "email" in form:
		if not User.query.filter_by(email=form["email"]).first():
			return jsonify({ "status": True })
		else:
			return jsonify({ "status": False, "msg": "This Email is already Exists." })
	abort(500)

@app.route("/validate_username", methods=["POST"], endpoint="validate_username")
@cross_origin()
def validate_username():
	form = request.json
	if "username" in form:
		if not User.query.filter_by(username=form["username"]).first():
			return jsonify({ "status": True })
		else:
			return jsonify({ "status": False, "msg": "This Username is already Exists." })
	abort(500)

@app.route("/validate_contact", methods=["POST"], endpoint="validate_contact")
@cross_origin()
def validate_contact():
	form = request.json
	if "contact" in form:
		if not User.query.filter_by(contact=form["contact"]).first():
			return jsonify({ "status": True })
		else:
			return jsonify({ "status": False, "msg": "This Contact is already Exists." })
	abort(500)