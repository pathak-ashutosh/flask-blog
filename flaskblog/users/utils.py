import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flaskblog import mail
from flask_mail import Message

def save_picture(form_picture):
    ''' Scales down and saves a profile picture '''
    random_hex = secrets.token_hex(8)   # to generate random hex string so that filename provided by user doesn't collide with an existing filename
    _, f_ext = os.path.splitext(form_picture.filename)      # returns filename and file extension
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)        # resizing the image because larger images will make the site slow to load
    i = Image.open(form_picture)    # opening the image
    i.thumbnail(output_size)        # setting image to size of output size
    i.save(picture_path)            # saving the scaled down image

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',             # email subject
                    sender = 'norerply@demo.com',
                    recipients = [user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token = token, _external = True)}

If you did not make this request, then simply ignore this email and no changes will be made.
    '''
# _external=True is used for giving the absolute path instead of relative path in the email because link in the email needs to have full dimain
    mail.send(msg)