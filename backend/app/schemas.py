from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, model_validator

# Pydantic serializes Decimal as a JSON string by default; the API returns a number.
Price = Annotated[Decimal, PlainSerializer(float, return_type=float)]


class VehicleCreate(BaseModel):
    make: str = Field(min_length=1, max_length=50)
    model: str = Field(min_length=1, max_length=50)
    category: str = Field(min_length=1, max_length=50)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    quantity: int = Field(ge=0)


class VehicleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    make: str
    model: str
    category: str
    price: Price
    quantity: int


class VehicleSearch(BaseModel):
    make: str | None = None
    model: str | None = None
    category: str | None = None
    min_price: Decimal | None = Field(default=None, ge=0)
    max_price: Decimal | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def check_price_range(self):
        if (
            self.min_price is not None
            and self.max_price is not None
            and self.min_price > self.max_price
        ):
            raise ValueError("min_price must not be greater than max_price")
        return self
