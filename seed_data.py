from beauty import create_app, db
from beauty.models import Product

def populate_beauty_details():
    app = create_app()
    with app.app_context():
        # Fetch all products currently in your database
        products = Product.query.all()
        
        for p in products:
            # EYES CATEGORY
            if p.category.lower() == 'eyes':
                p.full_description = f"Define your gaze with {p.name}. This professional-grade formula offers rich, blendable pigment that stays vibrant from day to night."
                p.benefits = "• 12-Hour Wear\n• Crease-Resistant\n• Intense Pigment Payoff\n• Ophthalmologist Tested"
                p.ingredients = "Mica, Talc, Synthetic Fluorphlogopite, Silica, Magnesium Stearate, Dimethicone, Ethylhexyl Palmitate, Vitamin E."
                p.usage = "Sweep over lids with a brush for a soft wash of color, or apply with fingertips for a bold, metallic finish."

            # LIPS CATEGORY
            elif p.category.lower() == 'lips':
                p.full_description = f"Experience ultimate lip luxury with {p.name}. A moisture-rich formula that delivers high-impact color with a weightless, silk-like feel."
                p.benefits = "• Deeply Hydrating\n• Satin-Smooth Finish\n• Non-Feathering\n• Infused with Natural Oils"
                p.ingredients = "Ricinus Communis Seed Oil, Jojoba Esters, Shea Butter, Candelilla Wax, Hyaluronic Acid, Rosehip Oil."
                p.usage = "Apply directly to lips starting from the center and moving outward. For a blurred effect, tap gently with ring finger."

            # FACE CATEGORY
            elif p.category.lower() == 'face':
                p.full_description = f"Achieve a radiant, second-skin finish with {p.name}. Designed to blur imperfections while allowing your natural glow to shine through."
                p.benefits = "• Buildable Coverage\n• Pore-Blurring Technology\n• Weightless Texture\n• All-Day Breathability"
                p.ingredients = "Aqua, Glycerin, Niacinamide, Squalane, Titanium Dioxide, Aloe Barbadensis Leaf Juice, Green Tea Extract."
                p.usage = "Apply 1-2 pumps to the back of your hand. Blend into skin using a damp beauty sponge or a dense buffing brush."

        # Save all changes to the database
        db.session.commit()
        print("✨ Success: Your products are now filled with luxury details!")

if __name__ == "__main__":
    populate_beauty_details()