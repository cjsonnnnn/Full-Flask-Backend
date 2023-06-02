from .warehouse import theWarehouse
from .categories import *
from app.main.models import Product
from .. import db


# add products
prdA = Product(
    name="Indomie Mi Instan Goreng Plus Special 85G",
    price=3100,
    description="Mi goreng yang lezat dan nikmat, terbuat dari bahan berkualitas dan rempah rempah terbaik.",
    available_qty=36,
    ordered_qty=0,
    total_qty=36,
    promo=0,
    img_link = "https://assets.klikindomaret.com/products/10003517/10003517_1.jpg",
    warehouse_id = theWarehouse.id,
    category_id= catA.id
)
prdB = Product(
    name="Sunlight Pencuci Piring Lime 420mL",
    price=9900,
    description="Sunlight Jeruk Nipis 100 mampu menghilangkan lemak dengan kekuatan 100 jeruk nipis di tiap kemasannya, secara aktif mengangkat dan menghilangkan lemak membandel, dan juga membersihkan dengan cepat berkat teknologi baru Cepat Bilas.",
    available_qty=3,
    ordered_qty=0,
    total_qty=3,
    promo=27,
    img_link = "https://assets.klikindomaret.com/products/20112492/20112492_1.jpg",
    warehouse_id = theWarehouse.id,
    category_id= catC.id
)
prdC = Product(
    name="Bear Brand Susu Encer Steril 189Ml",
    price=7300,
    description=f"Bear brand terbuat dari 100% susu sapi steril murni. Susu steril dianjurkan untuk setiap kegunaan yang membutuhkan susu dan dapat di konsumsi setiap hari sesuai kebutuhan.",
    available_qty=6,
    ordered_qty=0,
    total_qty=6,
    promo=45,
    img_link = "https://assets.klikindomaret.com/promos/20230517_07_00_20230523_23_00/10004906/10004906_1.jpg",
    warehouse_id = theWarehouse.id,
    category_id= catB.id
)
prdD = Product(
    name="Khong Guan Biscuit Red Segi Assorted 1600G",
    price=91500,
    description="Khong guan biskuit dengan kualitas terbaik, berbagai bentuk dan rasa yang enak didalamnya.",
    available_qty=312,
    ordered_qty=0,
    total_qty=312,
    promo=72,
    img_link = "https://assets.klikindomaret.com/products/10000360/10000360_1.jpg",
    warehouse_id = theWarehouse.id,
    category_id= catB.id
)
prdE = Product(
    name="Nescafe Coffee Drink Caramel Macchiato 220Ml",
    price=7000,
    description="Rasakan sensasi minuman kualitas Ala Caf kapan saja dan dimana saja didalam satu kemasan kaleng Nescaf Ala Caf. Dengan tiga varian rasa baru yaitu Latte, Cappucino, dan Caramel Macchiato, kenikmatan minuman caf kini bisa dinikmati oleh siapa saja. Perpadu",
    available_qty=35,
    ordered_qty=0,
    total_qty=35,
    promo=18,
    img_link = "https://assets.klikindomaret.com/products/20114494/20114494_1.jpg",
    warehouse_id = theWarehouse.id,
    category_id= catA.id
)
prdF = Product(
    name="So Klin Pembersih Lantai Sereh 780Ml",
    price=10900,
    description="SO KLIN Pembersih Lantai Sereh Lemon Grass merupakan cairan pembersih lantai yang di rancang khusus untuk memudahkan Anda dalam membersihkan lantai rumah. Cairan pembersih lantai persembahan SOKLIN ini secara efektif membersihkan seluruh permukaan lantai.",
    available_qty=463,
    ordered_qty=0,
    total_qty=463,
    promo=0,
    img_link = "https://assets.klikindomaret.com/products/20101095/20101095_1.jpg",
    warehouse_id = theWarehouse.id,
    category_id= catB.id
)

# store in a single variable
dummies = [
    prdA, 
    prdB,
    prdC,
    prdD,
    prdE,
    prdF
]

# add to database
db.session.add_all([
    prdA, prdB, prdC, prdD, prdE, prdF
])
db.session.commit()