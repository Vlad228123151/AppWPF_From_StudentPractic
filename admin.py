import tkinter as tk
from tkinter import messagebox, simpledialog
from database import Database

class AdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Авторизация Администратора")
        self.root.geometry("300x150")

        # Поля для логина и пароля
        self.username = tk.StringVar()
        self.password = tk.StringVar()

        # Виджеты
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Логин:").pack(padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.username).pack(padx=10, pady=5)

        tk.Label(self.root, text="Пароль:").pack(padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.password, show="*").pack(padx=10, pady=5)

        tk.Button(self.root, text="Войти", command=self.login).pack(pady=10)

    def login(self):
        # Проверяем логин и пароль
        db = Database()
        query = "SELECT * FROM users WHERE username=%s AND password=%s"
        result = db.fetch_all(query, (self.username.get(), self.password.get()))

        if result:
            messagebox.showinfo("Успех", "Добро пожаловать, Админ!")
            self.open_admin_panel(db)
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def open_admin_panel(self, db):
        # Окно администрирования для добавления и редактирования вычетов
        admin_panel = tk.Toplevel(self.root)
        admin_panel.title("Панель администратора")
        admin_panel.geometry("400x300")

        # Список доступных вычетов из базы данных
        self.deductions_listbox = tk.Listbox(admin_panel)
        self.deductions_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Инициализация self.deductions как пустого словаря
        self.deductions = {}

        # Заполняем Listbox и self.deductions
        self.update_deductions_listbox(db)

        # Кнопки для редактирования и добавления вычетов
        add_button = tk.Button(admin_panel, text="Добавить вычет", command=lambda: self.add_deduction(db))
        add_button.pack(side=tk.LEFT, padx=10, pady=10)

        edit_button = tk.Button(admin_panel, text="Редактировать вычет", command=lambda: self.edit_deduction(db))
        edit_button.pack(side=tk.LEFT, padx=10, pady=10)

        delete_button = tk.Button(admin_panel, text="Удалить вычет", command=lambda: self.delete_deduction(db))
        delete_button.pack(side=tk.LEFT, padx=10, pady=10)

    def add_deduction(self, db):
        # Добавление нового вычета
        deduction_name = simpledialog.askstring("Добавить вычет", "Введите название вычета:")

        # Проверка, что название вычета введено и не состоит только из пробелов
        if deduction_name is None or deduction_name.strip() == "":
            messagebox.showwarning("Предупреждение", "Название вычета должно быть заполнено.")
            return

        deduction_amount = simpledialog.askinteger("Сумма вычета", "Введите сумму вычета:")
        if deduction_amount is None:
            messagebox.showwarning("Предупреждение", "Сумма вычета должна быть введена.")
            return

        db.execute_query("INSERT INTO deductions (name, amount) VALUES (%s, %s)", (deduction_name, deduction_amount))
        messagebox.showinfo("Успех", f"Вычет '{deduction_name}' добавлен.")
        self.update_deductions_listbox(db)

    def edit_deduction(self, db):
        # Проверяем, что пользователь выбрал элемент в Listbox
        selected_deduction = self.deductions_listbox.curselection()
        if not selected_deduction:
            messagebox.showerror("Ошибка", "Выберите вычет для редактирования.")
            return

        # Получаем индекс выбранного элемента
        selected_deduction_index = selected_deduction[0]

        # Получаем название вычета из Listbox
        selected_deduction_name = list(self.deductions.keys())[selected_deduction_index]

        # Запрашиваем новую сумму для вычета
        new_amount = simpledialog.askinteger("Редактировать вычет",
                                             f"Введите новую сумму для '{selected_deduction_name}':")
        if new_amount is not None:
            # Обновляем вычет в базе данных
            db.execute_query("UPDATE deductions SET amount=%s WHERE name=%s", (new_amount, selected_deduction_name))

            # Обновляем Listbox
            self.update_deductions_listbox(db)
            messagebox.showinfo("Успех", f"Сумма вычета '{selected_deduction_name}' изменена.")
    def delete_deduction(self, db):
        # Удаление выбранного вычета
        selected_deduction = self.deductions_listbox.curselection()
        if not selected_deduction:
            messagebox.showerror("Ошибка", "Выберите вычет для удаления.")
            return

        selected_deduction_index = selected_deduction[0]
        selected_deduction_name = list(self.deductions.keys())[selected_deduction_index]
        db.execute_query("DELETE FROM deductions WHERE name=%s", (selected_deduction_name,))
        self.update_deductions_listbox(db)
        messagebox.showinfo("Успех", f"Вычет '{selected_deduction_name}' удален.")

    def update_deductions_listbox(self, db):
        # Создаем или обновляем атрибут self.deductions
        self.deductions = {}

        # Очищаем Listbox
        self.deductions_listbox.delete(0, tk.END)

        # Запрашиваем вычеты из базы данных
        deductions = db.fetch_all("SELECT * FROM deductions")

        # Заполняем Listbox и словарь self.deductions
        for deduction in deductions:
            self.deductions[deduction[1]] = deduction[2]  # {name: amount}
            self.deductions_listbox.insert(tk.END, f"{deduction[1]} - {deduction[2]} Р")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()