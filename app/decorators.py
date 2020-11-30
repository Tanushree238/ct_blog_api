from flask import request, abort, render_template, redirect
from app.models import User

def login_required(func):
    def check(*args,**kwargs):
        if "Authentication" in request.headers:
            if User.verify_login_token( request.headers["Authentication"] ):
                return func(*args,**kwargs)
            else:
                abort(500)
        else:
            abort(500)

    return check