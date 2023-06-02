from app.main.models import Warehouse
from .. import db


# define a warehouse
theWarehouse = Warehouse(
    ordered_qty = 0,
    available_qty = 0,
    total_qty = 0
)

# add to database
db.session.add(theWarehouse)
db.session.commit()