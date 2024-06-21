import hashlib
import sys
from PyQt5.QtCore import QFile, QTextStream, Qt, QDate
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QDateEdit, QDesktopWidget, QMessageBox


class MainWindow(QMainWindow):

    def __init__(self):

        # Вызов конструктора родительского класса QMainWindow.
        super().__init__()

        # Заголовок окна.
        self.setWindowTitle("Генерация кода зачетной книжки")
        # Размер окна.
        self.setFixedSize(600, 400)

        # Отключение возможности изменения размера окна.
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

        # Создание центрального виджета.
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Загрузка стилей из CSS файла.
        self.load_stylesheet("styles.css")

        # Создание основного вертикального контейнера для центрального виджета.
        main_layout = QVBoxLayout(central_widget)
        main_layout.setObjectName("main_widget")

        title_label = QLabel("ВВЕДИТЕ ДАННЫЕ СТУДЕНТА", self)
        title_label.setObjectName("title_label")
        main_layout.addWidget(title_label)

        # Форма для ввода данных.
        self.form_layout = QFormLayout()
        self.form_layout.setObjectName("form_layout")

        labels = ["Фамилия:", "Имя:", "Отчество:", "Дата рождения:", "Номер группы:"]
        self.line_edits = {}

        for text in labels:
            label = QLabel(text, self)
            # Условие для создания QLineEdit или QDateEdit в зависимости от текста метки
            edit_widget = QLineEdit() if text != "Дата рождения:" else QDateEdit()
            self.line_edits[text] = edit_widget
            self.form_layout.addRow(label, edit_widget)
            label.setObjectName("line_edit" if text != "Дата рождения:" else "date_edit")

        main_layout.addLayout(self.form_layout)

        # Кнопки "Сгенерировать код" и "Очистить поля".
        button_layout = QHBoxLayout()
        generate_button = QPushButton("Сгенерировать код", self)
        generate_button.setObjectName("generate_button")
        generate_button.clicked.connect(self.generate_code)
        button_layout.addWidget(generate_button)

        clear_button = QPushButton("Очистить поля", self)
        clear_button.setObjectName("clear_button")
        clear_button.clicked.connect(self.clear_fields)
        button_layout.addWidget(clear_button)

        main_layout.addLayout(button_layout)

        # Отображение кода зачетной книжки.
        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.setObjectName("horizontal_layout")

        label_code = QLabel("КОД ЗАЧЁТНОЙ КНИЖКИ:", self)
        label_code.setObjectName("label_code")
        self.horizontal_layout.addWidget(label_code)

        self.generated_code_label = QLabel("00000000", self)
        self.generated_code_label.setObjectName("generated_code_label")
        self.generated_code_label.setAlignment(Qt.AlignCenter)
        self.horizontal_layout.addWidget(self.generated_code_label)

        main_layout.addLayout(self.horizontal_layout)

        # Открытие окна по центру экрана.
        self.center()

    # Метод для открытия окна по центру экрана.
    def center(self):
        # Получаем геометрию главного экрана
        screen_geo = QDesktopWidget().screenGeometry()

        # Получаем геометрию окна приложения
        window_geo = self.geometry()

        # Центрируем окно относительно главного экрана
        x = int((screen_geo.width() - window_geo.width()) / 2)
        y = int((screen_geo.height() - window_geo.height()) / 2)

        self.move(x, y)

    # Метод для загрузки стилей из CSS файла.
    def load_stylesheet(self, path):

        style_file = QFile(path)
        style_file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(style_file)
        self.setStyleSheet(stream.readAll())

    # Метод очистки полей ввода.
    def clear_fields(self):
        for line_edit in self.line_edits.values():
            if isinstance(line_edit, QDateEdit):
                line_edit.setDate(QDate(2000, 1, 1))
            else:
                line_edit.clear()
        self.generated_code_label.setText("--------")

    # Метод для проверки ввода в поля ФИО.
    def check_fio(self, surname, name, middle_name):
        # Проверка, что поля ФИО содержат только буквы
        if not all(word.isalpha() for word in [surname, name, middle_name]):
            QMessageBox.critical(self, "Ошибка", "Поля ФИО должны состоять только из букв.")
            return False

        # Проверка, что поля ФИО не содержат пробелов
        if any(' ' in word for word in [surname, name, middle_name]):
            QMessageBox.critical(self, "Ошибка", "Поля ФИО не должны содержать пробелы.")
            return False

        return True

    # Метод для проверки ввода в поле Дата рождения.
    def check_birth_date(self, birth_date):
        # Проверка, что дата рождения не позже текущей даты
        current_date = QDate.currentDate()
        if birth_date > current_date:
            QMessageBox.critical(self, "Ошибка", "Дата рождения не может быть позже текущей даты.")
            return False

        return True

    # Метод для проверки ввода в поле Номер группы.
    def check_group_number(self, group_number):
        # Проверка, что номер группы состоит только из цифр
        if not group_number.isdigit():
            QMessageBox.critical(self, "Ошибка", "Номер группы должен быть целым числом.")
            return False

        return True

    def custom_hash(self, data_string):

        # Суммируем ASCII-коды всех символов строки - сумма не будет уникальной, но даст начальное значение для преобразования.
        total = sum(ord(char) for char in data_string)

        # Добавляем преобразования для усложнения алгоритма.
        # Использование чисел и букв для создания хеша уменьшает вероятность коллизий и увеличивает вариативность хешей.
        code_part1 = ''
        while total > 0:
            char = total % 36
            if char < 10:
                code_part1 += chr(char + 48)  # Цифры 0-9
            else:
                code_part1 += chr(char + 55)  # Буквы A-Z
            total //= 36

        # Дополнительные преобразования
        # Умножение ASCII-кодов символов на их позиции и взятие по модулю 256
        # обеспечивает более сложное и распределенное значение, что уменьшает вероятность коллизий.
        transformed = ''.join(chr((ord(char) * (i + 1)) % 256) for i, char in enumerate(data_string))

        # Это значение используется для создания второй части хеша, что добавляет дополнительную уникальность.
        total2 = sum(ord(char) for char in transformed)
        code_part2 = ''

        # Преобразования для второй части хеша.
        while total2 > 0:
            char = total2 % 36
            if char < 10:
                code_part2 += chr(char + 48)  # Цифры 0-9
            else:
                code_part2 += chr(char + 55)  # Буквы A-Z
            total2 //= 36

        # Соединяем оба результата и добираем до 8 символов
        final_code = (code_part1 + code_part2).upper()
        if len(final_code) < 8:
            final_code += '0' * (8 - len(final_code))
        else:
            final_code = final_code[:8]

        return final_code

    # Метод для генерации кода зачётной книжки по введенным данным.
    def generate_code(self):
        # Получение содержимого полей ввода.
        surname = self.line_edits["Фамилия:"].text().strip()
        name = self.line_edits["Имя:"].text().strip()
        middle_name = self.line_edits["Отчество:"].text().strip()
        birth_date = self.line_edits["Дата рождения:"].date()
        group_number = self.line_edits["Номер группы:"].text().strip()

        # Проверки на корректность пользовательского ввода полей.
        if not self.check_fio(surname, name, middle_name):
            return

        if not self.check_birth_date(birth_date):
            return

        if not self.check_group_number(group_number):
            return

        # Собираем все необходимые данные в одну строку.
        data_string = f"{surname} {name} {middle_name} {birth_date.toString('yyyy-MM-dd')} {group_number}"

        # Создаем уникальный код на основе ASCII-кодов символов и их преобразований.
        code = self.custom_hash(data_string)

        # Формируем итоговый код зачетной книжки.
        generated_code = f"{code}"

        # Отображение кода в окне приложения.
        self.generated_code_label.setText(generated_code)

        # Отображение кода в окне приложения.
        self.generated_code_label.setText(generated_code)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
