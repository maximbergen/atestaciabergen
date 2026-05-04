import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker - Менеджер прочитанных книг")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # Файл для сохранения данных
        self.data_file = "books.json"
        self.books = []
        
        # Загрузка сохраненных данных
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление таблицы
        self.refresh_table()
    
    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Фрейм для ввода данных
        input_frame = ttk.LabelFrame(main_frame, text="Добавление новой книги", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Поля ввода
        ttk.Label(input_frame, text="Название книги:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(input_frame, text="Автор:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.author_entry = ttk.Entry(input_frame, width=30)
        self.author_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(input_frame, text="Жанр:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.genre_entry = ttk.Entry(input_frame, width=30)
        self.genre_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(input_frame, text="Количество страниц:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.pages_entry = ttk.Entry(input_frame, width=30)
        self.pages_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Кнопка добавления
        add_btn = ttk.Button(input_frame, text="Добавить книгу", command=self.add_book)
        add_btn.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация", padding="10")
        filter_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Фильтр по жанру
        ttk.Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.genre_filter = ttk.Combobox(filter_frame, values=["Все"], width=27)
        self.genre_filter.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.genre_filter.set("Все")
        self.genre_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh_table())
        
        # Фильтр по страницам
        ttk.Label(filter_frame, text="Фильтр по страницам:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.pages_filter_var = tk.StringVar(value="Все")
        pages_filter_frame = ttk.Frame(filter_frame)
        pages_filter_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Radiobutton(pages_filter_frame, text="Все", variable=self.pages_filter_var, 
                       value="Все", command=self.refresh_table).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(pages_filter_frame, text="Меньше 200", variable=self.pages_filter_var, 
                       value="Меньше 200", command=self.refresh_table).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(pages_filter_frame, text="Больше 200", variable=self.pages_filter_var, 
                       value="Больше 200", command=self.refresh_table).pack(side=tk.LEFT, padx=5)
        
        # Кнопки управления
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(control_frame, text="Удалить выбранную", command=self.delete_book).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Сохранить в JSON", command=self.save_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Загрузить из JSON", command=self.load_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Очистить фильтры", command=self.clear_filters).pack(side=tk.LEFT, padx=5)
        
        # Таблица для отображения книг
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Создание Treeview
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Название", "Автор", "Жанр", "Страницы"), 
                                 show="headings", height=15)
        
        # Настройка колонок
        self.tree.heading("ID", text="ID")
        self.tree.heading("Название", text="Название")
        self.tree.heading("Автор", text="Автор")
        self.tree.heading("Жанр", text="Жанр")
        self.tree.heading("Страницы", text="Страницы")
        
        self.tree.column("ID", width=50)
        self.tree.column("Название", width=250)
        self.tree.column("Автор", width=200)
        self.tree.column("Жанр", width=150)
        self.tree.column("Страницы", width=100)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Настройка веса для расширения
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
    
    def validate_input(self, title, author, genre, pages):
        """Проверка корректности ввода"""
        if not title or not title.strip():
            messagebox.showerror("Ошибка", "Название книги не может быть пустым!")
            return False
        
        if not author or not author.strip():
            messagebox.showerror("Ошибка", "Автор не может быть пустым!")
            return False
        
        if not genre or not genre.strip():
            messagebox.showerror("Ошибка", "Жанр не может быть пустым!")
            return False
        
        if not pages or not pages.strip():
            messagebox.showerror("Ошибка", "Количество страниц не может быть пустым!")
            return False
        
        try:
            pages_num = int(pages)
            if pages_num <= 0:
                messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть числом!")
            return False
        
        return True
    
    def add_book(self):
        """Добавление новой книги"""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages = self.pages_entry.get().strip()
        
        if not self.validate_input(title, author, genre, pages):
            return
        
        # Создание новой книги
        book = {
            "id": len(self.books) + 1,
            "title": title,
            "author": author,
            "genre": genre,
            "pages": int(pages),
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.books.append(book)
        self.clear_input_fields()
        self.update_genre_filter()
        self.refresh_table()
        messagebox.showinfo("Успех", f"Книга '{title}' успешно добавлена!")
    
    def clear_input_fields(self):
        """Очистка полей ввода"""
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)
    
    def delete_book(self):
        """Удаление выбранной книги"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите книгу для удаления!")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту книгу?"):
            # Получение ID книги из таблицы
            book_id = int(self.tree.item(selected_item[0])['values'][0])
            # Удаление из списка
            self.books = [book for book in self.books if book['id'] != book_id]
            # Перенумерация ID
            for i, book in enumerate(self.books, 1):
                book['id'] = i
            
            self.update_genre_filter()
            self.refresh_table()
            messagebox.showinfo("Успех", "Книга успешно удалена!")
    
    def filter_books(self):
        """Фильтрация книг"""
        filtered_books = self.books.copy()
        
        # Фильтр по жанру
        selected_genre = self.genre_filter.get()
        if selected_genre != "Все":
            filtered_books = [book for book in filtered_books if book['genre'] == selected_genre]
        
        # Фильтр по страницам
        pages_filter = self.pages_filter_var.get()
        if pages_filter == "Меньше 200":
            filtered_books = [book for book in filtered_books if book['pages'] < 200]
        elif pages_filter == "Больше 200":
            filtered_books = [book for book in filtered_books if book['pages'] > 200]
        
        return filtered_books
    
    def refresh_table(self):
        """Обновление таблицы"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получение отфильтрованных книг
        filtered_books = self.filter_books()
        
        # Добавление книг в таблицу
        for book in filtered_books:
            self.tree.insert("", tk.END, values=(
                book['id'],
                book['title'],
                book['author'],
                book['genre'],
                book['pages']
            ))
    
    def update_genre_filter(self):
        """Обновление списка жанров в фильтре"""
        genres = list(set([book['genre'] for book in self.books]))
        genres.sort()
        self.genre_filter['values'] = ["Все"] + genres
        if self.genre_filter.get() not in self.genre_filter['values']:
            self.genre_filter.set("Все")
    
    def clear_filters(self):
        """Очистка фильтров"""
        self.genre_filter.set("Все")
        self.pages_filter_var.set("Все")
        self.refresh_table()
    
    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.books, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", f"Данные успешно сохранены в файл '{self.data_file}'!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении данных: {str(e)}")
    
    def load_data(self):
        """Загрузка данных из JSON файла"""
        if not os.path.exists(self.data_file):
            return
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                loaded_books = json.load(f)
            
            if loaded_books:
                self.books = loaded_books
                self.update_genre_filter()
                self.refresh_table()
                messagebox.showinfo("Успех", f"Данные успешно загружены из файла '{self.data_file}'!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке данных: {str(e)}")

def main():
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()