from app import app,db
from app.models import *
from flask import redirect,render_template,url_for, jsonify, request,flash,session, make_response, abort
from flask_cors import cross_origin
from PIL import Image as pil_img
import base64
from binascii import a2b_base64
from app.decorators import login_required
import math
import os

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
		with open("app/static/profile_pic/{}.{}".format(form["username"], form["image"]["ext"]), "wb") as img:
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
				read_time = math.ceil(len(form["content"].split())/125),
				# privacy=form["privacy"]
				privacy="Followers"
			)

		
		db.session.add(post_obj)
		db.session.commit()		

		if form["image1"]["data"] and form["image1"]["ext"]:
			with open("app/static/post_img/{}.{}".format(str(post_obj.id)+"_1", form["image1"]["ext"]), "wb") as img:
				data = base64.b64decode(form["image1"]["data"])
				img.write( data )
			postImgObj = PostImage(post_id=post_obj.id, image="{}.{}".format(str(post_obj.id)+"_1", form["image1"]["ext"]) )
			db.session.add(postImgObj)

		if form["image2"]["data"] and form["image2"]["ext"]:
			with open("app/static/post_img/{}.{}".format(str(post_obj.id)+"_2", form["image2"]["ext"]), "wb") as img:
				data = base64.b64decode(form["image2"]["data"])
				img.write( data )
			postImgObj = PostImage(post_id=post_obj.id, image="{}.{}".format(str(post_obj.id)+"_2", form["image2"]["ext"]) )
			db.session.add(postImgObj)

		if form["image3"]["data"] and form["image3"]["ext"]:
			with open("app/static/post_img/{}.{}".format(str(post_obj.id)+"_3", form["image3"]["ext"]), "wb") as img:
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


@app.route("/follow_user", methods=["POST"], endpoint="follow_user" )
@cross_origin()
@login_required
def follow_user():
	form=request.json
	follower = User.verify_login_token( request.headers["Authentication"] )
	following=User.query.filter_by(username=form["following"]).first()
	if( "status" in form and following ):
		follow_obj = Follow.query.filter_by(follower_id=follower.id, followed_id=following.id).first()
		if( form["status"] ):
			if not follow_obj:
				follow=Follow(
						follower_id=follower.id,
						followed_id=following.id
						)
				db.session.add(follow)
				db.session.commit()
		else:
			db.session.delete(follow_obj)
			db.session.commit()
		return jsonify({'status':'success'})
	else:
		abort(500)


# Users followed by User(username)
@app.route("/following_users", methods=["POST"], endpoint="following_users" )
@cross_origin()
@login_required
def following_users():
	form=request.json
	user = User.verify_login_token( request.headers["Authentication"] )
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
@login_required
def followers():
	form=request.json
	user = User.verify_login_token( request.headers["Authentication"] )
	followers=[]
	for follower in user.follower.all():
		user={}
		user["username"]=follower.following_user_obj.username
		user["name"]=follower.following_user_obj.name
		followers.append(user)
	return jsonify({'status':'success','followers':followers})


@app.route("/is_following", methods=["POST"], endpoint="is_following" )
@cross_origin()
@login_required
def is_following():
	form=request.json
	user = User.verify_login_token( request.headers["Authentication"] )
	following=User.query.filter_by(username=form["is_following"]).first()
	follow_obj=Follow.query.filter_by(follower_id=follower.id,followed_id=following.id).first()
	if follow_obj:
		return jsonify({'is_following':'True'})
	else:
		return jsonify({'is_following':'False'})


@app.route("/like_post", methods=["POST"], endpoint="like_post" )
@cross_origin()
@login_required
def like_post():
	form=request.json
	user = User.verify_login_token( request.headers["Authentication"] )
	post=Post.query.filter_by(id=form["post_id"]).first()
	if(form["status"]):
		if( not PostLike.query.filter_by(user_id=user.id, post_id=post.id).first() ):
			post_like_obj=PostLike(
					user_id=user.id,
					post_id=post.id
					)
			db.session.add(post_like_obj)
			db.session.commit()
	else:
		likeObj = PostLike.query.filter_by(user_id=user.id, post_id=post.id).first()
		if( likeObj ):
			db.session.delete(likeObj)
			db.session.commit() 
	return jsonify({'status':'success','msg':'{} liked post {}'.format(user.username,post.title), "likes": post.like.count() })


@app.route("/comment_post", methods=["POST"], endpoint="comment_post" )
@cross_origin()
@login_required
def comment_post():
	form=request.json
	user = User.verify_login_token( request.headers["Authentication"] )
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
@login_required
def home_feed():
	form=request.json
	user = User.verify_login_token( request.headers["Authentication"] )
	posts=[]
	
	for my_post in user.post.all():
		post={}
		post["id"]=my_post.id
		post["title"]=my_post.title
		post["username"]=my_post.post_user_obj.username
		post["content"]=my_post.content
		post["read_time"]=my_post.read_time if my_post.read_time else 0
		post["likes"]=my_post.like.count()
		post["is_liked"]= True if PostLike.query.filter_by(post_id=my_post.id,user_id=user.id).first() else False 
		post["created_on"]=my_post.created_on

		if my_post.images.first():
			img_path = "app/static/post_img/{}".format( my_post.images.first().image )
			if os.path.isfile(img_path):
				with open(img_path, "rb") as img:
					imgUri = "data:image/{};base64,".format( my_post.images.first().image.split(".")[-1] ) + str(base64.b64encode(img.read()))[2:][:-1]
					post["image"]=imgUri
			else:
				print(my_post.images.first().image, "error1")
		else:
			print("error2")

		posts.append(post)

	for follower in user.following.all():
		for follower_post in follower.follower_user_obj.post.all():
			if follower_post.privacy!="Only Me":
				post={}
				post["id"]=follower_post.id
				post["title"]=follower_post.title
				post["username"]=follower_post.post_user_obj.username
				post["content"]=follower_post.content
				post["read_time"]=follower_post.read_time if follower_post.read_time else 0
				post["is_liked"]= True if PostLike.query.filter_by(post_id=follower_post.id,user_id=user.id).first() else False 
				post["likes"]=follower_post.like.count()
				post["created_on"]=follower_post.created_on
				
				if follower_post.images.first():
					img_path = "app/static/post_img/{}".format( follower_post.images.first().image )
					if os.path.isfile(img_path):
						with open(img_path, "rb") as img:
							imgUri = "data:image/{};base64,".format( follower_post.images.first().image.split(".")[-1] ) + str(base64.b64encode(img.read()))[2:][:-1]
							post["image"]=imgUri
					else:
						print(follower_post.images.first().image, "error1")
				else:
					print("error2")
				
				posts.append(post)
	posts.sort(reverse=True,key=lambda x: x["created_on"])
	return jsonify({'status':'success','posts':posts})


@app.route("/fetch_post_data", methods=["POST"], endpoint="fetch_post_data" )
@cross_origin()
@login_required
def fetch_post_data():
	form = request.json
	user = User.verify_login_token( request.headers["Authentication"] )
	if "post_id" in form:
		post_obj = Post.query.get(int(form["post_id"]))
		post = {}

		post["id"]=post_obj.id
		post["title"]=post_obj.title
		post["username"]=post_obj.post_user_obj.username
		post["content"]=post_obj.content
		post["read_time"]=post_obj.read_time if post_obj.read_time else 0
		post["is_liked"]= True if PostLike.query.filter_by(post_id=post_obj.id,user_id=user.id).first() else False 
		post["no_of_likes"]=post_obj.like.count()
		post["is_following"]= True if Follow.query.filter_by(follower_id=user.id, followed_id=post_obj.post_user_obj.id).first() else False
		post["no_of_comments"]=post_obj.comment.count()
		post["created_on"]=post_obj.created_on

		if user.image:
			img_path = "app/static/profile_pic/{}".format( user.image )
			if os.path.isfile(img_path):
				with open(img_path, "rb") as img:
					imgUri = "data:image/{};base64,".format( user.image.split(".")[-1] ) + str(base64.b64encode(img.read()))[2:][:-1]
					post["profile_pic"]=imgUri
			else:
				print(user.image, "error1")
		else:
			print("error2")


		for img_obj in enumerate(post_obj.images.limit(3)):
			img_name = img_obj[1].image
			img_path = "app/static/post_img/{}".format( img_name )
			if os.path.isfile(img_path):
				with open(img_path, "rb") as img:
					imgUri = "data:image/{};base64,".format( img_name.split(".")[-1] ) + str(base64.b64encode(img.read()))[2:][:-1]
					post["image"+str(img_obj[0]+1)]=imgUri
			else:
				print(img_name, "error1")

		return jsonify({ "status": "success", "post": post })
	else:
		abort(500)

@app.route("/explore_feed", methods=["GET"], endpoint="explore_feed" )
@cross_origin()
@login_required
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
