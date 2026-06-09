from beauty import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# ------------ THE USER MODEL.............
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False) # Not unique
    last_name = db.Column(db.String(50), nullable=False)  # Not unique
    email = db.Column(db.String(120), unique=True, nullable=False) # Unique for login
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # the new ROLE column
    # default is 'user' but options can be admin, manager etc
    role = db.Column(db.String(20), nullable=False, default='user')

    # relationship to connect the user to cart
    cart = db.relationship('Cart', backref='owner', uselist=False) # uselist=False makes it a 1-to-1 relationship

    # The Bridge: This links the User to their Wishlist entries
    wishlist_items = db.relationship('Wishlist', backref='owner', lazy=True, cascade="all, delete-orphan")

    # relationship to the Address model
    addresses = db.relationship('Address', backref='owner', lazy=True, cascade="all, delete-orphan")

    # relationship to the review model
    reviews = db.relationship('Review', backref='author', lazy=True)


    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"
    

    @property
    def wishlist_product_ids(self):
        """Returns a list of product IDs in the user's wishlist for easy checking"""
        return [item.product_id for item in self.wishlist_items]

    def __repr__(self):
        return f"User('{self.full_name}', '{self.email}')"



# ------------ THE PRODUCT MODEL.............
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    # This will hold 'Best Seller', 'New', or 'Normal'
    description = db.Column(db.String(50), nullable=False, default='Normal')
    
    # This will hold 'Face', 'Lips', or 'Eyes'
    category = db.Column(db.String(50), nullable=False)
    
    # Filename of the image (e.g., 'mascara.jpg')
    image_file = db.Column(db.String(100), nullable=False)
    
    # Inventory management
    stock_count = db.Column(db.Integer, nullable=False, default=0)

    # --- NEW FIELDS FOR BEAUTY GLOW ---
    full_description = db.Column(db.Text, nullable = True)
    ingredients = db.Column(db.Text, nullable=True)
    benefits = db.Column(db.Text, nullable=True)
    usage = db.Column(db.Text, nullable=True)

    # The Archive Logic
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # relationship to the review model
    reviews = db.relationship('Review', backref='product_review', lazy=True, cascade="all, delete-orphan")


    # helper function to calculate average rating
    def get_average_rating(self):
        if not self.reviews:
            return 0
        total = sum(review.rating for review in self.reviews)
        return round(total / len(self.reviews), 1)
    

    def __repr__(self):
        return f"Product('{self.name}', Price: '{self.price}', Category: '{self.category}', Active: {self.is_active})"
    


# ------------ THE CART MODEL.............
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # relationship to get all items from cart easily
    items = db.relationship('CartItem', backref = 'cart', lazy = True, cascade="all, delete-orphan")

    @property
    def total_price(self):
        return sum(item.product.price * item.quantity for item in self.items)

    def __repr__(self):
        return f"Cart(User ID: {self.user_id})"


# ------------ THE CART ITEM MODEL.............
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    # relationship to get product details
    product = db.relationship('Product')

    def __repr__(self):
        return f"CartItem(Product ID: {self.product_id}, Quantity: {self.quantity})"
    



# ------------ THE WISHLIST MODEL.............
class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship: allows us to do 'wish_item.product.name'
    product = db.relationship('Product', backref='wishlisted_by')

    def __repr__(self):
        return f"Wishlist('User:{self.user_id}', 'Product:{self.product_id}')"




# ------------ THE ADDRESS MODEL.............
class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False) # In case they ship to someone else
    address_line_1 = db.Column(db.String(150), nullable=False)
    address_line_2 = db.Column(db.String(150))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), default="Nigeria")
    phone_number = db.Column(db.String(20), nullable=False)
    is_default = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Address('{self.address_line_1}', '{self.city}')"




# ------------ THE REVIEW MODEL.............
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)  # We will constrain this 1-5
    comment = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __repr__(self):
        return f"Review(Rating: {self.rating}, User: {self.user_id}, Product: {self.product_id})"