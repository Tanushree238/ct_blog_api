from app import app, db
from app.models import *
from flask import redirect, render_template, url_for, jsonify, request, flash, session, make_response, abort
from flask_cors import cross_origin
from PIL import Image as pil_img
import base64
from binascii import a2b_base64
from app.decorators import login_required
from sqlalchemy import or_
import math
import os


@app.route("/", methods=["GET", "POST"])
def home():
    return "Hello"


@app.route("/register_user", methods=["POST"], endpoint="register_user")
@cross_origin()
def register_user():
    form = request.json
    user_obj = User(
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
            img.write(data)

    user_obj.image = "{}.{}".format(form["username"], form["image"]["ext"])
    db.session.commit()
    token = user_obj.get_login_token()
    return jsonify({'status': 'success', 'token': token})


@app.route("/edit_profile", methods=["POST"], endpoint="edit_profile")
@cross_origin()
@login_required
def edit_profile():
    form = request.json
    user_obj = User.query.filter_by(id=form["id"]).first()
    if user_obj.username != form["username"]:
        user_obj.username = form["username"]
    if user_obj.name != form["name"]:
        user_obj.name = form["name"]
    if user_obj.email != form["email"]:
        user_obj.email = form["email"]
    if user_obj.contact != form["contact"]:
        user_obj.contact = form["contact"]
    if user_obj.bio != form["bio"]:
        user_obj.bio = form["bio"]
    user_obj.set_password(form["password"])
    if form["image"]["data"]:
        with open("app/static/profile_pic/{}.{}".format(form["username"], form["image"]["ext"]), "wb") as img:
            data = base64.b64decode(form["image"]["data"])
            img.write(data)

    user_obj.image = "{}.{}".format(form["username"], form["image"]["ext"])
    db.session.commit()
    token = user_obj.get_login_token()
    return jsonify({'status': 'success', 'token': token})


@app.route("/validate_login_token", methods=["POST"], endpoint="validate_login_token")
@cross_origin()
def validate_login_token():
    form = request.json
    user = User.verify_login_token(form["token"])
    if user:
        return jsonify({'status': 'valid'})
    else:
        return jsonify({'status': 'invalid'})


@app.route("/login_user", methods=["POST"], endpoint="login_user")
@cross_origin()
def login_user():
    form = request.json
    user = User.query.filter_by(username=form["username"]).first()
    if user and user.check_password(form["password"]):
        token = user.get_login_token()
        return jsonify({'status': 'success', 'msg': '', 'token': token})
    else:
        return jsonify({'status': 'error', 'msg': 'Incorrect Username or Password! Please try again.'})


@app.route("/create_post", methods=["POST"], endpoint="create_post")
@cross_origin()
@login_required
def create_post():
    form = request.json
    # print(form)
    user = User.verify_login_token(request.headers["Authentication"])
    privacy_obj = Privacy.query.filter_by(description=form["privacy"]).first()
    if user:
        post_obj = Post(
            title=form["title"],
            content=form["content"],
            user_id=user.id,
            read_time=math.ceil(len(form["content"].split())/125),
            privacy=privacy_obj.id,
        )
        db.session.add(post_obj)
        db.session.commit()
        category_obj = Category.query.filter_by(name=form["category"]).first()
        post_category = PostCategoryMapper(
            category_id=category_obj.id, post_id=post_obj.id)
        db.session.add(post_category)
        db.session.commit()
        if form["image1"]["data"] and form["image1"]["ext"]:
            with open("app/static/post_img/{}.{}".format(str(post_obj.id)+"_1", form["image1"]["ext"]), "wb") as img:
                data = base64.b64decode(form["image1"]["data"])
                img.write(data)
            postImgObj = PostImage(post_id=post_obj.id, image="{}.{}".format(
                str(post_obj.id)+"_1", form["image1"]["ext"]))
            db.session.add(postImgObj)

        if form["image2"]["data"] and form["image2"]["ext"]:
            with open("app/static/post_img/{}.{}".format(str(post_obj.id)+"_2", form["image2"]["ext"]), "wb") as img:
                data = base64.b64decode(form["image2"]["data"])
                img.write(data)
            postImgObj = PostImage(post_id=post_obj.id, image="{}.{}".format(
                str(post_obj.id)+"_2", form["image2"]["ext"]))
            db.session.add(postImgObj)

        if form["image3"]["data"] and form["image3"]["ext"]:
            with open("app/static/post_img/{}.{}".format(str(post_obj.id)+"_3", form["image3"]["ext"]), "wb") as img:
                data = base64.b64decode(form["image3"]["data"])
                img.write(data)
            postImgObj = PostImage(post_id=post_obj.id, image="{}.{}".format(
                str(post_obj.id)+"_3", form["image3"]["ext"]))
            db.session.add(postImgObj)

        db.session.commit()

        return jsonify({'status': 'success', 'msg': 'Post created successfully!'})
    abort(554)


@app.route("/validate_email", methods=["POST"], endpoint="validate_email")
@cross_origin()
def validate_email():
    form = request.json
    if "email" in form:
        if not User.query.filter_by(email=form["email"]).first():
            return jsonify({"status": True})
        else:
            return jsonify({"status": False, "msg": "This Email is already Exists."})
    abort(500)


@app.route("/validate_username", methods=["POST"], endpoint="validate_username")
@cross_origin()
def validate_username():
    form = request.json
    if "username" in form:
        if not User.query.filter_by(username=form["username"]).first():
            return jsonify({"status": True})
        else:
            return jsonify({"status": False, "msg": "This Username is already Exists."})
    abort(500)


@app.route("/validate_contact", methods=["POST"], endpoint="validate_contact")
@cross_origin()
def validate_contact():
    form = request.json
    if "contact" in form:
        if not User.query.filter_by(contact=form["contact"]).first():
            return jsonify({"status": True})
        else:
            return jsonify({"status": False, "msg": "This Contact is already Exists."})
    abort(500)


@app.route("/follow_user", methods=["POST"], endpoint="follow_user")
@cross_origin()
@login_required
def follow_user():
    form = request.json
    follower = User.verify_login_token(request.headers["Authentication"])
    following = User.query.filter_by(username=form["following"]).first()
    if("status" in form and following):
        follow_obj = Follow.query.filter_by(
            follower_id=follower.id, followed_id=following.id).first()
        if(form["status"]):
            if not follow_obj:
                follow = Follow(
                    follower_id=follower.id,
                    followed_id=following.id
                )
                db.session.add(follow)
                db.session.commit()
        else:
            # print(follow_obj)
            db.session.delete(follow_obj)
            db.session.commit()
        return jsonify({'status': 'success'})
    else:
        abort(500)


# Users followed by User(username)
@app.route("/following_users", methods=["POST"], endpoint="following_users")
@cross_origin()
@login_required
def following_users():
    form = request.json
    user = User.verify_login_token(request.headers["Authentication"])
    following_users = []
    for following_user in user.following.all():
        user = {}
        user["username"] = following_user.following_user_obj.username
        user["name"] = following_user.following_user_obj.name
        following_users.append(user)
    return jsonify({'status': 'success', 'following_users': following_users})

# Users following User(username)


@app.route("/followers", methods=["POST"], endpoint="followers")
@cross_origin()
@login_required
def followers():
    form = request.json
    user = User.verify_login_token(request.headers["Authentication"])
    followers = []
    for follower in user.follower.all():
        user = {}
        user["username"] = follower.following_user_obj.username
        user["name"] = follower.following_user_obj.name
        followers.append(user)
    return jsonify({'status': 'success', 'followers': followers})


@app.route("/is_following", methods=["POST"], endpoint="is_following")
@cross_origin()
@login_required
def is_following():
    form = request.json
    user = User.verify_login_token(request.headers["Authentication"])
    following = User.query.filter_by(username=form["is_following"]).first()
    follow_obj = Follow.query.filter_by(
        follower_id=follower.id, followed_id=following.id).first()
    if follow_obj:
        return jsonify({'is_following': 'True'})
    else:
        return jsonify({'is_following': 'False'})


@app.route("/like_post", methods=["POST"], endpoint="like_post")
@cross_origin()
@login_required
def like_post():
    form = request.json
    user = User.verify_login_token(request.headers["Authentication"])
    post = Post.query.filter_by(id=form["post_id"]).first()
    if(form["status"]):
        if(not PostLike.query.filter_by(user_id=user.id, post_id=post.id).first()):
            post_like_obj = PostLike(
                user_id=user.id,
                post_id=post.id
            )
            db.session.add(post_like_obj)
            db.session.commit()
    else:
        likeObj = PostLike.query.filter_by(
            user_id=user.id, post_id=post.id).first()
        if(likeObj):
            db.session.delete(likeObj)
            db.session.commit()
    return jsonify({'status': 'success', 'msg': '{} liked post {}'.format(user.username, post.title), "likes": post.like.count()})


@app.route("/comment_post", methods=["POST"], endpoint="comment_post")
@cross_origin()
@login_required
def comment_post():
    form = request.json
    user = User.verify_login_token(request.headers["Authentication"])
    post = Post.query.filter_by(id=form["post_id"]).first()
    post_comment_obj = PostComment(
        user_id=user.id,
        post_id=post.id,
        comment=form["comment"]
    )
    db.session.add(post_comment_obj)
    db.session.commit()
    return jsonify({'status': 'success', 'msg': '{} commmented on post {}'.format(user.username, post.title)})


@app.route("/home_feed", methods=["POST"], endpoint="home_feed")
@cross_origin()
@login_required
def home_feed():
    form = request.json
    user = User.verify_login_token(request.headers["Authentication"])
    posts = []

    for my_post in user.post.all():
        post = {}
        post["id"] = my_post.id
        post["title"] = my_post.title
        post["username"] = my_post.post_user_obj.username
        post["content"] = my_post.content
        post["read_time"] = my_post.read_time if my_post.read_time else 0
        post["likes"] = my_post.like.count()
        post["is_liked"] = True if PostLike.query.filter_by(
            post_id=my_post.id, user_id=user.id).first() else False
        post["created_on"] = my_post.created_on
        post["category"] = my_post.category.all()[0].category_obj.name
        if my_post.images.first():
            img_path = "app/static/post_img/{}".format(
                my_post.images.first().image)
            if os.path.isfile(img_path):
                with open(img_path, "rb") as img:
                    imgUri = "data:image/{};base64,".format(my_post.images.first().image.split(
                        ".")[-1]) + str(base64.b64encode(img.read()))[2:][:-1]
                    post["image"] = imgUri
            else:
                print(my_post.images.first().image, "error1")
        else:
            print("error2")

        posts.append(post)

    for follower in user.following.all():
        for follower_post in follower.follower_user_obj.post.all():
            if follower_post.privacy != "Only Me":
                post = {}
                post["id"] = follower_post.id
                post["title"] = follower_post.title
                post["username"] = follower_post.post_user_obj.username
                post["content"] = follower_post.content
                post["read_time"] = follower_post.read_time if follower_post.read_time else 0
                post["is_liked"] = True if PostLike.query.filter_by(
                    post_id=follower_post.id, user_id=user.id).first() else False
                post["likes"] = follower_post.like.count()
                post["created_on"] = follower_post.created_on
                post["category"] = follower_post.category.all()[
                    0].category_obj.name
                if follower_post.images.first():
                    img_path = "app/static/post_img/{}".format(
                        follower_post.images.first().image)
                    if os.path.isfile(img_path):
                        with open(img_path, "rb") as img:
                            imgUri = "data:image/{};base64,".format(follower_post.images.first(
                            ).image.split(".")[-1]) + str(base64.b64encode(img.read()))[2:][:-1]
                            post["image"] = imgUri
                    else:
                        print(follower_post.images.first().image, "error1")
                else:
                    print("error2")

                posts.append(post)
    posts.sort(reverse=True, key=lambda x: x["created_on"])
    return jsonify({'status': 'success', 'posts': posts})


@app.route("/fetch_post_data", methods=["POST"], endpoint="fetch_post_data")
@cross_origin()
@login_required
def fetch_post_data():
    form = request.json
    user = User.verify_login_token(request.headers["Authentication"])
    if "post_id" in form:
        post_obj = Post.query.get(int(form["post_id"]))
        post = {}
        post["id"] = post_obj.id
        post["title"] = post_obj.title
        post["username"] = post_obj.post_user_obj.username
        post["name"] = post_obj.post_user_obj.name
        post["content"] = post_obj.content
        post["read_time"] = post_obj.read_time if post_obj.read_time else 0
        post["is_liked"] = True if PostLike.query.filter_by(
            post_id=post_obj.id, user_id=user.id).first() else False
        post["no_of_likes"] = post_obj.like.count()
        post["is_following"] = True if Follow.query.filter_by(
            follower_id=user.id, followed_id=post_obj.post_user_obj.id).first() else False
        post["show_follow_btn"] = True if post_obj.post_user_obj != user else False
        post["no_of_comments"] = post_obj.comment.count()
        post["created_on"] = post_obj.created_on
        post["category"] = post_obj.category.all()[0].category_obj.name

        if user.image:
            img_path = "app/static/profile_pic/{}".format(
                post_obj.post_user_obj.image)
            if os.path.isfile(img_path):
                with open(img_path, "rb") as img:
                    imgUri = "data:image/{};base64,".format(post_obj.post_user_obj.image.split(
                        ".")[-1]) + str(base64.b64encode(img.read()))[2:][:-1]
                    post["profile_pic"] = imgUri
            else:
                print(user.image, "error1")
        else:
            print("error2")

        for img_obj in enumerate(post_obj.images.limit(3)):
            img_name = img_obj[1].image
            img_path = "app/static/post_img/{}".format(img_name)
            if os.path.isfile(img_path):
                with open(img_path, "rb") as img:
                    imgUri = "data:image/{};base64,".format(img_name.split(
                        ".")[-1]) + str(base64.b64encode(img.read()))[2:][:-1]
                    post["image"+str(img_obj[0]+1)] = imgUri
            else:
                print(img_name, "error1")

        return jsonify({"status": "success", "post": post})
    else:
        abort(500)


@app.route("/explore_feed", methods=["POST"], endpoint="explore_feed")
@cross_origin()
@login_required
def explore_feed():
    form = request.json
    user = User.verify_login_token(request.headers["Authentication"])
    posts = []
    all_posts = Post.query.filter_by(privacy=1).limit(100)
    for valid_post in all_posts:
        if not form or valid_post.category.all()[0].category_obj.name == form["category"]:
            post = {}
            post["id"] = valid_post.id
            post["title"] = valid_post.title
            post["username"] = valid_post.post_user_obj.username
            post["content"] = valid_post.content
            post["read_time"] = valid_post.read_time if valid_post.read_time else 0
            post["is_liked"] = True if PostLike.query.filter_by(
                post_id=valid_post.id, user_id=user.id).first() else False
            post["likes"] = valid_post.like.count()
            post["created_on"] = valid_post.created_on
            post["category"] = valid_post.category.all()[0].category_obj.name
            if valid_post.images.first():
                img_path = "app/static/post_img/{}".format(
                    valid_post.images.first().image)
                if os.path.isfile(img_path):
                    with open(img_path, "rb") as img:
                        imgUri = "data:image/{};base64,".format(valid_post.images.first().image.split(
                            ".")[-1]) + str(base64.b64encode(img.read()))[2:][:-1]
                        post["image"] = imgUri
                else:
                    print(valid_post.images.first().image, "error1")
            else:
                print("error2")
            posts.append(post)
    posts.sort(reverse=True, key=lambda x: (x["likes"], x["created_on"]))
    return jsonify({'status': 'success', 'posts': posts})


@app.route("/search_user", methods=["POST"], endpoint="search_user")
@cross_origin()
@login_required
def search_user():
    form = request.json
    text = form["searchInput"]
    user = User.verify_login_token(request.headers["Authentication"])
    result_users = User.query.filter(or_(User.username.like(
        "%{}%".format(text)), User.name.like("%{}%".format(text)))).all()
    results = []
    for result_user in result_users:
        if result_user != user:
            result = {}
            result["id"] = result_user.id
            result["name"] = result_user.name
            result["username"] = result_user.username

            img_path = "app/static/profile_pic/{}".format(result_user.image)
            if os.path.isfile(img_path):
                with open(img_path, "rb") as img:
                    imgUri = "data:image/{};base64,".format(result_user.image[-1]) + str(
                        base64.b64encode(img.read()))[2:][:-1]
                    result["image"] = imgUri
            result["is_following"] = user.is_following(result_user.id)
            result["show_follow_btn"] = True if result_user != user else False
            results.append(result)
    return jsonify({'status': 'success', 'results': results})


@app.route("/search_by_content", methods=["POST"], endpoint="search_by_content")
@cross_origin()
@login_required
def search_by_content():
    form = request.json
    text = form["searchInput"]
    user = User.verify_login_token(request.headers["Authentication"])
    category_id = Category.query.filter_by(name=form["category_id"]).first().id
    try:
        result_posts = Post.query.filter(
            Post.content.like("%{}%".format(text)), Post.category.any(category_id=category_id)).all()
    except Exception as err:
        print(err)
        result_posts = []

    results = []

    for post_obj in result_posts:
        post = {}
        post["id"] = post_obj.id
        post["title"] = post_obj.title
        post["username"] = post_obj.post_user_obj.username
        post["content"] = post_obj.content
        post["read_time"] = post_obj.read_time if post_obj.read_time else 0
        post["is_liked"] = True if PostLike.query.filter_by(
            post_id=post_obj.id, user_id=user.id).first() else False
        post["likes"] = post_obj.like.count()
        post["created_on"] = post_obj.created_on
        post["category"] = post_obj.category.all()[0].category_obj.name
        if post_obj.images.first():
            img_path = "app/static/post_img/{}".format(
                post_obj.images.first().image)
            if os.path.isfile(img_path):
                with open(img_path, "rb") as img:
                    imgUri = "data:image/{};base64,".format(post_obj.images.first().image.split(
                        ".")[-1]) + str(base64.b64encode(img.read()))[2:][:-1]
                    post["image"] = imgUri
            else:
                print(post_obj.images.first().image, "error1")
        else:
            print("error2")

        results.append(post)

    return jsonify({"status": "success", "posts": results})


@app.route("/user_details", methods=["POST"], endpoint="user_details")
@cross_origin()
@login_required
def user_details():
    form = request.json
    current_user = User.verify_login_token(request.headers["Authentication"])
    details = {}
    if form and "username" in form:
        user = User.query.filter_by(username=form["username"]).first()
        details["id"] = user.id
        details["name"] = user.name
        details["username"] = user.username
        details["email"] = user.email
        details["contact"] = user.contact
        img_path = "app/static/profile_pic/{}".format(user.image)
        image = ""
        if os.path.isfile(img_path):
            with open(img_path, "rb") as img:
                imgUri = "data:image/{};base64,".format(user.image[-1]) + str(
                    base64.b64encode(img.read()))[2:][:-1]
                image = imgUri
        details["is_following"] = current_user.is_following(user.id)
        details["show_follow_btn"] = True
        details["show_edit_btn"] = False
        details["postCount"] = user.post.count()
        details["followerCount"] = user.follower.count()
        details["followingCount"] = user.following.count()
        details["bio"] = user.bio
        posts = []
        for my_post in user.post.all():
            post = {}
            post["id"] = my_post.id
            post["title"] = my_post.title
            post["username"] = my_post.post_user_obj.username
            post["content"] = my_post.content
            post["read_time"] = my_post.read_time if my_post.read_time else 0
            post["likes"] = my_post.like.count()
            post["is_liked"] = True if PostLike.query.filter_by(
                post_id=my_post.id, user_id=user.id).first() else False
            post["created_on"] = my_post.created_on
            post["category"] = my_post.category.all()[0].category_obj.name
            post["privacy"] = my_post.privacy_obj.description
            if my_post.images.first():
                img_path = "app/static/post_img/{}".format(
                    my_post.images.first().image)
                if os.path.isfile(img_path):
                    with open(img_path, "rb") as img:
                        imgUri = "data:image/{};base64,".format(my_post.images.first().image.split(
                            ".")[-1]) + str(base64.b64encode(img.read()))[2:][:-1]
                        post["image"] = imgUri
                else:
                    print(my_post.images.first().image, "error1")
            else:
                print("error2")

            posts.append(post)

        posts.sort(reverse=True, key=lambda x: x["created_on"])
    else:
        details["id"] = current_user.id
        details["name"] = current_user.name
        details["username"] = current_user.username
        details["email"] = current_user.email
        details["contact"] = current_user.contact
        img_path = "app/static/profile_pic/{}".format(current_user.image)
        image = ""
        if os.path.isfile(img_path):
            with open(img_path, "rb") as img:
                imgUri = "data:image/{};base64,".format(current_user.image[-1]) + str(
                    base64.b64encode(img.read()))[2:][:-1]
                image = imgUri
        details["is_following"] = False
        details["show_follow_btn"] = False
        details["show_edit_btn"] = True
        details["postCount"] = current_user.post.count()
        details["followerCount"] = current_user.follower.count()
        details["followingCount"] = current_user.following.count()
        details["bio"] = current_user.bio
        posts = []

        for my_post in current_user.post.all():
            post = {}
            post["id"] = my_post.id
            post["title"] = my_post.title
            post["username"] = my_post.post_user_obj.username
            post["content"] = my_post.content
            post["read_time"] = my_post.read_time if my_post.read_time else 0
            post["likes"] = my_post.like.count()
            post["is_liked"] = True if PostLike.query.filter_by(
                post_id=my_post.id, user_id=current_user.id).first() else False
            post["created_on"] = my_post.created_on
            post["category"] = my_post.category.all()[0].category_obj.name
            post["privacy"] = my_post.privacy_obj.description
            if my_post.images.first():
                img_path = "app/static/post_img/{}".format(
                    my_post.images.first().image)
                if os.path.isfile(img_path):
                    with open(img_path, "rb") as img:
                        imgUri = "data:image/{};base64,".format(my_post.images.first().image.split(
                            ".")[-1]) + str(base64.b64encode(img.read()))[2:][:-1]
                        post["image"] = imgUri
                else:
                    print(my_post.images.first().image, "error1")
            else:
                print("error2")

            posts.append(post)

        posts.sort(reverse=True, key=lambda x: x["created_on"])
    return jsonify({'status': 'success', 'details': details, 'image': image, 'posts': posts})


@app.route("/options", methods=["GET"], endpoint="options")
@cross_origin()
@login_required
def options():
    privacy_options = Privacy.query.all()
    privacy = []
    for option in privacy_options:
        privacy_option = {}
        privacy_option["name"] = option.description
        privacy_option["id"] = option.id
        privacy.append(privacy_option)
    category_options = Category.query.all()
    category = []
    for option in category_options:
        category_option = {}
        category_option["name"] = option.name
        category_option["id"] = option.id
        category.append(category_option)
    return jsonify({'status': 'success', "privacy": privacy, 'category': category})


@app.route("/liked_by_users", methods=["POST"], endpoint="liked_by_users")
@cross_origin()
@login_required
def liked_by_users():
    form = request.json
    post_id = form["post_id"]
    user = User.verify_login_token(request.headers["Authentication"])
    result_likes = PostLike.query.filter_by(post_id=post_id).all()
    results = []
    for result_like in result_likes:
        result_user = result_like.like_user_obj
        result = {}
        result["id"] = result_user.id
        result["name"] = result_user.name
        result["username"] = result_user.username
        img_path = "app/static/profile_pic/{}".format(result_user.image)
        if os.path.isfile(img_path):
            with open(img_path, "rb") as img:
                imgUri = "data:image/{};base64,".format(result_user.image[-1]) + str(
                    base64.b64encode(img.read()))[2:][:-1]
                result["image"] = imgUri
        result["is_following"] = user.is_following(result_user.id)
        result["show_follow_btn"] = True if result_user != user else False
        results.append(result)
    return jsonify({'status': 'success', 'results': results})


@app.route("/user_posts", methods=["POST"], endpoint="user_posts")
@cross_origin()
@login_required
def user_posts():
    form = request.json
    user = User.verify_login_token(request.headers["Authentication"])
    posts = []

    for my_post in user.post.all():
        post = {}
        post["id"] = my_post.id
        post["title"] = my_post.title
        post["username"] = my_post.post_user_obj.username
        post["content"] = my_post.content
        post["read_time"] = my_post.read_time if my_post.read_time else 0
        post["likes"] = my_post.like.count()
        post["is_liked"] = True if PostLike.query.filter_by(
            post_id=my_post.id, user_id=user.id).first() else False
        post["created_on"] = my_post.created_on
        post["category"] = my_post.category.all()[0].category_obj.name
        if my_post.images.first():
            img_path = "app/static/post_img/{}".format(
                my_post.images.first().image)
            if os.path.isfile(img_path):
                with open(img_path, "rb") as img:
                    imgUri = "data:image/{};base64,".format(my_post.images.first().image.split(
                        ".")[-1]) + str(base64.b64encode(img.read()))[2:][:-1]
                    post["image"] = imgUri
            else:
                print(my_post.images.first().image, "error1")
        else:
            print("error2")

        posts.append(post)

    posts.sort(reverse=True, key=lambda x: x["created_on"])
    return jsonify({'status': 'success', 'posts': posts})


@app.route("/fetch_comment", methods=["POST"], endpoint="fetch_comment")
@cross_origin()
@login_required
def fetch_comment():
    form = request.json
    post_id = form["post_id"]
    user = User.verify_login_token(request.headers["Authentication"])
    result_comments = PostComment.query.filter_by(
        post_id=post_id).order_by(PostComment.id.desc()).all()
    results = []
    for result_comment in result_comments:
        result_user = result_comment.comment_user_obj
        result = {}
        result["user_id"] = result_user.id
        result["comment_id"] = result_comment.id
        result["comment"] = result_comment.comment
        result["read_only"] = True if user.id != result_comment.user_id else False
        result["created_on"] = result_comment.created_on.strftime(
            "%d %b %Y  %I:%M %p")
        result["name"] = result_user.name
        result["username"] = result_user.username
        img_path = "app/static/profile_pic/{}".format(result_user.image)
        if os.path.isfile(img_path):
            with open(img_path, "rb") as img:
                imgUri = "data:image/{};base64,".format(result_user.image[-1]) + str(
                    base64.b64encode(img.read()))[2:][:-1]
                result["image"] = imgUri

        results.append(result)
    return jsonify({'status': 'success', 'results': results})


@app.route("/edit_comment_post", methods=["POST"], endpoint="edit_comment_post")
@cross_origin()
@login_required
def edit_comment_post():
    form = request.json
    if "comment_id" in form and "comment" in form:
        comment_id = form["comment_id"]
        commentText = form["comment"]
        comment = PostComment.query.get(int(comment_id))
        if comment:
            comment.comment = commentText
            db.session.commit()
            return jsonify({"status": "success"})
    abort(500)


@app.route("/delete_comment_post", methods=["POST"], endpoint="delete_comment_post")
@cross_origin()
@login_required
def delete_comment_post():
    form = request.json
    if "comment_id" in form:
        comment_id = form["comment_id"]
        comment = PostComment.query.get(int(comment_id))
        if comment:
            db.session.delete(comment)
            db.session.commit()
            return jsonify({"status": "success"})
    abort(500)


@app.route("/delete_post", methods=["POST"], endpoint="delete_post")
@cross_origin()
@login_required
def delete_post():
    form = request.json
    if "post_id" in form:
        post_id = form["post_id"]
        post = Post.query.get(int(post_id))
        if post:
            db.session.delete(post)
            db.session.commit()
            return jsonify({"status": "success"})
    abort(500)


@app.route("/edit_post", methods=["POST"], endpoint="edit_post")
@cross_origin()
@login_required
def edit_post():
    form = request.json
    # print(form)
    user = User.verify_login_token(request.headers["Authentication"])
    privacy_obj = Privacy.query.filter_by(description=form["privacy"]).first()
    if user:
        post_obj = Post.query.filter_by(id=form["id"]).first()
        category_obj = Category.query.filter_by(name=form["category"]).first()

        if post_obj.title != form["title"]:
            post_obj.title = form["title"]
        if post_obj.content != form["content"]:
            post_obj.content = form["content"]

        post_category = PostCategoryMapper.query.filter_by(
            post_id=post_obj.id).first()
        if post_category.category_id != category_obj.id:
            db.session.delete(post_category)
            db.session.commit()
            post_category = PostCategoryMapper(
                category_id=category_obj.id, post_id=post_obj.id)
            db.session.add(post_category)
            db.session.commit()
        if form["image1"]["data"] and form["image1"]["ext"]:
            with open("app/static/post_img/{}.{}".format(str(post_obj.id)+"_1", form["image1"]["ext"]), "wb") as img:
                data = base64.b64decode(form["image1"]["data"])
                img.write(data)
            postImgObj = PostImage(post_id=post_obj.id, image="{}.{}".format(
                str(post_obj.id)+"_1", form["image1"]["ext"]))
            db.session.add(postImgObj)

        if form["image2"]["data"] and form["image2"]["ext"]:
            with open("app/static/post_img/{}.{}".format(str(post_obj.id)+"_2", form["image2"]["ext"]), "wb") as img:
                data = base64.b64decode(form["image2"]["data"])
                img.write(data)
            postImgObj = PostImage(post_id=post_obj.id, image="{}.{}".format(
                str(post_obj.id)+"_2", form["image2"]["ext"]))
            db.session.add(postImgObj)

        if form["image3"]["data"] and form["image3"]["ext"]:
            with open("app/static/post_img/{}.{}".format(str(post_obj.id)+"_3", form["image3"]["ext"]), "wb") as img:
                data = base64.b64decode(form["image3"]["data"])
                img.write(data)
            postImgObj = PostImage(post_id=post_obj.id, image="{}.{}".format(
                str(post_obj.id)+"_3", form["image3"]["ext"]))
            db.session.add(postImgObj)

        db.session.commit()

        return jsonify({'status': 'success', 'msg': 'Post edited successfully!'})
    abort(500)
