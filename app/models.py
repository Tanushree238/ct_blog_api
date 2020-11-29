from app import app, db
from datetime import datetime
from time import time
from flask import url_for
import jwt
from time import time
import os
from sqlalchemy import func,text
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
from sqlalchemy.dialects.mysql import LONGTEXT


class User(db.Model):
	id = db.Column( db.Integer, primary_key=True )
	username=db.Column( db.String(50), nullable=False, index=True  )
	name=db.Column( db.String(200), nullable=False )
	email = db.Column( db.String(100), nullable=False, index=True )
	password_hash = db.Column( db.String(128), nullable=False ) 
	contact = db.Column( db.BigInteger, unique=True, nullable=False)
	image=db.Column( db.String(60), nullable=True, index=True )  
	bio=db.Column( LONGTEXT , nullable=True )
	following = db.relationship( 'Follow', backref="following_user_obj", lazy="dynamic", foreign_keys="Follow.follower_id" )
	follower = db.relationship( 'Follow', backref="follower_user_obj", lazy="dynamic", foreign_keys="Follow.followed_id" )
	post = db.relationship( 'Post', backref="post_user_obj", lazy="dynamic" )

	created_on = db.Column( db.DateTime, default=datetime.now )
	updated_on = db.Column( db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP') )

	def set_password( self,password ):
		self.password_hash = generate_password_hash(password)

	def check_password( self,password ):
		return check_password_hash( self.password_hash, password ) 

	def get_login_token(self,expire_in=720):
		return jwt.encode( {'username':self.username, 'exp':time()+expire_in }, app.config['SECRET_KEY'], algorithm='HS256' ).decode('utf-8')

	@staticmethod
	def verify_login_token(token):
		try: 
			username = jwt.decode( token, app.config['SECRET_KEY'],algorithm=['HS256'] )['username']
		except:
			return None
 
		user = User.query.filter_by(username=username).first() 
		if user:
			return user
		else:
			return None	


class Follow(db.Model):
	id = db.Column( db.Integer, primary_key=True )
	follower_id=db.Column( db.Integer, db.ForeignKey('user.id') )
	followed_id=db.Column( db.Integer, db.ForeignKey('user.id') )
	created_on = db.Column( db.DateTime, default=datetime.now )
	updated_on = db.Column( db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP') )


class Category(db.Model):
	id = db.Column( db.Integer, primary_key=True )
	name=db.Column( db.String(200), nullable=False )
	created_on = db.Column( db.DateTime, default=datetime.now )
	updated_on = db.Column( db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP') )


class Post(db.Model):
	id = db.Column( db.Integer, primary_key=True )
	title=db.Column( db.String(255), nullable=False, index=True  )
	content=db.Column( LONGTEXT , nullable=False )
	privacy=db.Column( db.String(50), nullable=False, index=True  )
	user_id=db.Column( db.Integer, db.ForeignKey('user.id') )
	like = db.relationship( 'PostLike', backref="post_obj", lazy="dynamic" )
	comment = db.relationship( 'PostComment', backref="post_obj", lazy="dynamic" )
	created_on = db.Column( db.DateTime, default=datetime.now )
	updated_on = db.Column( db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP') )


class PostCategoryMapper(db.Model):
	id = db.Column( db.Integer, primary_key=True )
	post_id=db.Column( db.Integer, db.ForeignKey('post.id') )
	category_id=db.Column( db.Integer, db.ForeignKey('category.id') )
	created_on = db.Column( db.DateTime, default=datetime.now )
	updated_on = db.Column( db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP') )


class PostImage(db.Model):
	id = db.Column( db.Integer, primary_key=True )
	post_id=db.Column( db.Integer, db.ForeignKey('post.id') )
	image=db.Column( db.String(60), nullable=True, index=True ) 
	created_on = db.Column( db.DateTime, default=datetime.now )
	updated_on = db.Column( db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP') )


class PostLike(db.Model):
	id = db.Column( db.Integer, primary_key=True )
	post_id=db.Column( db.Integer, db.ForeignKey('post.id') )
	user_id=db.Column( db.Integer, db.ForeignKey('user.id') )
	created_on = db.Column( db.DateTime, default=datetime.now )
	updated_on = db.Column( db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP') )


class PostComment(db.Model):
	id = db.Column( db.Integer, primary_key=True )
	post_id=db.Column( db.Integer, db.ForeignKey('post.id') )
	user_id=db.Column( db.Integer, db.ForeignKey('user.id') )
	comment=db.Column( LONGTEXT , nullable=True )
	created_on = db.Column( db.DateTime, default=datetime.now )
	updated_on = db.Column( db.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP') )