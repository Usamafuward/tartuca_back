import os
import sys
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models

def update_data():
    db = SessionLocal()
    try:
        print("Starting Sri Lankan restaurant data update...")

        # 1. Update Categories
        categories_updates = {
            1: {"name": "Woodfired Pizzas & Paan", "slug": "pizza"},
            2: {"name": "Ceylon Spiced Rice & Kottu", "slug": "pasta"},
            3: {"name": "Fresh Sambols & Salads", "slug": "salads"},
            4: {"name": "Ceylon Sweets & Desserts", "slug": "desserts"},
            5: {"name": "Tropical Drinks & Ceylon Teas", "slug": "drinks"},
            6: {"name": "Ceylon Short Eats & Starters", "slug": "antipasti"},
            7: {"name": "Claypot Curries & Grills", "slug": "secondi"},
            8: {"name": "Negombo Lagoon & Ocean Seafood", "slug": "seafood"},
            9: {"name": "Village Hoppers & Breakfast", "slug": "breakfast"},
            10: {"name": "Traditional Claypot Mains", "slug": "mains"},
            11: {"name": "Island Roasts & Burgers", "slug": "burgers"},
            12: {"name": "Signature Island Mocktails", "slug": "cocktails"},
            13: {"name": "Cellar Wines & Ceylon Spirits", "slug": "wines"}
        }

        for cat_id, data in categories_updates.items():
            cat = db.query(models.Category).filter(models.Category.id == cat_id).first()
            if cat:
                cat.name = data["name"]
                cat.slug = data["slug"]
                print(f"Updated Category {cat_id}: {cat.name}")

        db.commit()

        # 2. Update Menu Items
        srilankan_dishes = [
            # ID: (Name, Description, Price, is_veg, is_gf)
            (1, "Colombo Woodfired Margherita", "Traditional stonebaked pizza topped with local buffalo mozzarella, ripe San Marzano tomatoes, and fresh sweet basil.", 1850.00, True, False),
            (2, "Spicy Devilled Chicken & Pepperoni Pizza", "Crispy crust topped with spiced marinated devilled chicken, beef pepperoni, banana peppers, and melted mozzarella.", 2350.00, False, False),
            (3, "Ceylon Roast Chicken & Egg Kottu", "Hand-chopped godamba roti tossed on hot griddle with farm eggs, tender chicken, leeks, and rich aromatic curry gravy.", 1650.00, False, False),
            (4, "Gotu Kola & Green Papaya Sambol Salad", "Crisp pennywort greens, freshly grated coconut, shallots, green chilies, and lime dressing.", 950.00, True, True),
            (5, "Artisanal Ceylon Watalappan", "Steamed rich jaggery custard spiced with cardamom, nutmeg, kithul treacle, and roasted cashew nuts.", 850.00, True, True),
            (6, "Fresh King Coconut & Lime Cooler", "Chilled natural king coconut water blended with freshly squeezed lime and a hint of mint.", 650.00, True, True),
            (8, "Seer Fish Carpaccio with Kochchi Dressing", "Thinly sliced ocean-fresh seer fish marinated in calamansi lime, extra virgin oil, kochchi chili, and pink sea salt.", 2100.00, False, True),
            (10, "Crab & Avocado Bruschetta with Curry Leaf Oil", "Crispy toasted woodfired paan topped with fresh lagoon crab meat, ripe avocado, and fragrant curry leaf infused oil.", 1850.00, False, False),
            (11, "Tartuca Signature Seafood Claypot Pizza", "Woodfired crust layered with buttered prawns, calamari, curry leaf pesto, and smoked buffalo mozzarella.", 2650.00, False, False),
            (12, "Negombo Woodfired Paan & Dips Platter", "Freshly baked woodfired crusty roast paan served with pol sambol, seeni sambol, and dhal curry dip.", 1250.00, True, False),
            (13, "Fiery Devilled Beef Pizza with Green Chilies", "Slow-roasted tender beef chunks tossed in hot devilled glaze, sweet onions, capsicums, and cheese.", 2450.00, False, False),
            (14, "Four Cheese & Kithul Glazed Woodfired Paan", "Melange of artisan local cheeses, toasted cashews, and a drizzle of pure organic Sinharaja kithul treacle.", 2100.00, True, False),
            (16, "Lagoon Seafood Kottu with Calamari & Prawns", "Chopped flaky flatbread wok-fried with giant prawns, ocean cuttlefish, egg, and spicy seafood stock.", 2450.00, False, False),
            (17, "Pumpkin & Spinach Curry Leaf Gnocchi", "Hand-rolled potato gnocchi tossed with roasted pumpkin puree, tender spinach, and toasted mustard seed butter.", 1950.00, True, False),
            (20, "Slow-Braised Ceylon Black Pepper Beef", "Tender beef shank slow-cooked in roasted black curry powder, Goraka, cracked black pepper, and thick onion gravy.", 2850.00, False, True),
        ]

        # General dictionary for remaining dishes by ID or fallback
        dish_templates = [
            ("Jaffna Lagoon Crab Curry", "Fresh blue swimming crab simmered in roasted Jaffna curry powder, coconut milk, and fragrant moringa leaves.", 3200.00, False, True),
            ("Negombo Hot Butter Cuttlefish (HBC)", "Crispy flash-fried cuttlefish rings tossed with butter, spring onions, dried chilies, and capsicum.", 2250.00, False, False),
            ("Black Pork Curry with Roast Paan", "Pork belly slow-simmered in roasted Sri Lankan spices, Goraka, and black pepper, served with crusty roast bread.", 2400.00, False, False),
            ("King Prawn Claypot Curry", "Jumbo ocean prawns cooked in fragrant coconut cream, fenugreek, turmeric, and fresh curry leaves.", 2750.00, False, True),
            ("Authentic Miris Fish Ambul Thiyal", "Traditional Southern sour fish curry made with fresh yellowfin tuna, Goraka paste, and black pepper.", 2100.00, False, True),
            ("Egg Hopper & Plain Hopper Basket", "Crispy edged bowl-shaped hoppers served with spicy katta sambol, caramelized seeni sambol, and creamy coconut milk.", 1150.00, True, True),
            ("Tangalle Flame-Grilled Seer Fish Steak", "Wild-caught seer fish marinated in lime, garlic, and Ceylon spices, chargrilled and served with fresh greens.", 2650.00, False, True),
            ("Tender Jackfruit (Polos) Curry", "Young baby jackfruit slow-braised for hours in rich roasted spices until meltingly tender and deeply flavorful.", 1350.00, True, True),
            ("Red Lentil Dhal with Tempered Mustard", "Creamy mysore dhal tempered with garlic, shallots, cumin, and fried curry leaves in thick coconut milk.", 950.00, True, True),
            ("Traditional Sri Lankan Fish Cutlets (4 pcs)", "Crispy breaded croquettes packed with spiced canned mackerel, potato, green chili, and black pepper.", 850.00, False, False),
            ("Mutton Sukka Fry with Banana Peppers", "Tender boneless mutton tossed dry with crushed coriander, fennel, curry leaves, and banana peppers.", 2750.00, False, True),
            ("Claypot Chicken Biryani with Mint Sambol", "Aromatic long-grain basmati cooked in whole spices with marinated chicken, served with egg, raita, and gravy.", 1950.00, False, False),
            ("Curd & Kithul Honey with Toasted Cashews", "Fresh organic buffalo curd drizzled with dark organic kithul palm treacle and crushed golden cashews.", 750.00, True, True),
            ("Tropical Passion Fruit & Mango Pavlova", "Crisp meringue nest topped with fresh passion fruit coulis, sweet mango cubes, and coconut cream.", 950.00, True, True),
            ("Iced Ceylon Cardamom Milk Tea", "High-grown Ceylon black tea brewed with crushed green cardamom pods, sweetened condensed milk, and ice.", 550.00, True, True),
            ("Golden Coconut Arrack Sour Mocktail", "Refreshing mocktail with fresh pineapple juice, lime, tamarind reduction, and crushed ginger.", 750.00, True, True),
            ("Wood Apple Nectar Smoothie", "Traditional tangy-sweet wood apple fruit blended with coconut milk, palm jaggery, and ice.", 650.00, True, True)
        ]

        # Apply specific mappings first
        for item_tuple in srilankan_dishes:
            item_id, name, desc, price, is_veg, is_gf = item_tuple
            item = db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()
            if item:
                item.name = name
                item.description = desc
                item.price = Decimal(str(price))
                item.is_vegetarian = is_veg
                item.is_gluten_free = is_gf
                print(f"Updated MenuItem {item_id}: {item.name}")

        # Update remaining items that still have generic or Italian names
        remaining_items = db.query(models.MenuItem).filter(models.MenuItem.id > 20).all()
        for idx, item in enumerate(remaining_items):
            template = dish_templates[idx % len(dish_templates)]
            item.name = template[0] + (f" (Special {idx+1})" if idx >= len(dish_templates) else "")
            item.description = template[1]
            item.price = Decimal(str(template[2]))
            item.is_vegetarian = template[3]
            item.is_gluten_free = template[4]
            print(f"Updated MenuItem {item.id}: {item.name}")

        db.commit()

        # 3. Update Special Offers
        srilankan_offers = [
            (1, "Colombo Street Feast: Kottu & Devilled Platter", "Hand-chopped chicken kottu, devilled cuttlefish, fish cutlets, and fresh lime cooler.", 2950.00, "20% OFF", "bg-orange-500"),
            (2, "Family Claypot Curry & Rice Feast for Four", "Choice of Jaffna crab curry or black pork curry, yellow rice, dhal, polos, pol sambol, and hoppers.", 6800.00, "FAMILY DEAL", "bg-amber-600"),
            (3, "Flame-Grilled Lagoon Seafood Platter", "Jumbo prawns, seer fish steaks, devilled calamari, and garlic herb woodfired paan.", 4800.00, "CHEF'S SPECIAL", "bg-red-600"),
            (4, "Traditional Ceylon Dessert Trio", "Artisanal Watalappan, curd with Sinharaja kithul treacle, and coconut ice cream.", 1450.00, "POPULAR", "bg-emerald-600"),
            (5, "Grand Ceylon Dining Experience for Two", "Five-course tasting banquet including crab soup, short eats, claypot curries, and watalappan.", 5500.00, "SIGNATURE", "bg-amber-500"),
            (6, "Chef's 5-Course Coastal Seafood Tasting", "Live lagoon mud crab, marinated seer fish, hot butter cuttlefish, and coconut lime sorbet.", 6500.00, "PREMIUM", "bg-yellow-500"),
            (7, "Weekend Village Hopper & Short-Eats Brunch", "Unlimited hot plain and egg hoppers with katta sambol, seeni sambol, and spiced Ceylon chai.", 2400.00, "WEEKEND SPECIAL", "bg-blue-600"),
            (8, "Sunday Claypot Biryani Banquet for Four", "Dum-cooked chicken biryani with mint sambol, boiled eggs, acchar, and creamy gravy.", 5200.00, "SUNDAY FEAST", "bg-orange-600"),
            (9, "Sunset Island Bites & Tropical Mocktails for Two", "Fish cutlets, mutton rolls, spicy cassava chips, and two king coconut coolers.", 2200.00, "SUNSET SPECIAL", "bg-rose-500"),
            (10, "Executive Colombo Express Business Lunch", "Choice of yellow rice with chicken or fish curry, two vegetable curries, papadam, and iced tea.", 1850.00, "QUICK SERVE", "bg-teal-600"),
            (11, "Chef's Heritage Tasting Platter", "Six signature miniature curries with string hoppers, pol roti, and fresh coconut sambol.", 3800.00, "TASTING MENU", "bg-purple-600"),
            (12, "Jaffna Lagoon Crab Dinner for Two", "Two large fresh crabs in dark spicy Jaffna curry with hot crusty roast paan and butter.", 5800.00, "MUST TRY", "bg-red-600"),
            (13, "Woodfired Island Pizza & Spicy Wings Combo", "Choice of seafood or devilled chicken pizza with 6 crispy spiced wings and drinks.", 3200.00, "COMBO DEAL", "bg-amber-600"),
            (14, "Romantic Garden Candlelight Dinner for Two", "Private terrace table, 4-course bespoke menu, fresh floral table arrangement, and dessert.", 7500.00, "EXCLUSIVE", "bg-pink-600"),
            (15, "Island Village Family Banquet", "Rich feast featuring black pepper beef, seer fish, egg hoppers, pol roti, and watalappan.", 7200.00, "FEAST FOR 4-6", "bg-amber-700"),
            (16, "Ceylon Evening Tea & Short-Eats Platter", "Egg rolls, vegetable samosas, spicy fish patties, and premium pot of Ceylon highland tea.", 1650.00, "HIGH TEA", "bg-emerald-700")
        ]

        for offer_tuple in srilankan_offers:
            offer_id, title, desc, price, badge, badge_color = offer_tuple
            offer = db.query(models.SpecialOffer).filter(models.SpecialOffer.id == offer_id).first()
            if offer:
                offer.title = title
                offer.description = desc
                offer.price = Decimal(str(price))
                offer.badge_text = badge
                offer.badge_color = badge_color
                print(f"Updated SpecialOffer {offer_id}: {offer.title}")

        db.commit()

        # 4. Update Reviews
        srilankan_reviews = [
            ("Kasun Perera", 5, "The Jaffna Crab Curry and hot butter cuttlefish are hands down the best in Colombo! Warm spices, generous portions, and a lovely garden ambiance.", "positive"),
            ("Dilani Jayawardena", 5, "Ordered the family claypot feast for delivery. Arrived steaming hot in under 35 minutes. Truly authentic Ceylon flavor and wonderful packaging.", "positive"),
            ("Roshan Senanayake", 5, "Tartuca's egg hoppers and seeni sambol took me back to village cooking. Great island hospitality in the heart of Colombo 07.", "positive"),
            ("Amanda Fernando", 5, "Exceptional ocean prawns and woodfired pizzas. The staff were very attentive and the atmosphere under the trees is enchanting.", "positive"),
            ("Dinesh Wickramasinghe", 5, "Best mutton kothu and watalappan in town. Authentic spices without being overpoweringly greasy. Highly recommended!", "positive"),
            ("Shamila Weerasinghe", 5, "We hosted a family birthday dinner on the garden terrace. Delicious food, beautiful lighting, and five-star service.", "positive"),
            ("Kaveen Alwis", 5, "The black pepper pork curry with roast paan is perfection. A must-visit dining destination in Colombo.", "positive"),
            ("Minoli Silva", 4, "The coconut sambol and fish ambul thiyal had the exact traditional sour-peppery balance. Truly authentic!", "positive"),
            ("Tharindu Bandara", 5, "Top notch dining experience. The king coconut mocktail and devilled prawns are outstanding. Will definitely return.", "positive"),
            ("Nirosha Mendis", 5, "Such a cozy and stylish place. The claypot biryani and fresh juices were simply exquisite.", "positive"),
            ("Sachithra De Silva", 5, "Incredible food and lovely garden setting! Highly recommend the seafood platter and hopper basket.", "positive"),
            ("Dr. Priyantha Gunawardena", 5, "Celebrated our wedding anniversary at Tartuca. Chef's tasting menu was exceptional from starter to dessert.", "positive"),
            ("Chathurika Perera", 5, "Ordered takeaway via website. Smooth checkout, prompt delivery, and the food was packed with incredible flavor.", "positive"),
            ("Suresh Rajaratnam", 4, "Authentic Jaffna spices and fresh crab. One of the best authentic restaurants in Colombo.", "positive"),
            ("Ayesha Careem", 5, "Loved the atmosphere, soft jazz, and the watalappan was heavenly. 10/10 experience!", "positive"),
            ("Mahesh Samarasekera", 5, "Outstanding hospitality. The mutton sukka and garlic roast paan were delicious.", "positive"),
            ("Anoma Kulatunga", 5, "The vegetarian curry selection is generous and bursting with fresh coconut milk and spices. Loved it!", "positive"),
            ("Gihan Abeywickrama", 5, "Great dining experience with friends. Fast service and authentic Ceylon cooking.", "positive"),
            ("Ruvini Jayasuriya", 5, "Best hot butter cuttlefish in town! Crispy, buttery, and just the right spicy kick.", "positive")
        ]

        reviews = db.query(models.Review).all()
        for idx, rev in enumerate(reviews):
            template = srilankan_reviews[idx % len(srilankan_reviews)]
            rev.author_name = template[0]
            rev.rating = template[1]
            rev.comment = template[2]
            rev.sentiment = template[3]
            rev.is_approved = True
            print(f"Updated Review {rev.id}: {rev.author_name}")

        db.commit()
        print("Successfully updated all categories, menu items, special offers, and reviews to authentic Sri Lankan restaurant data!")

    except Exception as e:
        db.rollback()
        print(f"Error updating data: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    update_data()
