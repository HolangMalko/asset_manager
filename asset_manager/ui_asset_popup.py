import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from utils import fix_date_format

class AssetPopup(tk.Toplevel):
    def __init__(self, parent, on_submit, asset=None):
        super().__init__(parent)
        self.title("자산 추가/편집")
        self.geometry("460x350")
        self.resizable(False, False)
        self.on_submit = on_submit
        self.category_list = ["예금", "적금", "주식"]

        # 최소화/최대화 버튼 비활성화 (윈도우 스타일 속성 설정)
        self.attributes("-toolwindow", True)  # 최소화/최대화 버튼 숨기기 (윈도우 스타일)

        self.kind_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.expire_var = tk.StringVar()
        self.alert_var = tk.BooleanVar(value=False)
        self.note_var = tk.StringVar()

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        if asset:
            self.load_asset(asset)

    def create_widgets(self):
        label_width = 8
        input_width = 35  # 충분히 넓게 설정

        # 종류 프레임 (콤보박스 + 버튼 한 줄)
        frame_kind = tk.Frame(self)
        frame_kind.pack(pady=6, fill="x", padx=10)

        ttk.Label(frame_kind, text="종류:", width=label_width, anchor="w").pack(side="left")
        self.kind_combo = ttk.Combobox(
            frame_kind,
            values=self.category_list,
            textvariable=self.kind_var,
            state="normal",
            width=input_width
        )
        self.kind_combo.pack(side="left")
        self.btn_add_remove = ttk.Button(frame_kind, text="추가 / 제거", width=10, command=self.add_or_remove_kind)
        self.btn_add_remove.pack(side="left", padx=5)

        # 자산명 프레임
        frame_name = tk.Frame(self)
        frame_name.pack(pady=4, fill="x", padx=10)
        ttk.Label(frame_name, text="자산명:", width=label_width, anchor="w").pack(side="left")
        ttk.Entry(frame_name, textvariable=self.name_var, width=input_width).pack(side="left", fill="x", expand=False)

        # 금액 프레임
        frame_amount = tk.Frame(self)
        frame_amount.pack(pady=4, fill="x", padx=10)
        ttk.Label(frame_amount, text="금액:", width=label_width, anchor="w").pack(side="left")
        entry_amount = ttk.Entry(frame_amount, textvariable=self.amount_var, width=input_width)
        entry_amount.pack(side="left", fill="x", expand=False)
        entry_amount.bind("<KeyRelease>", self.format_amount)

        # 만기일 프레임
        frame_expire = tk.Frame(self)
        frame_expire.pack(pady=4, fill="x", padx=10)
        ttk.Label(frame_expire, text="만기일:", width=label_width, anchor="w").pack(side="left")
        self.expire_entry = DateEntry(
            frame_expire,
            date_pattern='yyyy-MM-dd',
            textvariable=self.expire_var,
            width=input_width,
            background='darkblue',
            foreground='white',
            borderwidth=2
        )
        self.expire_entry.pack(side="left", fill="x", expand=False)
        self.expire_var.set("YYYY-MM-DD")
        self.expire_entry.bind("<FocusIn>", self.open_calendar)
        self.expire_entry.bind("<FocusOut>", self.restore_expire_placeholder)

        # 비고 프레임 (Text 위젯, 충분히 세로 넓게)
        frame_note = tk.Frame(self)
        frame_note.pack(pady=4, fill="x", padx=10)
        ttk.Label(frame_note, text="비고:", width=label_width, anchor="w").pack(side="left")
        self.note_entry = tk.Text(frame_note, height=8, width=input_width)  # 8줄 높이
        self.note_entry.pack(side="left", fill="x", expand=False)

        # 알림 프레임
        frame_alert = tk.Frame(self)
        frame_alert.pack(pady=4, fill="x", padx=10)
        ttk.Label(frame_alert, text="알림:", width=label_width, anchor="w").pack(side="left")
        ttk.Checkbutton(frame_alert, variable=self.alert_var).pack(side="left")

        # 버튼 프레임 (저장/취소 중앙 정렬, 여백 최소화)
        frame_btn = tk.Frame(self)
        frame_btn.pack(pady=8)
        self.btn_save = ttk.Button(frame_btn, text="저장", width=12, command=self.on_save)
        self.btn_save.pack(side="left", padx=15)
        self.btn_cancel = ttk.Button(frame_btn, text="취소", width=12, command=self.on_cancel)
        self.btn_cancel.pack(side="left", padx=15)

    def open_calendar(self, event=None):
        self.expire_entry.event_generate('<Button-1>')

    def add_or_remove_kind(self):
        current_value = self.kind_var.get().strip()
        if not current_value:
            messagebox.showwarning("경고", "종류를 입력하거나 선택하세요.", parent=self)
            return

        if current_value in self.category_list:
            self.category_list.remove(current_value)
            messagebox.showinfo("알림", f"'{current_value}' 종류가 제거되었습니다.", parent=self)
            self.kind_var.set("")
        else:
            self.category_list.append(current_value)
            messagebox.showinfo("알림", f"'{current_value}' 종류가 추가되었습니다.", parent=self)

        self.kind_combo['values'] = self.category_list

    def format_amount(self, event=None):
        val = self.amount_var.get().replace(",", "")
        if val.isdigit():
            formatted = f"{int(val):,}"
            self.amount_var.set(formatted)
        elif val == "":
            self.amount_var.set("")
        else:
            pass

    def on_save(self):
        kind = self.kind_var.get().strip()
        name = self.name_var.get().strip()
        amount_str = self.amount_var.get().replace(",", "").strip()
        expire = self.expire_var.get().strip()
        alert = self.alert_var.get()
        note = self.note_entry.get("1.0", "end").strip()

        if not kind or not name or not amount_str or not expire or expire == "YYYY-MM-DD":
            messagebox.showerror("오류", "모든 필수 항목을 입력해주세요.", parent=self)
            return

        if not amount_str.isdigit():
            messagebox.showerror("오류", "금액은 숫자만 입력 가능합니다.", parent=self)
            return

        if not fix_date_format(expire):
            messagebox.showerror("오류", "만기일 날짜 입력이 잘못 되었습니다. 형식에 맞게 입력해주세요", parent=self)
            return

        amount = int(amount_str)
        asset = [kind, name, amount, expire, alert, note]

        self.on_submit(asset)
        self.destroy()

    def on_cancel(self):
        self.destroy()

    def on_close(self):
        self.destroy()

    def load_asset(self, asset):
        kind, name, amount, expire, alert, note = asset
        if kind not in self.category_list:
            self.category_list.append(kind)
            self.kind_combo['values'] = self.category_list
        self.kind_var.set(kind)
        self.name_var.set(name)
        self.amount_var.set(f"{amount:,}")
        self.expire_var.set(expire)
        self.alert_var.set(alert)
        self.note_entry.delete("1.0", "end")
        self.note_entry.insert("1.0", note)

    def restore_expire_placeholder(self, event=None):
        if not self.expire_var.get():
            self.expire_var.set("YYYY-MM-DD")
