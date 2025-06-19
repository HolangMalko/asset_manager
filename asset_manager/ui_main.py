import tkinter as tk
from tkinter import ttk, messagebox
from data_handler import load_data, save_data, export_csv, import_csv
from ui_asset_popup import AssetPopup
from utils import format_currency, calculate_d_day
from datetime import datetime

class AssetManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("자산 관리 프로그램")
        self.geometry("1100x550")

        self.columns = ["종류", "자산명", "금액", "만기일", "알림", "D-Day", "비고"]
        self.data = []
        self.sort_state = {"column": None, "ascending": True}
        self.asset_popup = None

        self.create_widgets()
        self.load_assets()

    def create_widgets(self):
        top = tk.Frame(self)
        top.pack(fill="x")

        ttk.Button(top, text="자산 추가", command=self.add_asset_popup).pack(side="left", padx=5, pady=5)
        ttk.Button(top, text="저장", command=self.save_assets).pack(side="left", padx=5, pady=5)
        ttk.Button(top, text="CSV 내보내기", command=self.export_csv_file).pack(side="left", padx=5, pady=5)
        ttk.Button(top, text="CSV 가져오기", command=self.import_csv_file).pack(side="left", padx=5, pady=5)

        frame = tk.Frame(self)
        frame.pack(expand=True, fill="both")

        self.tree = ttk.Treeview(frame, columns=self.columns, show="headings")
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        for col in self.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by(c))
            self.tree.column(col, anchor="center", width=100)
        self.tree.column("자산명", width=150)
        self.tree.column("만기일", width=110)
        self.tree.column("금액", width=120)
        self.tree.column("D-Day", width=120)
        self.tree.column("비고", width=150)

        self.tree.tag_configure("gray", background="#d3d3d3")
        self.tree.tag_configure("red", background="#ffcccc")

        # 더블클릭 시 팝업 띄우기 (직접 셀 편집 기능은 제거)
        self.tree.bind("<Double-1>", self.on_double_click)

        self.total_label = ttk.Label(self, text="전체 자산 금액 합계: 0 원", anchor="e")
        self.total_label.pack(fill="x", padx=10, pady=5)

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        today = datetime.today().date()

        for idx, asset in enumerate(self.data):
            kind, name, amount, expire, alert, note = asset
            alert_icon = "🔔" if alert else "🔕"
            d_day = calculate_d_day(expire)
            values = [kind, name, format_currency(amount), expire, alert_icon, d_day, note]
            try:
                expire_date = datetime.strptime(expire, "%Y-%m-%d").date()
                if expire_date < today:
                    self.tree.insert("", "end", iid=idx, values=values, tags=("gray",))
                elif (expire_date - today).days <= 7:
                    self.tree.insert("", "end", iid=idx, values=values, tags=("red",))
                else:
                    self.tree.insert("", "end", iid=idx, values=values)
            except:
                self.tree.insert("", "end", iid=idx, values=values)

        total = sum(item[2] for item in self.data)
        self.total_label.config(text=f"전체 자산 금액 합계: {format_currency(total)} 원")

    def add_asset_popup(self):
        if self.asset_popup and self.asset_popup.winfo_exists():
            return
        self.asset_popup = AssetPopup(self, on_submit=self.on_asset_added)

    def on_asset_added(self, asset):
        if asset:
            self.data.append(asset)
            self.refresh_tree()
        self.asset_popup = None

    def save_assets(self):
        try:
            save_data(self.data)
            messagebox.showinfo("저장 완료", "자산 정보가 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("저장 실패", str(e))

    def load_assets(self):
        try:
            self.data = load_data()
            self.refresh_tree()
        except Exception as e:
            messagebox.showerror("불러오기 실패", str(e))

    def export_csv_file(self):
        try:
            export_csv(self.data, self.columns)
            messagebox.showinfo("내보내기 완료", "CSV 내보내기가 완료되었습니다.")
        except Exception as e:
            messagebox.showerror("내보내기 실패", str(e))

    def import_csv_file(self):
        try:
            imported_data = import_csv(self.columns)
            if imported_data is not None:
                self.data = imported_data
                self.refresh_tree()
                messagebox.showinfo("가져오기 완료", "CSV 가져오기가 완료되었습니다.")
        except Exception as e:
            messagebox.showerror("가져오기 실패", str(e))

    def sort_by(self, column):
        idx = self.columns.index(column)
        ascending = True
        if self.sort_state["column"] == column:
            ascending = not self.sort_state["ascending"]
        self.sort_state = {"column": column, "ascending": ascending}

        def sort_key(item):
            if column == "금액":
                return item[2]
            elif column == "만기일":
                try:
                    return datetime.strptime(item[3], "%Y-%m-%d")
                except:
                    return datetime.max
            elif column == "D-Day":
                try:
                    expire_date = datetime.strptime(item[3], "%Y-%m-%d").date()
                    return (expire_date - datetime.today().date()).days
                except:
                    return 999999
            return item[idx]

        self.data.sort(key=sort_key, reverse=not ascending)
        self.refresh_tree()

    def on_double_click(self, event):
        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return
        idx = int(row_id)
        if self.asset_popup and self.asset_popup.winfo_exists():
            return
        self.asset_popup = AssetPopup(self, on_submit=self.on_asset_edited)
        self.asset_popup.set_asset_data(self.data[idx])

    def on_asset_edited(self, updated_asset):
        if updated_asset:
            idx = None
            for i, asset in enumerate(self.data):
                if asset[1] == updated_asset[1]:
                    idx = i
                    break
            if idx is not None:
                self.data[idx] = updated_asset
                self.refresh_tree()
        self.asset_popup = None

if __name__ == "__main__":
    app = AssetManager()
    app.mainloop()
