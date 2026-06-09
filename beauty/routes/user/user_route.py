import os
from beauty.utils import save_picture
from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify, current_app, abort
from flask_login import login_required, current_user
from beauty.models import Product, Cart, CartItem, Address
from beauty import db
from beauty.forms import UpdateAccountForm, AddressForm

user = Blueprint('user', __name__)


# User add item to cart route
@user.route('/cart/add/<int:product_id>', methods = ['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)

    #1.  check if the user already has a cart, else create one
    user_cart = Cart.query.filter_by(user_id = current_user.id).first()
    if not user_cart:
        user_cart = Cart(user_id = current_user.id)
        db.session.add(user_cart)
        db.session.commit()
    
    # 2. check if the product is already in the user cart
    item = CartItem.query.filter_by(cart_id = user_cart.id, product_id = product.id).first()

    if item:
        item.quantity += 1
    else:
        item = CartItem(cart_id = user_cart.id, product_id = product.id, quantity = 1)
        db.session.add(item)
    
    #3. save everything to the database
    db.session.commit()

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.accept_json

    if not is_ajax:
        # Clear existing messages from the session queue before adding a new one
        # This prevents the "Double Flash" if the session hasn't cleared yet
        from flask import get_flashed_messages
        get_flashed_messages() 

        flash(f'{product.name} added to your bag!', 'success')

        # If adding from profile, go back to profile specifically
        if 'profile' in request.referrer:
             return redirect(url_for('user.profile'))
        return redirect(request.referrer or url_for('main.shop'))

    #4. Calculate values for the magic update
    total = sum(i.product.price * i.quantity for i in user_cart.items)
    count = sum(i.quantity for i in user_cart.items)

    return jsonify({
        "status": "success",
        "message": f"{product.name} added to bag!",
        "cart_html": render_template('includes/_cart_items.html', items=user_cart.items),
        "total": f"${total:,.2f}",
        "count": count
    })



# USER REMOVE CART ITEMS ROUTE
@user.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    user_cart = item.cart # Get the cart before we delete the item

    # Security check
    if user_cart.user_id != current_user.id:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    # Delete the item
    db.session.delete(item)
    db.session.commit()

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.accept_json

    if not is_ajax:
        # Only flash if it's a traditional page reload
        flash(f'Item removed from your bag!', 'success')
        return redirect(request.referrer or url_for('main.shop'))

    # Recalculate values for the UI update
    total = sum(i.product.price * i.quantity for i in user_cart.items)
    count = sum(i.quantity for i in user_cart.items)

    return jsonify({
        "status": "success",
        "message": "Item removed from your bag.",
        "cart_html": render_template('includes/_cart_items.html', items=user_cart.items),
        "total": f"${total:,.2f}",
        "count": count
    })




# GET THE USER'S CART
@user.route('/cart')
@login_required
def cart_page():
    user_cart = Cart.query.filter_by(user_id = current_user.id).first()

    return render_template(
        'user/cart_page.html',
        cart = user_cart,
        title = 'Your Shopping Bag'
    )



# ENABLE UPDATE QUANTITY IN USER CART
@user.route('/cart/update_quantity/<int:item_id>/<string:action>', methods=['POST'])
@login_required
def update_quantity(item_id, action):
    item = CartItem.query.get_or_404(item_id)

    if action == "increment":
        item.quantity += 1
    elif action == "decrement" and item.quantity > 1:
        item.quantity -= 1
    
    db.session.commit()

    # Calculate new values for the UI
    total = sum(i.product.price * i.quantity for i in item.cart.items)
    item_subtotal = item.product.price * item.quantity
    count = sum(i.quantity for i in item.cart.items)

    return jsonify({
        "status": "success",
        "new_quantity": item.quantity,
        "item_subtotal": f"${item_subtotal:,.2f}",
        "total": f"${total:,.2f}",
        "count": count,
        "cart_html": render_template('includes/_cart_items.html', items=item.cart.items)
    })





# --------------User Profile Page----------------
@user.route('/profile', methods = ['GET', 'POST'])
@login_required
def profile():

    # THIS IS FOR THE USER ACCOUNT
    form = UpdateAccountForm()

    if form.validate_on_submit():
        # handle picture upload
        if form.picture.data:
            # delete the old picture if it is not the default one
            if current_user.image_file != 'default.jpg':
                old_pic_path = os.path.join(current_app.root_path, 'static/images/user_profile_pics', current_user.image_file)
                if os.path.exists(old_pic_path):
                    try:
                        os.remove(old_pic_path)
                    except OSError:
                        pass
            
            # save the new picture using out utility.py
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        
        # update user detail
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data

        db.session.commit()

        flash('Your profile has been elegantly updated.', 'success')
        return redirect(url_for('user.profile'))
    
    # populate the form with current data on page load
    elif request.method == "GET":
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email



    # THIS IS FOR THE USER WISHLIST
    wishlist_items = current_user.wishlist_items


    # this is for user address
    address_form = AddressForm()

    if address_form.validate_on_submit():
        # If the user marked this as default, unset all their other defaults first
        if address_form.is_default.data:
            Address.query.filter_by(user_id=current_user.id).update({Address.is_default: False})

        new_address = Address(
            full_name=address_form.full_name.data,
            address_line_1=address_form.address_line_1.data,
            address_line_2=address_form.address_line_2.data,
            city=address_form.city.data,
            state=address_form.state.data,
            postal_code=address_form.postal_code.data,
            phone_number=address_form.phone_number.data,
            is_default=address_form.is_default.data,
            user_id=current_user.id
        )
        db.session.add(new_address)
        db.session.commit()
        flash('New address saved!', 'success')
        return redirect(url_for('user.profile'))
    
    # Fetch all saved addresses to display in the grid
    addresses = Address.query.filter_by(user_id=current_user.id).order_by(Address.is_default.desc()).all()


    return render_template(
        "user/profile.html",
        title = 'Profile',
        form = form,
        wishlist_items = wishlist_items,
        address_form=address_form, 
        addresses=addresses
    )



@user.route("/address/delete/<int:address_id>", methods=['POST'])
@login_required
def delete_address(address_id):
    address = Address.query.get_or_404(address_id)
    # Security check: ensure the address belongs to the current user
    if address.user_id != current_user.id:
        abort(403)
    db.session.delete(address)
    db.session.commit()
    flash('Address removed.', 'success')
    return redirect(url_for('user.profile'))