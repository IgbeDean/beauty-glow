from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from beauty.models import User
from flask_login import current_user
from beauty.models import User


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Join the Glow')

    # validation to ensure email is unique
    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()

        if user:
            raise ValidationError('That email is already registered. Please re-login.')



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me') # Keeps the user logged in
    submit = SubmitField('Log In')




class UpdateAccountForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])

    picture = FileField("Update Profile Picture", validators=[FileAllowed(['jpg', 'png', 'jpeg', 'webp'])])
    submit = SubmitField('Save Changes')

    # Custom validator to ensure user doesn't take someone else's email
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email = email.data).first()
            
            if user:
                raise ValidationError('That email is already taken. Please choose a different one.')




class AddressForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    address_line_1 = StringField('Address Line 1', validators=[DataRequired()])
    address_line_2 = StringField('Address Line 2 (Optional)')
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State/Province', validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    is_default = BooleanField('Set as default address')
    submit = SubmitField('Save Address')




class ReviewForm(FlaskForm):
    # The first value in the tuple is what goes to the DB, the second is what the user sees
    rating = SelectField(
        'How would you rate it?',
        choices=[
            (5, '5 - Excellent'),
            (4, '4 - Very Good'),
            (3, '3 - Average'),
            (4, '2 - Poor'),
            (4, '1 - Terrible')
        ],
        coerce=int,
        validators=[DataRequired()]
    )

    comment = TextAreaField(
        'Your thoughts',
        validators=[
            DataRequired(),
            Length(min=5, max=500, message='Please keep your review between 5 and 500 characters.')
        ]
    )

    submit = SubmitField('Post Review')



class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    stock_count = IntegerField('Stock Quantity', validators=[DataRequired(), NumberRange(min=0)])
    
    # SelectFields ensure data consistency
    category = SelectField('Category', choices=[('face', 'face'), ('lips', 'lips'), ('eyes', 'eyes')], validators=[DataRequired()])
    description = SelectField('Product Tag', choices=[('normal', 'normal'), ('new', 'new'), ('best seller', 'best seller')])
    
    # Detailed Beauty Fields
    full_description = TextAreaField('Detailed Description')
    ingredients = TextAreaField('Ingredients')
    benefits = TextAreaField('Key Benefits')
    usage = TextAreaField('How to Use')
    
    image = FileField('Product Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update Catalog')