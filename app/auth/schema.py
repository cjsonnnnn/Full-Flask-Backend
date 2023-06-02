from .. import ma
from .models import Sales


class SalesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Sales
        include_fk = True