import tkinter as tk
from tkinter import messagebox, simpledialog
from enum import Enum
from datetime import datetime
import json
import os


class NoteCategory(Enum):
    """
    Заметки.
    """
    WORK = "Работа"
    HOME = "Дом"
    HEALTH = "Здоровье и Спорт"
    PEOPLE = "Люди"
    DOCUMENTS = "Документы"
    FINANCE = "Финансы"
    MISC = "Разное"


class Note:
    """
    Класс, описывающий структуру заметки.

    Атрибуты:
        title (str): Название заметки (не более 50 символов).
        category (NoteCategory): Категория, к которой относится заметка.
        content (str): Содержимое заметки.
        created_at (datetime): Дата и время создания заметки.
        updated_at (datetime): Дата и время последнего обновления заметки.
    """

    def __init__(self, heading="Без названия", category=NoteCategory.MISC, content_body=""):
        """
        Инициализирует экземпляр заметки с заданными параметрами.
        """
        self.title = heading[:50]  # Ограничиваем длину названия 50 символами.
        self.category = category
        self.content = content_body
        self.created_at = datetime.now()
        self.updated_at = self.created_at

    def update(self, heading=None, category=None, content_body=None):
        """
        Обновляет текущую заметку новыми данными, если они переданы.

       
        """
        if heading:
            self.title = heading[:50]
        if category:
            self.category = category
        if content_body:
            self.content = content_body
        self.updated_at = datetime.now()

    def to_dict(self):
        """
        Преобразует заметку в словарь для дальнейшей сериализации в JSON.

     
        """
        return {
            "title": self.title,
            "category": self.category.value,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        """
        Восстанавливает заметку из словаря (например, при чтении из JSON).
        """
        note_instance = cls(
            heading=data["title"],
            category=NoteCategory(data["category"]),
            content_body=data["content"]
        )
        note_instance.created_at = datetime.fromisoformat(data["created_at"])
        note_instance.updated_at = datetime.fromisoformat(data["updated_at"])
        return note_instance


class Project:
    """
    Класс для управления коллекцией заметок.
    """

    def __init__(self):
        """Создает пустую коллекцию заметок."""
        self.memo_collection = []

    def add_note(self, note_obj):
        """
        Добавляет новую заметку в коллекцию.

        """
        self.memo_collection.append(note_obj)

    def remove_note_by_index(self, index):
        """
        Удаляет заметку из коллекции по заданному индексу.
        """
        if 0 <= index < len(self.memo_collection):
            del self.memo_collection[index]

    def to_dict(self):
        """
        Преобразует весь проект (коллекцию заметок) в словарь для сериализации.
        """
        return {
            "notes": [n.to_dict() for n in self.memo_collection]
        }

    @classmethod
    def from_dict(cls, data):
        """
        Восстанавливает коллекцию заметок из словаря.
        """
        project_instance = cls()
        project_instance.memo_collection = [
            Note.from_dict(note_data) for note_data in data["notes"]
        ]
        return project_instance


class ProjectManager:
    """
    Класс, обеспечивающий сохранение и загрузку проекта (коллекции заметок) в файл.
    """
    DEFAULT_FILE_PATH = os.path.join(os.path.dirname(__file__), "contacts.json")

    @staticmethod
    def save_project(project):
        """
        Сохраняет проект (коллекцию заметок) в JSON-файл.
        """
        with open(ProjectManager.DEFAULT_FILE_PATH, "w", encoding="utf-8") as file:
            json.dump(project.to_dict(), file, ensure_ascii=False, indent=4)

    @staticmethod
    def load_project():
        """
        Загружает проект (коллекцию заметок) из JSON-файла.
        """
        if os.path.exists(ProjectManager.DEFAULT_FILE_PATH):
            with open(ProjectManager.DEFAULT_FILE_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)
                return Project.from_dict(data)
        return Project()


class NoteApp:
    """
    Основной класс приложения для управления заметками при помощи графического интерфейса на Tkinter.
    """

    def __init__(self, main_window):
        """
        Инициализирует главное окно приложения, загружает проект из файла
        и настраивает пользовательский интерфейс.
        """
        self.main_window = main_window
        self.main_window.title("NoteApp")

        # Загружаем уже существующий проект или создаем новый
        self.current_project = ProjectManager.load_project()
        self.current_note_idx = None

        self._setup_interface()

    def _setup_interface(self):
        """
        Создает элементы интерфейса: список заметок, кнопки CRUD, меню и текстовую область для содержимого.
        """
        self.left_panel = tk.Frame(self.main_window)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)

        self.right_panel = tk.Frame(self.main_window)
        self.right_panel.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Список заметок
        self.notes_listbox = tk.Listbox(self.left_panel)
        self.notes_listbox.pack(fill=tk.BOTH, expand=True)
        self.notes_listbox.bind("<<ListboxSelect>>", self._show_note_content)

        # Кнопки управления заметками
        self.btn_add_note = tk.Button(self.left_panel, text="Add Note", command=self.add_note)
        self.btn_add_note.pack(fill=tk.X)

        self.btn_edit_note = tk.Button(self.left_panel, text="Edit Note", command=self.edit_note)
        self.btn_edit_note.pack(fill=tk.X)

        self.btn_remove_note = tk.Button(self.left_panel, text="Remove Note", command=self.remove_note)
        self.btn_remove_note.pack(fill=tk.X)

        # Метка и текстовое поле для содержимого заметки
        self.label_note_title = tk.Label(self.right_panel, text="Title:", font=("Arial", 14))
        self.label_note_title.pack(anchor=tk.W)

        self.text_note_content = tk.Text(self.right_panel, state=tk.DISABLED, wrap=tk.WORD)
        self.text_note_content.pack(expand=True, fill=tk.BOTH)

        # Меню
        self.menu_bar = tk.Menu(self.main_window)
        self.main_window.config(menu=self.menu_bar)

        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.main_window.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Add Note", command=self.add_note)
        edit_menu.add_command(label="Edit Note", command=self.edit_note)
        edit_menu.add_command(label="Remove Note", command=self.remove_note)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about_info)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)

        self._update_notes_list()

    def _open_note_dialog(self, existing_note=None):
        """
        Открывает диалоговое окно для создания новой заметки или редактирования существующей.
        """
        note_dialog = tk.Toplevel(self.main_window)
        note_dialog.title("Edit Note" if existing_note else "Add Note")

        tk.Label(note_dialog, text="Title:").pack()
        title_input = tk.Entry(note_dialog)
        title_input.pack(fill=tk.X)

        tk.Label(note_dialog, text="Category:").pack()
        category_value = tk.StringVar(value=NoteCategory.MISC.value)
        category_selector = tk.OptionMenu(note_dialog, category_value, *[cat.value for cat in NoteCategory])
        category_selector.pack(fill=tk.X)

        tk.Label(note_dialog, text="Content:").pack()
        text_area = tk.Text(note_dialog, height=10)
        text_area.pack(fill=tk.BOTH, expand=True)

        # Если редактируем, предварительно заполняем поля
        if existing_note:
            title_input.insert(0, existing_note.title)
            category_value.set(existing_note.category.value)
            text_area.insert(1.0, existing_note.content)

        def _save_note():
            heading = title_input.get().strip()
            if not heading:
                messagebox.showerror("Error", "Title cannot be empty!")
                return

            if len(heading) > 50:
                messagebox.showerror("Error", "Title cannot exceed 50 characters!")
                return

            selected_category = NoteCategory(category_value.get())
            note_text = text_area.get(1.0, tk.END).strip()

            if existing_note:
                existing_note.update(
                    heading=heading,
                    category=selected_category,
                    content_body=note_text
                )
            else:
                new_note_instance = Note(
                    heading=heading,
                    category=selected_category,
                    content_body=note_text
                )
                self.current_project.add_note(new_note_instance)

            ProjectManager.save_project(self.current_project)
            self._update_notes_list()
            note_dialog.destroy()

        tk.Button(note_dialog, text="OK", command=_save_note).pack(side=tk.LEFT)
        tk.Button(note_dialog, text="Cancel", command=note_dialog.destroy).pack(side=tk.RIGHT)

    def add_note(self):
        """Открывает диалог для создания новой заметки."""
        self._open_note_dialog()

    def edit_note(self):
        """Открывает диалог для редактирования выбранной заметки."""
        if self.current_note_idx is None:
            messagebox.showwarning("Warning", "No note selected!")
            return
        note_to_edit = self.current_project.memo_collection[self.current_note_idx]
        self._open_note_dialog(note_to_edit)

    def remove_note(self):
        """Удаляет выбранную заметку из коллекции, после запроса подтверждения."""
        if self.current_note_idx is None:
            messagebox.showwarning("Warning", "No note selected!")
            return
        note_to_remove = self.current_project.memo_collection[self.current_note_idx]
        user_confirmation = messagebox.askyesno("Confirm", f"Do you really want to remove this note: {note_to_remove.title}?")
        if user_confirmation:
            self.current_project.remove_note_by_index(self.current_note_idx)
            self.current_note_idx = None
            ProjectManager.save_project(self.current_project)
            self._update_notes_list()

    def _show_note_content(self, event=None):
        """
        Отображает заголовок и содержимое выбранной заметки в текстовой области справа.
        """
        selection = self.notes_listbox.curselection()
        if not selection:
            return

        self.current_note_idx = selection[0]
        note_to_display = self.current_project.memo_collection[self.current_note_idx]

        self.label_note_title.config(text=f"Title: {note_to_display.title}")
        self.text_note_content.config(state=tk.NORMAL)
        self.text_note_content.delete(1.0, tk.END)
        self.text_note_content.insert(1.0, note_to_display.content)
        self.text_note_content.config(state=tk.DISABLED)

    def _update_notes_list(self):
        """
        Обновляет список заметок (Listbox) в левой панели, отражая текущую коллекцию.
        """
        self.notes_listbox.delete(0, tk.END)
        for memo_item in self.current_project.memo_collection:
            self.notes_listbox.insert(tk.END, f"{memo_item.title} ({memo_item.category.value})")

    def _show_about_info(self):
        """Отображает информационное окно с данными о приложении."""
        messagebox.showinfo(
            "About",
            "NoteApp\nVersion 1.0\nDeveloped with Python and Tkinter."
        )


if __name__ == "__main__":
    main_win = tk.Tk()
    app_instance = NoteApp(main_win)
    main_win.mainloop()
