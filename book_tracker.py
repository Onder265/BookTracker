import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

DATA_FILE = "books.json"


class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker")
        self.root.geometry("800x500")

        # Данные
        self.books = []
        self.load_data()

        # Виджеты ввода
        input_frame = ttk.LabelFrame(root, text="Добавить книгу", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5)
        self.title_entry = ttk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Автор:").grid(row=0, column=2, padx=5, pady=5)
        self.author_entry = ttk.Entry(input_frame, width=20)
        self.author_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Жанр:").grid(row=1, column=0, padx=5, pady=5)
        self.genre_entry = ttk.Entry(input_frame, width=20)
        self.genre_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Страниц:").grid(row=1, column=2, padx=5, pady=5)
        self.pages_entry = ttk.Entry(input_frame, width=10)
        self.pages_entry.grid(row=1, column=3, padx=5, pady=5)

        add_btn = ttk.Button(input_frame, text="Добавить книгу", command=self.add_book)
        add_btn.grid(row=2, column=0, columnspan=4, pady=10)

        # Фильтры
        filter_frame = ttk.LabelFrame(root, text="Фильтры", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, padx=5)
        self.genre_filter = ttk.Entry(filter_frame, width=20)
        self.genre_filter.grid(row=0, column=1, padx=5)
        self.genre_filter.bind("<KeyRelease>", self.apply_filters)

        ttk.Label(filter_frame, text="Страниц >").grid(row=0, column=2, padx=5)
        self.pages_filter = ttk.Entry(filter_frame, width=8)
        self.pages_filter.grid(row=0, column=3, padx=5)
        self.pages_filter.bind("<KeyRelease>", self.apply_filters)

        reset_btn = ttk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters)
        reset_btn.grid(row=0, column=4, padx=20)

        # Таблица
        columns = ("Название", "Автор", "Жанр", "Страниц")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Кнопки управления
        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="Удалить выбранную", command=self.delete_book).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Сохранить в JSON", command=self.save_data).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Загрузить из JSON", command=self.load_data).pack(side="left", padx=5)

        self.refresh_table()

    def add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages_str = self.pages_entry.get().strip()

        if not title or not author or not genre or not pages_str:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        try:
            pages = int(pages_str)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть положительным целым числом!")
            return

        self.books.append({
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        })

        # Очистка полей
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)

        self.refresh_table()

    def delete_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите книгу для удаления")
            return

        # Получаем название выбранной книги
        item = self.tree.item(selected[0])
        title = item["values"][0]

        for book in self.books:
            if book["title"] == title:
                self.books.remove(book)
                break

        self.refresh_table()

    def apply_filters(self, event=None):
        self.refresh_table()

    def reset_filters(self):
        self.genre_filter.delete(0, tk.END)
        self.pages_filter.delete(0, tk.END)
        self.refresh_table()

    def get_filtered_books(self):
        genre_filter = self.genre_filter.get().strip().lower()
        pages_filter_str = self.pages_filter.get().strip()

        filtered = self.books[:]

        if genre_filter:
            filtered = [b for b in filtered if genre_filter in b["genre"].lower()]

        if pages_filter_str:
            try:
                min_pages = int(pages_filter_str)
                filtered = [b for b in filtered if b["pages"] > min_pages]
            except ValueError:
                pass  # игнорируем нечисловой ввод

        return filtered

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for book in self.get_filtered_books():
            self.tree.insert("", tk.END, values=(
                book["title"],
                book["author"],
                book["genre"],
                book["pages"]
            ))

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные сохранены в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.books = json.load(f)
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()
