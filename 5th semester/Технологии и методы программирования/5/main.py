# -*- coding: utf-8 -*-
"""
Лабораторная: «Шифровка решёткой (Кардано)» и «Шифр перестановки Скитала».
GUI: tkinter. Python 3.9+ (Windows/macOS/Linux). Внешние пакеты не требуются.

Новое:
- Меню «Правка» (Вырезать/Копировать/Вставить/Выделить всё/Очистить).
- Горячие клавиши: Ctrl/⌘ + C/V/X/A.
- Контекстное меню правой кнопкой в текстовых полях (вход/результат).

Остальное:
- Шифрование/дешифрование обоими методами.
- Автоопределение: если вставленный текст похож на уже зашифрованный выбранным методом,
  программа предложит «Расшифровать» или «Зашифровать повторно».
- Работа с файлами, примерами, настройкой ключей (для решётки — импорт/экспорт JSON).
"""

import json
import platform
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

IS_MAC = (platform.system() == "Darwin")

# ----------------------------- УТИЛИТЫ ---------------------------------

RUS_COMMON_WORDS = {
    "и","в","во","не","что","он","на","я","с","со","как","а","то","все","она","так",
    "его","но","да","ты","к","у","же","вы","за","бы","по","ее","мне","есть","для",
    "мы","тебя","их","из","ли","только","моё","мой","моя","меня","это","это","для"
}
RUS_VOWELS = set("аеёиоуыэюяАЕЁИОУЫЭЮЯ")
CYR = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя") | set("АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")

def russian_natural_score(text: str) -> float:
    """Очень простая эвристика «насколько похоже на нормальный русский текст»."""
    if not text:
        return 0.0
    total = len(text)
    cyr_count = sum(1 for ch in text if ch in CYR)
    vowels = sum(1 for ch in text if ch in RUS_VOWELS)
    spaces = text.count(" ")
    punct = sum(1 for ch in text if ch in ",.?!:;—-()\"«»")
    words = [w.strip(".,!?;:()\"«»") for w in text.lower().split()]
    common_hits = sum(1 for w in words if w in RUS_COMMON_WORDS)

    score = 0.0
    score += 1.0 * (cyr_count / total)
    letters = sum(1 for ch in text if ch.isalpha())
    if letters:
        score += 0.7 * (vowels / letters)
    score += 0.3 * (spaces / max(1, total/6))
    score += 0.3 * (punct / max(1, total/20))
    score += 0.6 * (common_hits / max(1, len(words)))
    return min(score / 3.0, 1.0)

# ----------------------------- СКИТАЛА ---------------------------------

def skytale_encrypt(text: str, rows: int, filler: str = "¤") -> str:
    if rows <= 1:
        return text
    n = len(text)
    cols = (n + rows - 1) // rows
    padded = text + (filler * (rows * cols - n))
    grid = [list(padded[i*cols:(i+1)*cols]) for i in range(rows)]
    out = []
    for c in range(cols):
        for r in range(rows):
            out.append(grid[r][c])
    return "".join(out)

def skytale_decrypt(cipher: str, rows: int, filler: str = "¤") -> str:
    if rows <= 1:
        return cipher
    n = len(cipher)
    cols = (n + rows - 1) // rows
    grid = [[""] * cols for _ in range(rows)]
    it = iter(cipher)
    for c in range(cols):
        for r in range(rows):
            grid[r][c] = next(it, filler)
    out = "".join("".join(row) for row in grid)
    return out.rstrip(filler)

# --------------------------- РЕШЁТКА (КАРДАНО) --------------------------

def rotate_coords(coords, n):
    """Поворот координат на 90° по часовой, индексация 0..n-1."""
    return [(c, n-1-r) for (r, c) in coords]

def validate_grille(coords, n):
    """Проверить, что при 4 поворотах покрываются все n*n клетки ровно один раз."""
    used = set()
    cur = list(coords)
    for _ in range(4):
        for cell in cur:
            if cell in used:
                return False
            used.add(cell)
        cur = rotate_coords(cur, n)
    return len(used) == n * n

# ✅ Корректная решётка 4×4: на 4 поворотах покрывает все 16 клеток единожды
DEFAULT_GRILLE = {
    "n": 4,
    "holes": [(0,0), (0,1), (0,2), (1,1)]
}
assert validate_grille(DEFAULT_GRILLE["holes"], DEFAULT_GRILLE["n"]), "Встроенная решётка некорректна!"

def grille_encrypt(text: str, grille: dict, filler: str = "¤") -> str:
    n = grille["n"]
    holes = grille["holes"]
    if not validate_grille(holes, n):
        raise ValueError("Ключ-решётка некорректен.")
    out = []
    i = 0
    while i < len(text):
        block = text[i:i+n*n]
        if len(block) < n*n:
            block = block + filler * (n*n - len(block))
        grid = [[""] * n for _ in range(n)]
        idx = 0
        cur = list(holes)
        for _ in range(4):
            for (r, c) in cur:
                grid[r][c] = block[idx]
                idx += 1
            cur = rotate_coords(cur, n)
        for r in range(n):
            for c in range(n):
                out.append(grid[r][c])
        i += n*n
    return "".join(out)

def grille_decrypt(cipher: str, grille: dict, filler: str = "¤") -> str:
    n = grille["n"]
    holes = grille["holes"]
    if not validate_grille(holes, n):
        raise ValueError("Ключ-решётка некорректен.")
    out = []
    i = 0
    while i < len(cipher):
        block = cipher[i:i+n*n]
        if len(block) < n*n:
            block = block + filler * (n*n - len(block))
        grid = [[""] * n for _ in range(n)]
        it = iter(block)
        for r in range(n):
            for c in range(n):
                grid[r][c] = next(it)
        cur = list(holes)
        chars = []
        for _ in range(4):
            for (r, c) in cur:
                chars.append(grid[r][c])
            cur = rotate_coords(cur, n)
        out.append("".join(chars))
        i += n*n
    return "".join(out).rstrip(filler)

# ----------------------------- АВТО-ОПРЕДЕЛЕНИЕ -------------------------
AUTO_DIFF_THRESHOLD = 0.03  # порог разницы «натуральности»

def autodetect_mode(method: str, text: str, rows: int = 3, grille: dict = None, filler: str = "¤"):
    """Вернёт ('encrypted'|'plaintext', confidence: 0..1, decrypted_preview)"""
    if not text.strip():
        return ("plaintext", 0.0, "")
    if method == "skytale":
        dec = skytale_decrypt(text, rows, filler=filler)
    elif method == "grille":
        dec = grille_decrypt(text, grille or DEFAULT_GRILLE, filler=filler)
    else:
        return ("plaintext", 0.0, "")
    s_in = russian_natural_score(text)
    s_dec = russian_natural_score(dec)
    if (s_dec - s_in) > AUTO_DIFF_THRESHOLD and s_dec > 0.50:
        return ("encrypted", min(1.0, (s_dec - s_in + 0.5)), dec)
    else:
        return ("plaintext", max(0.0, s_in), dec)

# ----------------------------- GUI -------------------------------------

APP_NAME = "Исторические шифры: Решётка и Скитала"

EXAMPLES = {
    "Короткий (повторы 3–4 букв)": "мама мыла раму! мама-раму? рама, мама; мама: раму.",
    "Разные буквы": "съешь же ещё этих мягких французских булок, да выпей чаю.",
    "Англо-русский": "Hello, мир! Как дела? fine, ok :)",
    "Длиннее": "В криптографии скитала — древнегреческий шифр перестановки, использовавшийся спартанцами."
}

# ---------- общие действия «Правка» и контекстное меню для Text ----------

def get_active_text_widget(root):
    w = root.focus_get()
    return w if isinstance(w, tk.Text) else None

def text_select_all(w: tk.Text):
    w.tag_add("sel", "1.0", "end-1c")
    w.mark_set("insert", "1.0")

def attach_text_edit_bindings(root, text_widget: tk.Text):
    # Горячие клавиши: Ctrl/⌘ + C/V/X/A
    accel = "Command" if IS_MAC else "Control"

    text_widget.bind(f"<{accel}-c>", lambda e: (text_widget.event_generate("<<Copy>>"), "break"))
    text_widget.bind(f"<{accel}-v>", lambda e: (text_widget.event_generate("<<Paste>>"), "break"))
    text_widget.bind(f"<{accel}-x>", lambda e: (text_widget.event_generate("<<Cut>>"), "break"))
    text_widget.bind(f"<{accel}-a>", lambda e: (text_select_all(text_widget), "break"))

    # Контекстное меню (ПКМ)
    ctx = tk.Menu(text_widget, tearoff=0)
    ctx.add_command(label="Вырезать", command=lambda: text_widget.event_generate("<<Cut>>"))
    ctx.add_command(label="Копировать", command=lambda: text_widget.event_generate("<<Copy>>"))
    ctx.add_command(label="Вставить", command=lambda: text_widget.event_generate("<<Paste>>"))
    ctx.add_separator()
    ctx.add_command(label="Выделить всё", command=lambda: text_select_all(text_widget))
    ctx.add_command(label="Очистить", command=lambda: (text_widget.delete("1.0", "end"), None))

    def show_ctx(event):
        try:
            ctx.tk.call("tk_popup", ctx, event.x_root, event.y_root)
        except Exception:
            pass

    # ПКМ: <Button-3> (Win/Linux), на macOS иногда <Button-2>
    text_widget.bind("<Button-3>", show_ctx)
    if IS_MAC:
        text_widget.bind("<Button-2>", show_ctx)

class CipherWindow(tk.Toplevel):
    def __init__(self, master, method: str):
        super().__init__(master)
        self.master_app = master
        self.method = method  # 'skytale' | 'grille'
        self.title(f"{APP_NAME} — {self.title_of_method()}")
        self.geometry("980x700")
        self.minsize(900, 620)

        # Параметры ключей/настроек
        self.filler = tk.StringVar(value="¤")
        self.rows = tk.IntVar(value=3)  # для скиталы
        self.grille = DEFAULT_GRILLE.copy()
        self._last_offer_sig = None  # чтобы не «дёргать» пользователя одним и тем же вопросом

        self._build_ui()

    def title_of_method(self):
        return "Скитала (перестановка)" if self.method == "skytale" else "Решётка (Кардано)"

    def _build_ui(self):
        # Верхняя панель
        top = ttk.Frame(self)
        top.pack(side=tk.TOP, fill=tk.X, padx=10, pady=6)
        ttk.Label(top, text=self.title_of_method(), font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT)

        ttk.Label(top, text="Паддинг:").pack(side=tk.LEFT, padx=(16,4))
        ttk.Entry(top, textvariable=self.filler, width=3, justify="center").pack(side=tk.LEFT)

        if self.method == "skytale":
            ttk.Label(top, text="Рядов:").pack(side=tk.LEFT, padx=(16,4))
            ttk.Spinbox(top, from_=2, to=50, textvariable=self.rows, width=4).pack(side=tk.LEFT)
        else:
            ttk.Label(top, text="Решётка 4×4 (встроена)").pack(side=tk.LEFT, padx=(16,6))
            ttk.Button(top, text="Экспорт ключа…", command=self.export_grille).pack(side=tk.LEFT, padx=2)
            ttk.Button(top, text="Импорт ключа…", command=self.import_grille).pack(side=tk.LEFT, padx=2)

        # Панель действий
        actions = ttk.Frame(self)
        actions.pack(side=tk.TOP, fill=tk.X, padx=10, pady=6)
        ttk.Label(actions, text="Пример:").pack(side=tk.LEFT)
        self.examples_var = tk.StringVar(value=list(EXAMPLES.keys())[0])
        ttk.Combobox(actions, textvariable=self.examples_var,
                     values=list(EXAMPLES.keys()), state="readonly", width=36).pack(side=tk.LEFT, padx=4)
        ttk.Button(actions, text="Вставить", command=self.insert_example).pack(side=tk.LEFT)

        ttk.Button(actions, text="Открыть файл…", command=self.load_file).pack(side=tk.LEFT, padx=(12,2))
        ttk.Button(actions, text="Сохранить результат…", command=self.save_result).pack(side=tk.LEFT, padx=2)

        ttk.Button(actions, text="Автоанализ", command=self.auto_analyze).pack(side=tk.LEFT, padx=(16,4))
        ttk.Button(actions, text="Зашифровать", command=self.encrypt).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions, text="Расшифровать", command=self.decrypt).pack(side=tk.LEFT, padx=2)

        # Индикатор/подсказка
        self.status_var = tk.StringVar(value="Подсказка: вставьте текст — программа подскажет, что сделать.")
        ttk.Label(self, textvariable=self.status_var, foreground="#006699").pack(side=tk.TOP, anchor="w", padx=12)

        # Поля ввода/вывода
        panes = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        panes.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        left = ttk.Frame(panes)
        right = ttk.Frame(panes)
        panes.add(left, weight=1)
        panes.add(right, weight=1)

        ttk.Label(left, text="Входной текст").pack(anchor="w")
        self.input_txt = tk.Text(left, wrap="word", font=("Segoe UI", 11), undo=True, maxundo=-1, autoseparators=True)
        self.input_txt.pack(fill=tk.BOTH, expand=True)
        self.input_txt.bind("<<Modified>>", self.on_input_modified)

        ttk.Label(right, text="Результат").pack(anchor="w")
        self.output_txt = tk.Text(right, wrap="word", font=("Segoe UI", 11), undo=True, maxundo=-1, autoseparators=True)
        self.output_txt.pack(fill=tk.BOTH, expand=True)

        # Подключаем горячие клавиши и контекстные меню к обоим полям
        attach_text_edit_bindings(self, self.input_txt)
        attach_text_edit_bindings(self, self.output_txt)

        # Меню «Правка» в окне алгоритма
        self._install_edit_menu()

    # Меню «Правка»
    def _install_edit_menu(self):
        menubar = tk.Menu(self)
        edit_menu = tk.Menu(menubar, tearoff=0)

        def act(action):
            w = get_active_text_widget(self)
            if not w:
                return
            if action == "cut":
                w.event_generate("<<Cut>>")
            elif action == "copy":
                w.event_generate("<<Copy>>")
            elif action == "paste":
                w.event_generate("<<Paste>>")
            elif action == "select_all":
                text_select_all(w)
            elif action == "clear":
                w.delete("1.0", "end")

        edit_menu.add_command(label="Вырезать", accelerator="Ctrl+X" if not IS_MAC else "⌘X",
                              command=lambda: act("cut"))
        edit_menu.add_command(label="Копировать", accelerator="Ctrl+C" if not IS_MAC else "⌘C",
                              command=lambda: act("copy"))
        edit_menu.add_command(label="Вставить", accelerator="Ctrl+V" if not IS_MAC else "⌘V",
                              command=lambda: act("paste"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Выделить всё", accelerator="Ctrl+A" if not IS_MAC else "⌘A",
                              command=lambda: act("select_all"))
        edit_menu.add_command(label="Очистить", command=lambda: act("clear"))

        menubar.add_cascade(label="Правка", menu=edit_menu)
        self.config(menu=menubar)

    # ----------------- КЛЮЧИ РЕШЁТКИ -----------------

    def export_grille(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")], title="Экспорт ключа-решётки")
        if not path: return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.grille, f, ensure_ascii=False, indent=2)
        messagebox.showinfo(APP_NAME, f"Ключ-решётка сохранён:\n{path}")

    def import_grille(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")], title="Импорт ключа-решётки")
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                g = json.load(f)
            if not isinstance(g, dict) or "n" not in g or "holes" not in g:
                raise ValueError("Формат JSON-ключа неверен.")
            holes = [tuple(map(int, xy)) for xy in g["holes"]]
            if not validate_grille(holes, int(g["n"])):
                raise ValueError("Ключ-решётка некорректна (должна покрывать все клетки за 4 поворота).")
            self.grille = {"n": int(g["n"]), "holes": holes}
            messagebox.showinfo(APP_NAME, "Ключ-решётка импортирован.")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Не удалось импортировать ключ:\n{e}")

    # ----------------- ДЕЙСТВИЯ -----------------

    def insert_example(self):
        self.input_txt.delete("1.0", tk.END)
        self.input_txt.insert("1.0", EXAMPLES[self.examples_var.get()])

    def load_file(self):
        path = filedialog.askopenfilename(title="Открыть файл", filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()
            self.input_txt.delete("1.0", tk.END)
            self.input_txt.insert("1.0", data)
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Ошибка чтения файла:\n{e}")

    def save_result(self):
        data = self.output_txt.get("1.0", tk.END)
        if not data.strip():
            messagebox.showwarning(APP_NAME, "Нет данных для сохранения.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Текстовые файлы", "*.txt")], title="Сохранить результат")
        if not path: return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(data)
            messagebox.showinfo(APP_NAME, f"Результат сохранён:\n{path}")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Ошибка сохранения:\n{e}")

    def read_in(self):
        return self.input_txt.get("1.0", tk.END).rstrip("\n")

    def write_out(self, s: str):
        self.output_txt.delete("1.0", tk.END)
        self.output_txt.insert("1.0", s)

    def auto_analyze(self):
        text = self.read_in()
        if self.method == "skytale":
            m, conf, dec = autodetect_mode("skytale", text, rows=self.rows.get(), filler=self.filler.get())
        else:
            m, conf, dec = autodetect_mode("grille", text, grille=self.grille, filler=self.filler.get())
        if m == "encrypted":
            self.status_var.set(f"Похоже, что это шифртекст выбранного метода (уверенность ~{int(conf*100)}%). "
                                f"Выберите: «Расшифровать» или «Зашифровать повторно».")
        else:
            self.status_var.set("Похоже на открытый текст. Нажмите «Зашифровать» или «Автоанализ».")
        self.write_out(dec)

    def encrypt(self):
        text = self.read_in()
        if self.method == "skytale":
            out = skytale_encrypt(text, self.rows.get(), filler=self.filler.get())
        else:
            out = grille_encrypt(text, self.grille, filler=self.filler.get())
        self.write_out(out)

    def decrypt(self):
        text = self.read_in()
        if self.method == "skytale":
            out = skytale_decrypt(text, self.rows.get(), filler=self.filler.get())
        else:
            out = grille_decrypt(text, self.grille, filler=self.filler.get())
        self.write_out(out)

    def on_input_modified(self, event=None):
        # Сбрасываем флаг изменения
        self.input_txt.edit_modified(0)
        text = self.read_in()
        if not text.strip():
            self.status_var.set("Подсказка: вставьте текст — программа подскажет, что сделать.")
            self._last_offer_sig = None
            return
        # Обновляем подсказку
        if self.method == "skytale":
            m, conf, _ = autodetect_mode("skytale", text, rows=self.rows.get(), filler=self.filler.get())
        else:
            m, conf, _ = autodetect_mode("grille", text, grille=self.grille, filler=self.filler.get())
        if m == "encrypted":
            self.status_var.set(f"Обнаружен шифртекст ({int(conf*100)}%). "
                                f"Можно «Расшифровать» или «Зашифровать повторно».")
            # Автопредложение действия — только один раз для данного текста
            signature = (len(text), text[:64])
            if signature != self._last_offer_sig:
                self._last_offer_sig = signature
                self.offer_action_dialog()
        else:
            self.status_var.set("Похоже на открытый текст. Нажмите «Зашифровать» или «Автоанализ».")
            self._last_offer_sig = None

    def offer_action_dialog(self):
        """Показывает диалог, если текст похож на шифртекст выбранного метода."""
        verb = "Скиталы" if self.method == "skytale" else "решётки Кардано"
        msg = (f"Похоже, что вставленный текст уже зашифрован методом {verb}.\n\n"
               f"Что сделать сейчас?\n"
               f"Да — расшифровать до исходного текста.\n"
               f"Нет — зашифровать повторно (второй раз подряд).\n"
               f"Отмена — ничего не делать.")
        res = messagebox.askyesnocancel(APP_NAME, message=msg, icon="question")
        if res is True:        # Да — расшифровать
            self.decrypt()
        elif res is False:     # Нет — зашифровать ещё раз
            self.encrypt()
        else:
            pass               # Отмена

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("820x480")
        self.minsize(760, 440)
        self._build_home()
        self._install_global_edit_menu()

    def _build_home(self):
        header = ttk.Frame(self, padding=12)
        header.pack(fill=tk.X)
        ttk.Label(header, text=APP_NAME, font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(header, text="Выберите алгоритм. Русский текст и любые символы поддерживаются.").pack(anchor="w", pady=(4,0))

        body = ttk.Frame(self, padding=12)
        body.pack(fill=tk.BOTH, expand=True)

        cards = ttk.Frame(body)
        cards.pack(expand=True)

        self._make_card(cards,
                        "Решётка (Кардано)",
                        "Транспозиционный шифр с «дырчатым трафаретом» и 4 поворотами. "
                        "Встроен корректный ключ 4×4; возможен импорт/экспорт JSON.",
                        lambda: CipherWindow(self, "grille"))

        self._make_card(cards,
                        "Скитала (перестановка)",
                        "Древнегреческий шифр: записываем построчно, читаем по столбцам. "
                        "Ключ — число рядов.",
                        lambda: CipherWindow(self, "skytale"))

        footer = ttk.Frame(self, padding=12)
        footer.pack(fill=tk.X)
        ttk.Label(footer, text="Совет: правый клик в поле текста — контекстное меню, Ctrl/⌘+C/V/X/A работают.").pack(anchor="w")

    def _make_card(self, parent, title, desc, on_open):
        frame = ttk.Labelframe(parent, text=title, padding=12)
        frame.pack(fill=tk.X, pady=8)
        ttk.Label(frame, text=desc, wraplength=700).pack(anchor="w")
        ttk.Button(frame, text=f"Открыть: {title}", command=on_open).pack(anchor="e", pady=6)

    # Глобальное меню «Правка» (на главном окне)
    def _install_global_edit_menu(self):
        menubar = tk.Menu(self)
        edit_menu = tk.Menu(menubar, tearoff=0)

        def act(action):
            w = get_active_text_widget(self)
            if not w:
                return
            if action == "cut":
                w.event_generate("<<Cut>>")
            elif action == "copy":
                w.event_generate("<<Copy>>")
            elif action == "paste":
                w.event_generate("<<Paste>>")
            elif action == "select_all":
                text_select_all(w)
            elif action == "clear":
                w.delete("1.0", "end")

        edit_menu.add_command(label="Вырезать", accelerator="Ctrl+X" if not IS_MAC else "⌘X",
                              command=lambda: act("cut"))
        edit_menu.add_command(label="Копировать", accelerator="Ctrl+C" if not IS_MAC else "⌘C",
                              command=lambda: act("copy"))
        edit_menu.add_command(label="Вставить", accelerator="Ctrl+V" if not IS_MAC else "⌘V",
                              command=lambda: act("paste"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Выделить всё", accelerator="Ctrl+A" if not IS_MAC else "⌘A",
                              command=lambda: act("select_all"))
        edit_menu.add_command(label="Очистить", command=lambda: act("clear"))

        menubar.add_cascade(label="Правка", menu=edit_menu)
        self.config(menu=menubar)

if __name__ == "__main__":
    App().mainloop()
