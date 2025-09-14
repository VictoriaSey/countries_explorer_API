# Queen's Country Explorer API

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python) 
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb) 
![Cloudinary](https://img.shields.io/badge/Cloudinary-3448C5?style=for-the-badge&logo=cloudinary)

A robust backend API built with FastAPI to fetch data about countries, save your favorites with custom notes and images, and compare them.

## Description

This API provides a backend service for an application that explores country data. It leverages the external [REST Countries API](https://restcountries.com/) for real-time information, uses MongoDB for storage of user favorites, and integrates with Cloudinary for cloud-based image storage and management.

## Features

-   **Search Country Data**: Get detailed information for any country by its common name.
-   **Compare Countries**: Compare the populations of two different countries.
-   **Manage Favorites**: Full CRUD (Create, Read, Update, Delete) functionality for a personalized list of favorite countries.
-   **Custom Notes**: Add and update personal text notes for each saved country.
-   **Image Uploads**: Upload a custom image for each favorite, which is securely hosted on Cloudinary.

## Technologies Used

-   **Backend**: Python, FastAPI
-   **Database**: MongoDB (with PyMongo)
-   **Image Storage**: Cloudinary
-   **Server**: Uvicorn
-   **Data Validation**: Pydantic
-   **External API Client**: Requests
-   **Environment Management**: python-dotenv

## Setup and Installation

Follow these steps to get the application running locally.

### 1. Prerequisites

-   Python 3.8+
-   A MongoDB Atlas account (or a local MongoDB instance)
-   A Cloudinary account

### 2. Clone the Repository

```bash
git clone <your-repository-url>
cd <project-directory>
