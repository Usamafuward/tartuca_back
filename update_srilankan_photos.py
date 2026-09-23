import sys
import os

# Add root directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import MenuItem, Category, SpecialOffer, GalleryImage

def update_photos():
    db = SessionLocal()
    print("=== Updating Sri Lankan Restaurant & Food Photos in Database ===")

    # Photo URL mapping
    PHOTOS = {
        'chicken_kottu': 'https://upload.wikimedia.org/wikipedia/commons/a/a3/Chicken_Kottu.jpg',
        'seafood_kottu': 'https://upload.wikimedia.org/wikipedia/commons/1/15/Kottu_Roti.jpg',
        'egg_hopper': 'https://upload.wikimedia.org/wikipedia/commons/0/00/Appam_with_egg.jpg',
        'plain_hopper': 'https://upload.wikimedia.org/wikipedia/commons/e/eb/Appam_by_Connie_Ma.jpg',
        'hbc': 'https://upload.wikimedia.org/wikipedia/commons/6/6d/Hot_Butter_Cuttlefish.jpg',
        'crab_curry': 'https://upload.wikimedia.org/wikipedia/commons/f/f9/Colombo_restaurant_visit_to_enjoy_crab_curry_-_Oct_2022.jpg',
        'pol_sambol': 'https://upload.wikimedia.org/wikipedia/commons/e/e8/Pol_Sambol.jpg',
        'watalappan': 'https://upload.wikimedia.org/wikipedia/commons/8/81/Watalappan-Sri_Lanka.jpg',
        'dhal': 'https://upload.wikimedia.org/wikipedia/commons/d/d3/Parippu_Curry.jpg',
        'curd_treacle': 'https://upload.wikimedia.org/wikipedia/commons/c/c7/Curd_%26_treacle-Sri_Lanka.jpg',
        'king_coconut': 'https://upload.wikimedia.org/wikipedia/commons/a/ad/King_Coconuts.jpg',
        'chicken_curry': 'https://upload.wikimedia.org/wikipedia/commons/0/07/Sri_Lankan_Chicken_Curry.jpg',
        'rice_and_curry': 'https://upload.wikimedia.org/wikipedia/commons/6/6f/Sri_Lankan_Rice_and_Curry.jpg',
        'fish_cutlets': 'https://upload.wikimedia.org/wikipedia/commons/7/76/Sri-lankan-snacks.jpg',
        'fish_curry': 'https://upload.wikimedia.org/wikipedia/commons/0/0d/Srilankan_fish_curry.JPG',
        'pork_curry': 'https://upload.wikimedia.org/wikipedia/commons/6/63/Sri_Lankan_Pork_Curry_and_Scotch_Eggs-_Mshomebakedgoodies%2C_Kolkata_-_West_Bengal_-_DSC021.jpg',
        'jackfruit': 'https://upload.wikimedia.org/wikipedia/commons/8/83/Jackfruit_curry%2C_Kerala.jpg',
        'biryani': 'https://upload.wikimedia.org/wikipedia/commons/2/23/Biryani_in_Nuwara_Eliya.jpg',
        'restaurant_meal': 'https://upload.wikimedia.org/wikipedia/commons/6/64/Sri_Lankan_meal_in_restaurant_style.jpg'
    }

    # 1. Update Menu Items
    menu_updates_count = 0
    menu_items = db.query(MenuItem).all()
    for item in menu_items:
        name_lower = item.name.lower()
        new_url = None
        if 'kottu' in name_lower and 'seafood' in name_lower:
            new_url = PHOTOS['seafood_kottu']
        elif 'kottu' in name_lower:
            new_url = PHOTOS['chicken_kottu']
        elif 'hopper' in name_lower:
            new_url = PHOTOS['egg_hopper']
        elif 'hot butter cuttlefish' in name_lower or 'hbc' in name_lower:
            new_url = PHOTOS['hbc']
        elif 'crab curry' in name_lower:
            new_url = PHOTOS['crab_curry']
        elif 'sambol' in name_lower or 'gotu kola' in name_lower:
            new_url = PHOTOS['pol_sambol']
        elif 'watalappan' in name_lower:
            new_url = PHOTOS['watalappan']
        elif 'curd & kithul' in name_lower:
            new_url = PHOTOS['curd_treacle']
        elif 'king coconut' in name_lower:
            new_url = PHOTOS['king_coconut']
        elif 'dhal' in name_lower or 'red lentil' in name_lower:
            new_url = PHOTOS['dhal']
        elif 'fish cutlets' in name_lower:
            new_url = PHOTOS['fish_cutlets']
        elif 'ambul thiyal' in name_lower:
            new_url = PHOTOS['fish_curry']
        elif 'black pork' in name_lower or 'pork curry' in name_lower:
            new_url = PHOTOS['pork_curry']
        elif 'jackfruit' in name_lower or 'polos' in name_lower:
            new_url = PHOTOS['jackfruit']
        elif 'biryani' in name_lower:
            new_url = PHOTOS['biryani']
        elif 'black pepper beef' in name_lower or 'prawn claypot' in name_lower:
            new_url = PHOTOS['chicken_curry']

        if new_url:
            item.image_url = new_url
            menu_updates_count += 1
            print(f"Updated MenuItem #{item.id} '{item.name}' -> {new_url.split('/')[-1]}")

    # 2. Update Categories
    cat_updates_count = 0
    categories = db.query(Category).all()
    for cat in categories:
        c_name = cat.name.lower()
        new_url = None
        if 'kottu' in c_name:
            new_url = PHOTOS['chicken_kottu']
        elif 'sambol' in c_name:
            new_url = PHOTOS['pol_sambol']
        elif 'dessert' in c_name or 'sweet' in c_name:
            new_url = PHOTOS['watalappan']
        elif 'tea' in c_name or 'drink' in c_name:
            new_url = PHOTOS['king_coconut']
        elif 'short eat' in c_name:
            new_url = PHOTOS['fish_cutlets']
        elif 'seafood' in c_name:
            new_url = PHOTOS['hbc']
        elif 'hopper' in c_name:
            new_url = PHOTOS['egg_hopper']
        elif 'curry' in c_name:
            new_url = PHOTOS['rice_and_curry']

        if new_url:
            cat.image_url = new_url
            cat_updates_count += 1
            print(f"Updated Category #{cat.id} '{cat.name}' -> {new_url.split('/')[-1]}")

    # 3. Update Special Offers
    offer_updates_count = 0
    offers = db.query(SpecialOffer).all()
    for off in offers:
        o_name = off.title.lower()
        new_url = None
        if 'kottu' in o_name:
            new_url = PHOTOS['chicken_kottu']
        elif 'crab' in o_name:
            new_url = PHOTOS['crab_curry']
        elif 'hopper' in o_name:
            new_url = PHOTOS['egg_hopper']
        elif 'biryani' in o_name:
            new_url = PHOTOS['biryani']
        elif 'dessert' in o_name:
            new_url = PHOTOS['watalappan']
        elif 'curry & rice' in o_name or 'banquet' in o_name:
            new_url = PHOTOS['rice_and_curry']
        elif 'seafood' in o_name:
            new_url = PHOTOS['hbc']
        elif 'tea' in o_name or 'short-eats' in o_name:
            new_url = PHOTOS['fish_cutlets']
        elif 'grand ceylon' in o_name or 'dining experience' in o_name:
            new_url = PHOTOS['restaurant_meal']

        if new_url:
            off.image_url = new_url
            offer_updates_count += 1
            print(f"Updated SpecialOffer #{off.id} '{off.title}' -> {new_url.split('/')[-1]}")

    # 4. Update Gallery Images
    gallery_updates_count = 0
    gallery_items = db.query(GalleryImage).all()
    for g in gallery_items:
        alt_lower = g.alt_text.lower()
        new_url = None
        if g.id == 1:
            new_url = PHOTOS['rice_and_curry']
            g.alt_text = "Traditional Ceylon Rice & Curry Spread"
        elif g.id == 3:
            new_url = PHOTOS['pol_sambol']
            g.alt_text = "Fresh Sri Lankan Pol Sambol with Chilies"
        elif g.id == 6:
            new_url = PHOTOS['restaurant_meal']
            g.alt_text = "Authentic Sri Lankan Fine Dining Setup"
        elif g.id == 9:
            new_url = PHOTOS['restaurant_meal']
            g.alt_text = "Ceylon Restaurant Dining Hall & Hospitality"
        elif g.id == 16:
            new_url = PHOTOS['king_coconut']
            g.alt_text = "Fresh King Coconut Beverage Bar"
        elif g.id == 21:
            new_url = PHOTOS['hbc']
            g.alt_text = "Signature Negombo Hot Butter Cuttlefish"
        elif g.id == 30:
            new_url = PHOTOS['crab_curry']
            g.alt_text = "Jaffna Lagoon Claypot Crab Curry"
        elif g.id == 36:
            new_url = PHOTOS['watalappan']
            g.alt_text = "Artisanal Ceylon Spiced Watalappan"

        if new_url:
            g.image_url = new_url
            gallery_updates_count += 1
            print(f"Updated GalleryImage #{g.id} '{g.alt_text}' -> {new_url.split('/')[-1]}")

    db.commit()
    db.close()
    print("\nSUCCESS SUMMARY:")
    print(f"- Menu Items Updated: {menu_updates_count}")
    print(f"- Categories Updated: {cat_updates_count}")
    print(f"- Special Offers Updated: {offer_updates_count}")
    print(f"- Gallery Images Updated: {gallery_updates_count}")
    print("- All other dish photos retained as original!")

if __name__ == '__main__':
    update_photos()
