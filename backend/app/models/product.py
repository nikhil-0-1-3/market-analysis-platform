from pydantic import BaseModel


class ProductOverview(BaseModel):
    platform: str
    api_products: list[str]
    trader_app_features: list[str]
    core_modules: list[str]
    business_value: list[str]
