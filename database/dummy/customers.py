from .sales_persons import salesA, salesB
from app.main.models import Customer
from .. import db


# add customers
cusA = Customer(
    username="cusA", 
    address="SHINJUKU EASTSIDE SQUARE 6-27-30 Shinjuku, Shinjuku-ku, Tokyo 160-8430, Japan",
    img_link="https://cdn.medcom.id/dynamic/content/2022/06/19/1440278/r7gTknhVI2.jpg?w=480",
    sales_id=salesA.username
)
cusB = Customer(
    username="cusB", 
    address="Residence No. 55 Central Luxury Mansion",
    img_link="https://helpx.adobe.com/content/dam/help/en/illustrator/how-to/character-design/jcr_content/main-pars/image/character-design-intro_900x506.jpg.img.jpg",
    sales_id=salesA.username
)
cusC = Customer(
    username="cusC", 
    address="2 Chome-8-1 Nagao, Tama Ward, Kawasaki Prefecture, Kanagawa 214-0023, Japan",
    img_link="https://lumiere-a.akamaihd.net/v1/images/ct_belle_upcportalreskin_20694_e5816813.jpeg?region=0,0,330,330",
    sales_id=salesB.username
)

# add to database
db.session.add_all([
    cusA, cusB, cusC
])
db.session.commit()