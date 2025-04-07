from pydantic import BaseModel


class PercentageResponseModel(BaseModel):
    positive_percentage: str
    negative_percentage: str
    average_rating: float
