import requests
import os

class MovieApp:
    """
    A class that manages the user interface for movie operations.
    It depends on a storage object that implements the IStorage interface.
    """

    def __init__(self, storage):
        """
        Initialize the MovieApp with a storage object that implements IStorage.

        :param storage: An object implementing the IStorage interface (e.g., StorageJson, StorageCsv).
        """
        self._storage = storage
        self._api_key = "3b23248a"   # Replace with your OMDb API key
        self._api_url = "http://www.omdbapi.com/"

    def run(self):
        """
        Runs the main loop of the application, displaying a menu to the user
        and executing the chosen commands.
        """
        while True:
            self._print_menu()
            command = input("Enter your choice: ").strip()

            if command == "0":
                print("Exiting the app.")
                break
            elif command == "1":
                self._command_list_movies()
            elif command == "2":
                self._command_add_movie()
            elif command == "3":
                self._command_delete_movie()
            elif command == "4":
                self._command_update_movie()
            elif command == "5":
                self._command_movie_stats()
            elif command == "9":
                self._command_generate_website()
            else:
                print("Invalid choice. Try again.")

    def _print_menu(self):
        """
        Prints the menu options for the user.
        """
        print("\n--- Movie App Menu ---")
        print("0. Exit")
        print("1. List movies")
        print("2. Add movie (fetch data from OMDb)")
        print("3. Delete movie")
        print("4. Update movie rating")
        print("5. Show movie stats")
        print("9. Generate website")

    def _command_list_movies(self):
        """
        Lists all the movies from storage.
        """
        movies = self._storage.list_movies()
        if not movies:
            print("No movies found.")
            return

        print("\n--- List of Movies ---")
        for title, info in movies.items():
            print(f"{title} ({info.get('year', 'N/A')}) - "
                  f"Rating: {info.get('rating', 'N/A')} - "
                  f"Poster: {info.get('poster', 'N/A')}")

    def _command_add_movie(self):
        """
        Prompts user for a movie title, fetches data from the OMDb API,
        and adds the movie to storage with Title, Year, Rating, and Poster.
        """
        title = input("Enter the movie title: ").strip()
        if not title:
            print("Title cannot be empty. Operation cancelled.")
            return

        # Fetch movie data from OMDb
        movie_data = self._fetch_movie_data(title)
        if not movie_data:
            # If None or empty, an error was already displayed
            return

        # Extract and parse fields (safely)
        try:
            year = int(movie_data.get("Year", "0"))
        except ValueError:
            year = 0

        try:
            rating = float(movie_data.get("imdbRating", "0"))
        except ValueError:
            rating = 0.0

        poster_url = movie_data.get("Poster", "N/A")
        real_title = movie_data.get("Title", title)

        # Add to storage
        self._storage.add_movie(
            title=real_title,
            year=year,
            rating=rating,
            poster=poster_url
        )

        print(f"Movie '{real_title}' added successfully.")

    def _command_delete_movie(self):
        """
        Prompts user for a movie title and deletes it from storage.
        """
        title = input("Enter the title of the movie to delete: ").strip()
        self._storage.delete_movie(title)
        print(f"Movie '{title}' deleted (if it existed).")

    def _command_update_movie(self):
        """
        Prompts user for a movie title and a new rating, then updates
        that movie in the storage.
        """
        title = input("Enter the title of the movie to update: ").strip()
        if not title:
            print("Title cannot be empty.")
            return

        new_rating_str = input("Enter the new rating: ").strip()
        if not new_rating_str:
            print("Rating cannot be empty.")
            return

        try:
            new_rating = float(new_rating_str)
        except ValueError:
            print("Rating must be a number.")
            return

        self._storage.update_movie(title, new_rating)
        print(f"Movie '{title}' rating updated (if it existed).")

    def _command_movie_stats(self):
        """
        Calculates and prints simple statistics about the movie collection:
        - Total number of movies
        - Average rating
        - Highest-rated movie
        - Lowest-rated movie
        """
        movies = self._storage.list_movies()
        if not movies:
            print("No movies found. Cannot calculate statistics.")
            return

        ratings = [info["rating"] for info in movies.values() if isinstance(info["rating"], (int, float))]
        if not ratings:
            print("No valid ratings found. Cannot calculate statistics.")
            return

        avg_rating = sum(ratings) / len(ratings)
        max_title = max(movies, key=lambda t: movies[t]["rating"])
        min_title = min(movies, key=lambda t: movies[t]["rating"])

        print("\n--- Movie Statistics ---")
        print(f"Number of Movies: {len(movies)}")
        print(f"Average Rating: {avg_rating:.2f}")
        print(f"Highest Rated: {max_title} ({movies[max_title]['rating']})")
        print(f"Lowest Rated: {min_title} ({movies[min_title]['rating']})")

    def _command_generate_website(self):
        """
        Generates an HTML file (index.html) that displays all movies in a grid.
        Uses the 'index_template.html' file from the '_static' directory.
        """
        movies = self._storage.list_movies()
        if not movies:
            print("No movies found. Website not generated.")
            return

        # Where is your template located? Adjust as needed.
        template_path = os.path.join("_static", "index_template.html")
        if not os.path.exists(template_path):
            print(f"Template file not found: {template_path}")
            return

        # Read the template
        with open(template_path, "r", encoding="utf-8") as f:
            template_html = f.read()

        # Build the <li> items
        movie_items_html = ""
        for title, info in movies.items():
            poster_url = info.get("poster", "")
            year = info.get("year", "N/A")
            movie_items_html += f"""
            <li>
                <div class="movie">
                    <img class="movie-poster" src="{poster_url}" alt="Poster">
                    <div class="movie-title">{title}</div>
                    <div class="movie-year">{year}</div>
                </div>
            </li>
            """

        # Insert items into template
        final_html = template_html.replace("{{MOVIES}}", movie_items_html)

        # Save the result to index.html
        output_path = "index.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_html)

        print("Website was generated successfully.")

    def _fetch_movie_data(self, title):
        """
        Internal helper to fetch movie data from OMDb by title.
        Returns the JSON (dict) from OMDb if found, otherwise None.
        Handles connection errors and 'movie not found' responses gracefully.
        """
        try:
            params = {"t": title, "apikey": self._api_key}
            response = requests.get(self._api_url, params=params, timeout=5)
            response.raise_for_status()  # Raise for 4xx/5xx errors
        except requests.exceptions.RequestException as e:
            print(f"Error: Could not connect to OMDb API ({e}).")
            return None

        data = response.json()

        if data.get("Response") == "False":
            # OMDb returns {"Response": "False", "Error": "..."} if not found
            print(f"Movie not found in OMDb for title '{title}'.")
            return None

        return data
