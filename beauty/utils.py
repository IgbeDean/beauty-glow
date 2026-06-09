import os
import secrets
from PIL import Image
from flask import current_app, abort
from functools import wraps
from flask_login import current_user

def save_picture(form_picture):
    # 1. Create a random hex name to prevent filename collisions
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    
    # 2. Define the path (make sure static/images/profile_pics exists)
    picture_path = os.path.join(current_app.root_path, 'static/images/user_profile_pics', picture_fn)

    # 3. Resize the image (Editorial profile pics don't need to be 4K)
    output_size = (300, 300)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    
    # 4. Save it to the filesystem
    i.save(picture_path)

    return picture_fn



def save_product_picture(form_picture):
    # Create a random hex name to avoid filename collisions
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    
    # Define the path to the static folder
    # Ensure the folder 'static/product_pics' exists in your project!
    picture_path = os.path.join(current_app.root_path, 'static/images/product_images', picture_fn)

    # Resize the image
    # We use a 1000px max width/height to keep it sharp but lightweight
    output_size = (1000, 1000)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    
    # Save the processed image
    i.save(picture_path)

    return picture_fn



# this is for the special admin login
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in AND has the admin role
        if not current_user.is_authenticated or current_user.role != 'admin':
            # 403 Forbidden is the standard for "I know who you are, but you're not allowed here"
            abort(403)
        return f(*args, **kwargs)
    return decorated_function