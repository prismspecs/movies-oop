import json
import os
from istorage import IStorage

class StorageJson(IStorage):

    def __init__(self, file_path):
        """
        :param file_path: Path to the JSON file where movie data is stored.
        """
        self.file_path = file_path

    def list_movies(self):
        """
        Load and return the entire dictionary of movies from the JSON file.
        If the file doesn't exist or is invalid, return an empty dict.
        """
        movies = self._load_data()
        return movies

    def add_movie(self, title, year, rating, poster):
        """
        Add a new movie to the JSON file.
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
        Delete a movie by its title key.
        """
        movies = self._load_data()
        if title in movies:
            del movies[title]
        self._save_data(movies)

    def update_movie(self, title, rating):
        """
        Update the rating of an existing movie.
        """
        movies = self._load_data()
        if title in movies:
            movies[title]["rating"] = rating
        self._save_data(movies)

    def _load_data(self):
        """
        Internal helper method to load movie data from the JSON file.
        Returns an empty dictionary if the file doesn't exist or the JSON is invalid.
        """
        if not os.path.exists(self.file_path):
            return {}

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_data(self, data):
        """
        Internal helper method to save the dictionary of movies back to the JSON file.
        """
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
