from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.sql import func
from beauty.models import Product, Wishlist, Review
from beauty import db
from beauty.forms import ReviewForm

main = Blueprint('main', __name__)

# HOME ROUTE
@main.route('/')
def home():
    # fetch products with description "best seller"
    bestsellers = Product.query.filter_by(description = 'best seller').limit(5).all()

    trending = Product.query.order_by(func.random()).limit(5).all()

    return render_template(
        'main/home.html',
        title = 'Home',
        bestsellers = bestsellers,
        trending = trending
    )



# SHOPPING ROUTE
@main.route("/shop/<string:category_name>")
@main.route("/shop")
def shop(category_name=None):
    # 1. Start with a base query that ONLY includes active products
    query = Product.query.filter_by(is_active=True)
    
    # 2. Apply Category/Tag Filtering
    if category_name == "new":
        query = query.filter(Product.description.contains('new'))
        title = "New Arrivals"
    elif category_name == "best-sellers":
        query = query.filter(Product.description.contains('best seller'))
        title = "Best Sellers"
    elif category_name:
        query = query.filter_by(category=category_name)
        title = category_name.capitalize()
    else:
        title = "All Products"

    # 3. Get the sort argument from the URL
    sort_by = request.args.get('sort', 'recommended')
    
    # 4. Apply Sorting to the already filtered query
    if sort_by == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Product.price.desc())
    else:
        # Default 'Recommended' sort
        query = query.order_by(Product.id.desc())

    # 5. Execute the final filtered and sorted query
    products = query.all()
        
    return render_template(
        'main/shop.html', 
        products=products, 
        title=title, 
        current_cat=category_name
    )




# VIEW EACH PRODUCT ROUTE
@main.route('/product/<int:product_id>', methods = ['GET', 'POST'])
def product_detail(product_id):
    # fetch product by id and throw a 404 error if not exist
    product = Product.query.get_or_404(product_id)

    # find the next product in the same category
    next_product = Product.query.filter(Product.category == product.category, Product.id > product.id).order_by(Product.id.asc()).first()

    # find the previous product in the same category
    prev_product = Product.query.filter(Product.category == product.category, Product.id < product.id).order_by(Product.id.desc()).first()

    # fetch up to 5 related products from the same category
    related_products = Product.query.filter(Product.category == product.category, Product.id != product.id).limit(5).all()


    # --------- Working on the reviews sections -----------
    form = ReviewForm()

    if form.validate_on_submit():
        if current_user.is_authenticated:
            # create the review object
            new_review = Review(
                rating = form.rating.data,
                comment = form.comment.data,
                user_id = current_user.id,
                product_id = product.id
            )

            db.session.add(new_review)
            db.session.commit()
            flash('Thank you! Your review has been posted.', 'success')
            return redirect(url_for('main.product_detail', product_id = product.id))
        else:
            flash('You must be logged in to leave a review.', 'danger')
            return redirect(url_for('auth.login'))
    
    # fetch review to display them on page
    reviews = Review.query.filter_by(product_id = product.id).order_by(Review.date_posted.desc()).all()

    
    return render_template( 
        'main/product_detail.html',
        title = product.name,
        product = product,
        related_products = related_products,
        next_product = next_product,
        prev_product = prev_product,
        form = form,
        reviews = reviews
    )




# ENABLE PRODUCT ADDED TO WISHLIST BY USER
@main.route('/wishlist/toggle/<int:product_id>', methods = ['POST'])
@login_required
def toggle_wishlist(product_id):
    # check if the product is already in the wishlist for this user
    wish_item = Wishlist.query.filter_by(user_id = current_user.id, product_id = product_id).first()

    if wish_item:
        db.session.delete(wish_item)
        db.session.commit()
        return jsonify({"status": "removed", "icon": "♡"})
    else:
        new_wish = Wishlist(user_id = current_user.id, product_id = product_id)
        db.session.add(new_wish)
        db.session.commit()
        return jsonify({"status": "added", "icon": "♥"})