from app.models import *

category_obj1 = Category(name="Clothing")
category_obj2 = Category(name="Travel")
category_obj3 = Category(name="Technology")
category_obj4 = Category(name="Nature")
category_obj5 = Category(name="Health")
category_obj6 = Category(name="Literature")
category_obj7 = Category(name="Psychology")
db.session.add_all([category_obj1, category_obj2, category_obj3,
                    category_obj4, category_obj5, category_obj6, category_obj7])

privacy_obj1 = Privacy(description="Public")
privacy_obj2 = Privacy(description="Followers")
privacy_obj3 = Privacy(description="Only Me")
db.session.add_all([privacy_obj1, privacy_obj2, privacy_obj3])
db.session.commit()

print("Category and Privacy Tables Populated")
