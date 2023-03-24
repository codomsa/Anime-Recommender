import json
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO
import requests
from random import choice
import webbrowser


class AnimeApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("UWU recommendation bot")
        self.geometry("1600x900")
        self.config(bg="#f5f5f5")

        self.anime_url = ""

        self.genre_label = ttk.Label(self, text="Select genre:")
        self.genre_label.place(relx=0.5, rely=0.11, anchor=tk.CENTER)

        self.genre_combobox = ttk.Combobox(self, values=["Action", "Adventure", "Comedy", "Drama", "Slice of Life", "Fantasy", "Magic", "Supernatural", "Horror", "Mystery", "Psychological", "Romance", "Sci-Fi", "Sports", "Tragedy", "Ecchi", "Hentai"])
        self.genre_combobox.place(relx=0.46, rely=0.15, anchor=tk.CENTER)

        self.search_button = ttk.Button(self, text="Search", command=self.update_anime_info)
        self.search_button.place(relx=0.54, rely=0.15, anchor=tk.CENTER)

        self.title_frame = tk.Frame(self, bg="#f5f5f5", bd=1, relief="solid")
        self.title_label = ttk.Label(self.title_frame, text="", wraplength=600, font=("Arial", 16))

        self.synopsis_text = tk.Text(self, wrap=tk.WORD, height=10, width=75, bg="#f5f5f5", bd=0)
        self.synopsis_text.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        self.rating_label = ttk.Label(self, text="")
        self.rating_label.place(relx=0.5, rely=0.65, anchor=tk.CENTER)

        self.anime_image_label = ttk.Label(self)
        self.anime_image_label.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

        self.read_more_button = ttk.Button(self, text="Read more", command=self.toggle_synopsis)
        self.read_more_button.place(relx=0.46, rely=0.58, anchor=tk.CENTER)
        self.read_more_button.place_forget()
        self.is_collapsed = True

        self.visit_anilist_button = ttk.Button(self, text="Visit Anilist", command=self.open_anilist_page)
        self.visit_anilist_button.place(relx=0.54, rely=0.58, anchor=tk.CENTER)
        self.visit_anilist_button.place_forget()

    def open_anilist_page(self):
        webbrowser.open(self.anime_url)

    def toggle_synopsis(self):
        if self.is_collapsed:
            self.synopsis_text.config(height=self.full_line_count)
            self.read_more_button.config(text="Read less")
            self.is_collapsed = False
        else:
            self.synopsis_text.config(height=10)
            self.read_more_button.config(text="Read more")
            self.is_collapsed = True

    def update_anime_info(self):
        genre = self.genre_combobox.get()
        anime = get_random_anime(genre)

        self.anime_url = anime['url']
        self.title_label.config(text=f"{anime['title']['romaji']}")
        self.title_label.pack(fill=tk.BOTH, padx=10, pady=10)
        self.title_frame.place(relx=0.5, rely=0.25, anchor=tk.CENTER)
        self.synopsis_text.delete(1.0, tk.END)
        self.full_synopsis = anime['description']
        self.synopsis_text.insert(tk.END, self.full_synopsis)
        self.full_line_count = int(self.synopsis_text.index(tk.END).split('.')[0]) - 1
        if not self.is_collapsed:
            self.toggle_synopsis()

        rating = anime['averageScore']
        if rating >= 90:
            color = "dark purple"
        elif rating >= 86:
            color = "purple"
        elif rating >= 76:
            color = "blue"
        elif rating >= 65:
            color = "green"
        elif rating >= 50:
            color = "orange"
        elif rating >= 35:
            color = "red"
        else:
            color = "red"

        self.rating_label.config(text=f"Rating: {rating}%", foreground=color)

        img_url = anime['coverImage']['large']
        img_data = requests.get(img_url).content

        image = Image.open(BytesIO(img_data))
        image.thumbnail((200, 200))
        photo = ImageTk.PhotoImage(image)

        self.anime_image_label.config(image=photo)
        self.anime_image_label.image = photo

        self.read_more_button.place(relx=0.46, rely=0.58, anchor=tk.CENTER)
        self.visit_anilist_button.place(relx=0.54, rely=0.58, anchor=tk.CENTER)


def get_random_anime(genre):
    query = '''
    query ($genre: String) {
      Page(perPage: 50) {
        media(genre: $genre, sort: POPULARITY_DESC, type: ANIME) {
          id
          title {
            romaji
          }
          description
          averageScore
          coverImage {
            large
          }
          siteUrl
        }
      }
    }
    '''

    variables = {
        "genre": genre
    }

    url = "https://graphql.anilist.co"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)

    if response.status_code == 200:
        anime_data = json.loads(response.text)
        anime_list = anime_data['data']['Page']['media']
        random_anime = choice(anime_list)
        random_anime["url"] = random_anime["siteUrl"]
        return random_anime
    else:
        raise Exception(f"Error: {response.status_code}")


if __name__ == "__main__":
    app = AnimeApp()
    app.mainloop()