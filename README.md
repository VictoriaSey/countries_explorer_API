# countries_explorer_API

A RESTful API built with **FastAPI** and **MongoDB** that serves as a personal explorer for countries around the world. It fetches live data from the free and open-source [restcountries.com](https://restcountries.com/) API, allowing users to find country data, save a list of favorite countries with personal notes, and compare them.

# Country Explorer API 

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.103.2-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-blueviolet.svg)](https://www.mongodb.com/)



##  Features

-   **Fetch Country Data**: Get up-to-date information for any country, including its capital, population, and region.
-   **Save Favorites**: Persistently store countries you're interested in, along with your own notes, in a MongoDB database.
-   **List Favorites**: Retrieve your curated list of saved countries.
-   **Compare Countries**: An endpoint to directly compare the populations of any two countries.
-   **Interactive Docs**: Automatic, interactive API documentation provided by FastAPI via Swagger UI and ReDoc.

## ️ Tech Stack

-   **Framework**: [FastAPI](https://fastapi.tiangolo.com/) for building the robust and high-performance API.
-   **Database**: [MongoDB](https://www.mongodb.com/) for flexible, NoSQL data storage.
-   **Async Driver**: [Motor](https://motor.readthedocs.io/) to interact with MongoDB asynchronously.
-   **Data Validation**: [Pydantic](https://docs.pydantic.dev/) for data modeling and validation.
-   **Server**: [Uvicorn](https://www.uvicorn.org/) as the lightning-fast ASGI server.
-   **External Data Source**: The free [restcountries.com v3.1 API](https://restcountries.com/).

##  Getting Started

### Prerequisites

-   Python 3.9+
-   A running instance of MongoDB. (e.g., via [Docker](https://www.docker.com/get-started/) or a local installation).

### Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/country-explorer.git
    cd country-explorer
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies from `requirements.txt`:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Run the application server:**
    ```sh
    uvicorn main:app --reload
    ```
    The API will be live at `http://127.0.0.1:8000`.

##  API Endpoints

Navigate to `http://127.0.0.1:8000/docs` for a live, interactive documentation experience.

#### 1. Fetch Country Information

-   **Endpoint**: `GET /countries/{name}`
-   **Description**: Retrieves public data for a single country.
-   **Example Request**:
    ```sh
    curl http://127.0.0.1:8000/countries/Estonia
    ```
-   **Example Response**:
    ```json
    {
      "name": "Estonia",
      "capital": "Tallinn",
      "population": 1331057,
      "region": "Europe"
    }
    ```

#### 2. Save a Favorite Country

-   **Endpoint**: `POST /countries/favorites?name={name}&notes={notes}`
-   **Description**: Fetches country data, adds user notes, and saves it to the database.
-   **Example Request**:
    ```sh
    curl -X POST "http://127.0.0.1:8000/countries/favorites?name=Japan&notes=Want%20to%20visit%20Tokyo%20and%20Kyoto"
    ```
-   **Example Response**:
    ```json
    {
      "id": "673f8e2a1b9d4e3a9c7b2d1f",
      "name": "Japan",
      "capital": "Tokyo",
      "population": 125836021,
      "region": "Asia",
      "user_notes": "Want to visit Tokyo and Kyoto",
      "date_saved": "2025-09-14T20:00:00.000Z"
    }
    ```

#### 3. List All Favorites

-   **Endpoint**: `GET /countries/favorites`
-   **Description**: Returns a list of all saved countries.
-   **Example Request**:
    ```sh
    curl http://127.0.0.1:8000/countries/favorites
    ```

#### 4. Compare Two Countries (Extra Challenge)

-   **Endpoint**: `GET /countries/compare?country1={name1}&country2={name2}`
-   **Description**: Compares the populations of two countries.
-   **Example Request**:
    ```sh
    curl "http://127.0.0.1:8000/countries/compare?country1=China&country2=India"
    ```
-   **Example Response**:
    ```json
    {
      "country1": { "name": "China", "capital": "Beijing", "population": 1425893465, "region": "Asia" },
      "country2": { "name": "India", "capital": "New Delhi", "population": 1428627663, "region": "Asia" },
      "population_difference": 2734198,
      "message": "India has a larger population by 2,734,198 people."
    }
    ```
