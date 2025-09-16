# main.py
import requests
import os
from datetime import datetime
from typing import Optional, Annotated
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Query, Form, status, File, UploadFile
from pydantic import BaseModel, Field, HttpUrl
from dotenv import load_dotenv

# --- Cloudinary and Database Integration ---
import cloudinary
import cloudinary.uploader
from db import favourites_collection
from utils import replace_mongo_id

load_dotenv()

# --- Configure Cloudinary ---
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
)

# --- FastAPI App Initialization with OpenAPI Tags ---
tags_metadata = [
    {
        "name": "Home",
        "description": "Welcome to Queen's Country Explorer API!",
    },
    {
        "name": "Country Information",
        "description": "Endpoints for fetching data from the external REST Countries API.",
    },
    {
        "name": "Favorite Countries",
        "description": "Manage your list of saved favorite countries (CRUD).",
    },
]

app = FastAPI(
    title="Queen's Country Explorer API",
    description="Fetch data about countries, save your favorites with notes, and compare them.",
    openapi_tags=tags_metadata,
)

# --- Pydantic Models ---
class CountryData(BaseModel):
    """Represents the core data fetched for a country."""
    name: str
    capital: Optional[str] = None
    population: int
    region: str

class SavedCountry(BaseModel):
    """Represents a country saved as a favorite in the database."""
    id: Optional[str] = Field(alias="_id", default=None)
    name: str
    capital: Optional[str] = None
    population: int
    region: str
    user_notes: Optional[str] = None
    image_url: Optional[HttpUrl] = None  
    image_public_id: Optional[str] = None  
    date_saved: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class ComparisonResult(BaseModel):
    """Model for the country comparison response."""
    country1: CountryData
    country2: CountryData
    population_difference: int
    message: str

# --- Helper Function ---
def fetch_country_from_api(name: str) -> Optional[CountryData]:
    url = f"https://restcountries.com/v3.1/name/{name}?fullText=true"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()[0]
        capital = data.get("capital", [None])[0]
        return CountryData(
            name=data["name"]["common"],
            capital=capital,
            population=data["population"],
            region=data["region"],
        )
    except (requests.exceptions.RequestException, IndexError, KeyError):
        return None

# --- API Endpoints ---

# --- Home Endpoint ---
@app.get("/", tags=["Home"], summary="Welcome Message")
def read_root():
    return {"message": "Welcome to the Queen's Country Explorer API!"}

# --- Country Information Endpoints ---
@app.get(
    "/countries/search/{name}",
    response_model=CountryData,
    tags=["Country Information"],
    summary="Search for a single country",
)
def search_country_info(name: str):
    country_data = fetch_country_from_api(name)
    if not country_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country '{name}' not found."
        )
    return country_data

@app.get(
    "/countries/compare",
    response_model=ComparisonResult,
    tags=["Country Information"],
    summary="Compare two countries by population",
)
def compare_countries(
    country1: str = Query(..., description="The first country to compare. Example: China"),
    country2: str = Query(..., description="The second country to compare. Example: India"),
):
    data1 = fetch_country_from_api(country1)
    if not data1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country '{country1}' not found.",
        )
    data2 = fetch_country_from_api(country2)
    if not data2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country '{country2}' not found.",
        )

    difference = abs(data1.population - data2.population)
    message = (
        f"{data1.name} has a larger population by {difference:,} people."
        if data1.population > data2.population
        else f"{data2.name} has a larger population by {difference:,} people."
    )
    return ComparisonResult(
        country1=data1,
        country2=data2,
        population_difference=difference,
        message=message,
    )

# --- Favorite Countries Endpoints ---
@app.post(
    "/favorites",
    status_code=status.HTTP_201_CREATED,
    tags=["Favorite Countries"],
    summary="Save a country as a favorite with an image",
)
def save_favorite_country(
    name: Annotated[str, Form()],
    user_notes: Annotated[Optional[str], Form()] = None,
    favorite_picture: Annotated[Optional[UploadFile], File()] = None,
):
    if favourites_collection.find_one({"name": name}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"'{name}' is already in your favorites.",
        )
    country_data = fetch_country_from_api(name)
    if not country_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot save favorite: Country '{name}' not found.",
        )

    image_url = None
    image_public_id = None
    if favorite_picture:
        upload_result = cloudinary.uploader.upload(favorite_picture.file)
        image_url = upload_result["secure_url"]
        image_public_id = upload_result["public_id"]

    favorite_doc = SavedCountry(
        **country_data.model_dump(),
        user_notes=user_notes,
        image_url=image_url,
        image_public_id=image_public_id,
    )
    
    doc_to_insert = favorite_doc.model_dump(mode='json', by_alias=True, exclude={"id"})

    db_result = favourites_collection.insert_one(doc_to_insert)
    created_favorite = favourites_collection.find_one({"_id": db_result.inserted_id})
    return {"data": replace_mongo_id(created_favorite)}

@app.get(
    "/favorites",
    tags=["Favorite Countries"],
    summary="List all favorite countries"
)
def get_all_favorites(limit: int = 10, skip: int = 0):
    favorites_cursor = (
        favourites_collection.find().sort("date_saved", -1).limit(limit).skip(skip)
    )
    favorites_list = list(favorites_cursor)
    return {"data": list(map(replace_mongo_id, favorites_list))}

@app.get(
    "/favorites/{favorite_id}",
    tags=["Favorite Countries"],
    summary="Get a specific favorite country",
)
def get_favorite_by_id(favorite_id: str):
    if not ObjectId.is_valid(favorite_id):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid favorite ID received!"
        )
    favorite = favourites_collection.find_one({"_id": ObjectId(favorite_id)})
    if not favorite:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Favorite country not found.")
    return {"data": replace_mongo_id(favorite)}

@app.put(
    "/favorites/{favorite_id}",
    tags=["Favorite Countries"],
    summary="Update notes and/or image for a favorite country",
)
def update_favorite_country(
    favorite_id: str,
    user_notes: Annotated[Optional[str], Form()] = None,
    favorite_picture: Annotated[Optional[UploadFile], File()] = None,
):
    if not ObjectId.is_valid(favorite_id):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid favorite ID received!"
        )
    existing_favorite = favourites_collection.find_one({"_id": ObjectId(favorite_id)})
    if not existing_favorite:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "No favorite country found to update!"
        )
    
    update_fields = {}
    if user_notes is not None:
        update_fields["user_notes"] = user_notes
    
    if favorite_picture:
        if existing_favorite.get("image_public_id"):
            cloudinary.uploader.destroy(existing_favorite["image_public_id"])
        
        upload_result = cloudinary.uploader.upload(favorite_picture.file)
        update_fields["image_url"] = upload_result["secure_url"]
        update_fields["image_public_id"] = upload_result["public_id"]
        
    if not update_fields:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No update fields provided.")
    
    favourites_collection.update_one(
        {"_id": ObjectId(favorite_id)}, {"$set": update_fields}
    )
    return {"message": "Favorite country updated successfully!"}

@app.delete(
    "/favorites/{favorite_id}",
    tags=["Favorite Countries"],
    summary="Delete a favorite country",
)
def delete_favorite(favorite_id: str):
    if not ObjectId.is_valid(favorite_id):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid favorite ID received!"
        )
    
    favorite_to_delete = favourites_collection.find_one({"_id": ObjectId(favorite_id)})
    if not favorite_to_delete:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "No favorite country found to delete!"
        )
    
    if favorite_to_delete.get("image_public_id"):
        cloudinary.uploader.destroy(favorite_to_delete["image_public_id"])
    
    delete_result = favourites_collection.delete_one({"_id": ObjectId(favorite_id)})
    
    if not delete_result.deleted_count:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "No favorite country found to delete!"
        )
    return {"message": "Favorite country deleted successfully!"}
