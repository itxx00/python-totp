import qrcode
import pyotp
import os
from StringIO import StringIO
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect

from user import User


#@app.route('/qr/<email>')
def qr(request,email):
    """
    Return a QR code for the secret key associated with the given email
    address. The QR code is returned as file with MIME type image/png.
    """
    u = User.get_user(email)
    if u is None:
        return ''
    t = pyotp.TOTP(u.key)
    q = qrcode.make(t.provisioning_uri(email))
    img = StringIO()
    q.save(img)
    img.seek(0)
    return HttpResponse(img, mimetype="image/png")


#@app.route('/code/<email>')
def code(request,email):
    """
    Returns the one-time password associated with the given user for the
    current time window. Returns empty string if user is not found.
    """
    u = User.get_user(email)
    if u is None:
        return ''
    t = pyotp.TOTP(u.key)
    return HttpResponse(str(t.now()))


#@app.route('/user/<email>')
def user(request,email):
    """User view page."""
    u = User.get_user(email)
    if u is None:
        return HttpResponseRedirect('/totp/')
    return render_to_response('view.html', {'user':u})


#@app.route('/new', methods=['GET', 'POST'])
def new(request):
    """New user form."""
    if request.method == 'POST':
        u = User(request.POST['email'])
        if u.save():
            return render_to_response('totp/created.html', {'user':u})
        else:
            return HttpResponse('Invalid email or user already exists.')
    else:
        return render_to_response('new.html')


#@app.route('/login', methods=['GET', 'POST'])
def login(request):
    """Login form."""
    if request.method == 'POST':
        u = User.get_user(request.POST['email'])
        if u is None:
            return HttpResponse('Invalid email address.', 'danger')
        else:
            otp = request.POST['otp']
            if u.authenticate(otp):
                return render_to_response('view.html', {'user':u})
            else:
                return HttpResponse('Invalid one-time password!', 'danger')
    else:
        return render_to_response('login.html')


#@app.route('/')
def main(request):
    return render_to_response('index.html')
