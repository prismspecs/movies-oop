import csv
import os
from istorage import IStorage

class StorageCsv(IStorage):
    """
    A concrete implementation of the IStorage interface that
    stores movie data in a CSV file.
    
    The CSV file has the following headers:
        title,year,rating,poster

    Example of a CSV file content:
    title,year,rating,poster
    Titanic,1995,9.2,https://example.com/titanic.jpg
    The Dark Knight,2002,8.8,https://example.com/darkknight.jpg
    """

    def __init__(self, file_path):
        """
        :param file_path: Path to the CSV file for storing movie data.
        """
        self.file_path = file_path

    def list_movies(self):
        """
        Reads the CSV file and returns a dictionary of movies.

        Format (as per the IStorage interface):
        {
          "Titanic": {
            "year": 1995,
            "rating": 9.2,
            "poster": "https://example.com/titanic.jpg"
          },
          "The Dark Knight": {
            "year": 2002,
            "rating": 8.8,
            "poster": "https://example.com/darkknight.jpg"
          }
        }
        """
        return self._load_data()

    def add_movie(self, title, year, rating, poster):
        """
        Adds a new movie entry to the CSV file.
        """
        movies = self._load_data()
        movies[title] = {
            "year": year,
            "rating": rating,
            "poster": poster
        }
        self._save_data(movies)

    def delete_movie(self, title):
        """
        Deletes a movie from the CSV file by title.
        """
        movies = self._load_data()
        if title in movies:
            del movies[title]
        self._save_data(movies)

    def update_movie(self, title, rating):
        """
        Updates the rating of a movie by title.
        """
        movies = self._load_data()
        if title in movies:
            movies[title]["rating"] = rating
        self._save_data(movies)

    def _load_data(self):
        """
        Internal helper that reads the CSV file and returns a dictionary.

        If the file doesn't exist or is empty, returns an empty dictionary.
        """
        if not os.path.exists(self.file_path):
            return {}

        movies = {}
        try:
            with open(self.file_path, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    title = row["title"]
                    
                    # Attempt to parse year as int, rating as float
                    try:
                        year = int(row["year"])
                    except ValueError:
                        year = None  # or 0, or handle differently
                    try:
                        rating = float(row["rating"])
                    except ValueError:
                        rating = None
                    
                    poster = row["poster"]
                    movies[title] = {
                        "year": year,
                        "rating": rating,
                        "poster": poster
                    }
        except (IOError, KeyError, csv.Error):
            # Return empty if file is corrupted or has missing columns
            return {}
        
        return movies

    def _save_data(self, movies):
        """
        Internal helper that writes the dictionary back to the CSV file.
        The CSV will have a header row: title, year, rating, poster
        """
        # Convert dictionary to a list of rows that DictWriter can handle
        fieldnames = ["title", "year", "rating", "poster"]
        
        with open(self.file_path, "w", encoding="utf-8", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for title, info in movies.items():
                # info is a dict like {"year": 1995, "rating": 9.2, "poster": "..."}
                row = {
                    "title": title,
                    "year": info.get("year", ""),
                    "rating": info.get("rating", ""),
                    "poster": info.get("poster", "")
                }
                writer.writerow(row)
