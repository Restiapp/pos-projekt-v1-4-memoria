from typing import NewType, Union, List, Dict

# Strong types for IDs to prevent mixing them up
OrderId = NewType("OrderId", int)
OrderItemId = NewType("OrderItemId", int)
TableId = NewType("TableId", int)
ProductId = NewType("ProductId", int)
CustomerId = NewType("CustomerId", int)
UserId = NewType("UserId", int)

# JSON Type alias
JsonDict = Dict[str, Union[str, int, float, bool, None, "JsonDict", List["JsonDict"]]]
