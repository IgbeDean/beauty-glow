from flask import Blueprint, render_template, url_for, flash, redirect, request
from beauty import db
from beauty.utils import admin_required
from beauty.models import User, Product, Review
from beauty.forms import ProductForm
from beauty.utils import save_product_picture



admin = Blueprint('admin', __name__, url_prefix='/admin')


# THE ADMIN DASHBOARD ROUTE
@admin.route('/dashboard')
@admin_required
def dashboard():

    # Real-time metrics
    stats = {
        'users': User.query.count(),
        'products': Product.query.count(),
        'reviews': Review.query.count()
    }
    
    # Let's also grab the 5 most recent reviews to show on the main feed
    recent_reviews = Review.query.order_by(Review.date_posted.desc()).limit(5).all()


    return render_template(
        'admin/dashboard.html',
        stats = stats,
        recent_reviews = recent_reviews
    )




# The ADMIN Product Management Route
@admin.route('/products')
@admin_required
def manage_product():
    # Fetch all products, sorted by the most recently added
    all_products = Product.query.order_by(Product.date_added.desc()).all()

    # We can split them in the template or here
    active_products = [p for p in all_products if p.is_active]
    archived_products = [p for p in all_products if not p.is_active]
    
    return render_template(
        'admin/products.html', 
        active_products=active_products, 
        archived_count=len(archived_products)
    )




# the ADMIN add product route
@admin.route('/product/new', methods = ['GET', 'POST'])
@admin_required
def add_product():
    form = ProductForm()

    if form.validate_on_submit():
        # 1. Handle the image
        if form.image.data:
            picture_file = save_product_picture(form.image.data)
        else:
            picture_file = 'default_product.jpg'
        

        # 2. Map form data to Product Model
        new_product = Product(
            name=form.name.data,
            price=form.price.data,
            description=form.description.data, # This is the Tag: New/Best Seller
            category=form.category.data,
            stock_count=form.stock_count.data,
            image_file=picture_file,
            full_description=form.full_description.data,
            ingredients=form.ingredients.data,
            benefits=form.benefits.data,
            usage=form.usage.data
        )


        # 3. Commit to Database
        try:
            db.session.add(new_product)
            db.session.commit()
            flash(f'"{new_product.name}" has been successfully added to the collection.', 'success')
            return redirect(url_for('admin.manage_product'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while saving the product. Please try again.', 'danger')
            print(f"Error: {e}") # For your terminal debugging


    return render_template(
        'admin/add_product.html',
        form = form
    )








# ------ The ADMIN edit a product route -----------
@admin.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    # Fetch the product or return 404 if it doesn't exist
    product = Product.query.get_or_404(product_id)
    form = ProductForm()

    if form.validate_on_submit():
        # Update the Image ONLY if a new one was uploaded
        if form.image.data:
            product.image_file = save_product_picture(form.image.data)
        
        # Update text fields from the form
        product.name = form.name.data
        product.price = form.price.data
        product.stock_count = form.stock_count.data
        product.category = form.category.data
        product.description = form.description.data # The 'New/Best Seller' tag
        product.full_description = form.full_description.data
        product.ingredients = form.ingredients.data
        product.benefits = form.benefits.data
        product.usage = form.usage.data
        
        db.session.commit()
        flash(f'Changes to "{product.name}" have been saved.', 'success')
        return redirect(url_for('admin.manage_product'))

    # This part fills the form with current DB data when the page loads
    elif request.method == 'GET':
        form.name.data = product.name
        form.price.data = product.price
        form.stock_count.data = product.stock_count
        form.category.data = product.category
        form.description.data = product.description
        form.full_description.data = product.full_description
        form.ingredients.data = product.ingredients
        form.benefits.data = product.benefits
        form.usage.data = product.usage

    # We reuse the add_product template but change the title
    return render_template(
        'admin/add_product.html', 
        title='Edit Product', 
        form=form, 
        product=product
    )






# ------ The ADMIN Archive a product route -----------
@admin.route('/product/<int:product_id>/archive', methods=['POST'])
@admin_required
def archive_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = False # The "Soft Delete"
    db.session.commit()
    
    flash(f'"{product.name}" has been moved to the archive.', 'warning')
    return redirect(url_for('admin.manage_product'))




# ------ The ADMIN restore an archive product route -----------
@admin.route('/product/<int:product_id>/restore', methods=['POST'])
@admin_required
def restore_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = True
    db.session.commit()
    flash(f'"{product.name}" has been restored to the main gallery.', 'success')
    return redirect(url_for('admin.archived_products'))




# ------ The ADMIN view archived products route -----------
@admin.route('/products/archived')
@admin_required
def archived_products():
    # Fetch only products that are NOT active
    products = Product.query.filter_by(is_active=False).order_by(Product.date_added.desc()).all()
    return render_template(
        'admin/archived_products.html', 
        products=products
    )