from typing import List

from groq import BaseModel


class ReviewResponseModel(BaseModel):
    reviews: List[str]
