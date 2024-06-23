from sqlalchemy import Table, Column, ForeignKey, Integer, UniqueConstraint

from .base import Base

order_product_association_table = Table(
    "order_product_association",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("orders_id", ForeignKey("orders.id"), nullable=False,),
    Column("product_id", ForeignKey("products.id"), nullable=False,),
    UniqueConstraint("orders_id", "product_id", name="idx_unique_order_product"),
)
