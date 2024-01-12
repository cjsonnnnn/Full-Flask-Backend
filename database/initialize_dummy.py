import bcrypt

from app.models import *


def initializeDummy():
    try:
        # add an sales
        salesA = Sales(
            username="salesA",
            name="Suhendra",
            password=bcrypt.hashpw("sA".encode("utf-8"), bcrypt.gensalt()),
            email="jpiay40@students.calvin.ac.id",
            verified=True,
        )
        salesB = Sales(
            username="salesB",
            name="Siti",
            password=bcrypt.hashpw("sB".encode("utf-8"), bcrypt.gensalt()),
            email="cjsonnnnn@gmail.com",
            verified=False,
        )

        # add their carts. Notice that, since it is one to one relationship (uselist=False), so we use a normal assign method, instead of append
        cartA = Cart(qty=0)
        salesA.cart = cartA
        cartB = Cart(qty=0)
        salesB.cart = cartB

        # add customers
        cusA = Customer(
            username="cusA",
            address="SHINJUKU EASTSIDE SQUARE 6-27-30 Shinjuku, Shinjuku-ku, Tokyo 160-8430, Japan",
            img_link="https://cdn.medcom.id/dynamic/content/2022/06/19/1440278/r7gTknhVI2.jpg?w=480",
            sales_id=salesA.username,
        )
        cusB = Customer(
            username="cusB",
            address="Residence No. 55 Central Luxury Mansion",
            img_link="https://helpx.adobe.com/content/dam/help/en/illustrator/how-to/character-design/jcr_content/main-pars/image/character-design-intro_900x506.jpg.img.jpg",
            sales_id=salesA.username,
        )
        cusC = Customer(
            username="cusC",
            address="2 Chome-8-1 Nagao, Tama Ward, Kawasaki Prefecture, Kanagawa 214-0023, Japan",
            img_link="https://lumiere-a.akamaihd.net/v1/images/ct_belle_upcportalreskin_20694_e5816813.jpeg?region=0,0,330,330",
            sales_id=salesB.username,
        )

        # execute sales and customer data
        db.session.add_all([salesA, salesB, cusA, cusB, cusC])
        db.session.commit()

        # define a warehouse
        theWarehouse = Warehouse(ordered_qty=0, available_qty=0, total_qty=0)

        # execute warehouse
        db.session.add(theWarehouse)
        db.session.commit()

        # add categories
        catA = Category(name="beverages")
        catB = Category(name="foods")
        catC = Category(name="cleaning product")

        # execute categories
        db.session.add_all([catA, catB, catC])
        db.session.commit()

        # add products
        prdA = Product(
            name="Indomie Mi Instan Goreng Plus Special 85G",
            price=3100,
            description="Mi goreng yang lezat dan nikmat, terbuat dari bahan berkualitas dan rempah rempah terbaik.",
            available_qty=36,
            ordered_qty=0,
            total_qty=36,
            promo=0,
            img_link="https://assets.klikindomaret.com/products/10003517/10003517_1.jpg",
            warehouse_id=theWarehouse.id,
            category_id=catA.id,
        )
        prdB = Product(
            name="Sunlight Pencuci Piring Lime 420mL",
            price=9900,
            description="Sunlight Jeruk Nipis 100 mampu menghilangkan lemak dengan kekuatan 100 jeruk nipis di tiap kemasannya, secara aktif mengangkat dan menghilangkan lemak membandel, dan juga membersihkan dengan cepat berkat teknologi baru Cepat Bilas.",
            available_qty=3,
            ordered_qty=0,
            total_qty=3,
            promo=27,
            img_link="https://assets.klikindomaret.com/products/20112492/20112492_1.jpg",
            warehouse_id=theWarehouse.id,
            category_id=catC.id,
        )
        prdC = Product(
            name="Bear Brand Susu Encer Steril 189Ml",
            price=7300,
            description=f"Bear brand terbuat dari 100% susu sapi steril murni. Susu steril dianjurkan untuk setiap kegunaan yang membutuhkan susu dan dapat di konsumsi setiap hari sesuai kebutuhan.",
            available_qty=6,
            ordered_qty=0,
            total_qty=6,
            promo=45,
            img_link="https://assets.klikindomaret.com/promos/20230517_07_00_20230523_23_00/10004906/10004906_1.jpg",
            warehouse_id=theWarehouse.id,
            category_id=catB.id,
        )
        prdD = Product(
            name="Khong Guan Biscuit Red Segi Assorted 1600G",
            price=91500,
            description="Khong guan biskuit dengan kualitas terbaik, berbagai bentuk dan rasa yang enak didalamnya.",
            available_qty=312,
            ordered_qty=0,
            total_qty=312,
            promo=72,
            img_link="https://assets.klikindomaret.com/products/10000360/10000360_1.jpg",
            warehouse_id=theWarehouse.id,
            category_id=catB.id,
        )
        prdE = Product(
            name="Nescafe Coffee Drink Caramel Macchiato 220Ml",
            price=7000,
            description="Rasakan sensasi minuman kualitas Ala Caf kapan saja dan dimana saja didalam satu kemasan kaleng Nescaf Ala Caf. Dengan tiga varian rasa baru yaitu Latte, Cappucino, dan Caramel Macchiato, kenikmatan minuman caf kini bisa dinikmati oleh siapa saja. Perpadu",
            available_qty=35,
            ordered_qty=0,
            total_qty=35,
            promo=18,
            img_link="https://assets.klikindomaret.com/products/20114494/20114494_1.jpg",
            warehouse_id=theWarehouse.id,
            category_id=catA.id,
        )
        prdF = Product(
            name="So Klin Pembersih Lantai Sereh 780Ml",
            price=10900,
            description="SO KLIN Pembersih Lantai Sereh Lemon Grass merupakan cairan pembersih lantai yang di rancang khusus untuk memudahkan Anda dalam membersihkan lantai rumah. Cairan pembersih lantai persembahan SOKLIN ini secara efektif membersihkan seluruh permukaan lantai.",
            available_qty=463,
            ordered_qty=0,
            total_qty=463,
            promo=0,
            img_link="https://assets.klikindomaret.com/products/20101095/20101095_1.jpg",
            warehouse_id=theWarehouse.id,
            category_id=catB.id,
        )

        # execute product data
        db.session.add_all([prdA, prdB, prdC, prdD, prdE, prdF])
        db.session.commit()
    except Exception as e:
        db.session.rollback()
