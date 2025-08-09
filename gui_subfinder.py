# gui_subfinder.py
import os
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

from utils import scanner

class App:
    def __init__(self, root):
        self.root = root
        root.title("SubFinder GUI")
        root.geometry("760x520")
        self.stop_event = threading.Event()
        self.results = []
        self._build_ui()

    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Target domain (e.g. example.com):").grid(row=0, column=0, sticky=tk.W)
        self.domain_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.domain_var, width=40).grid(row=0, column=1, sticky=tk.W, padx=6, pady=4)

        ttk.Label(frm, text="Wordlist:").grid(row=1, column=0, sticky=tk.W)
        self.wordlist_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.wordlist_var, width=40).grid(row=1, column=1, sticky=tk.W, padx=6)
        ttk.Button(frm, text="Browse", command=self.browse_wordlist).grid(row=1, column=2, padx=6)
        ttk.Button(frm, text="Use sample", command=self.use_sample_wordlist).grid(row=1, column=3, padx=6)

        ttk.Label(frm, text="Workers:").grid(row=2, column=0, sticky=tk.W)
        self.workers_var = tk.IntVar(value=30)
        ttk.Spinbox(frm, from_=1, to=200, textvariable=self.workers_var, width=6).grid(row=2, column=1, sticky=tk.W)
        ttk.Label(frm, text="Timeout(s):").grid(row=2, column=2, sticky=tk.W)
        self.timeout_var = tk.DoubleVar(value=2.0)
        ttk.Spinbox(frm, from_=0.5, to=10.0, increment=0.5, textvariable=self.timeout_var, width=6).grid(row=2, column=3, sticky=tk.W)

        self.start_btn = ttk.Button(frm, text="Start Scan", command=self.start_scan)
        self.start_btn.grid(row=3, column=1, pady=8, sticky=tk.W)
        self.stop_btn = ttk.Button(frm, text="Stop", command=self.stop_scan, state=tk.DISABLED)
        self.stop_btn.grid(row=3, column=2, pady=8, sticky=tk.W)
        ttk.Button(frm, text="Save results", command=self.save_results).grid(row=3, column=3, pady=8, sticky=tk.W)

        self.status_var = tk.StringVar(value="Idle.")
        ttk.Label(frm, textvariable=self.status_var).grid(row=4, column=0, columnspan=4, sticky=tk.W, pady=(2,8))

        self.output = scrolledtext.ScrolledText(frm, width=95, height=20)
        self.output.grid(row=5, column=0, columnspan=4, pady=8)

    def browse_wordlist(self):
        path = filedialog.askopenfilename(title="Select wordlist", filetypes=[("Text files", "*.txt")])
        if path:
            self.wordlist_var.set(path)

    def use_sample_wordlist(self):
        p = os.path.join(os.path.dirname(__file__), "wordlists", "common-subdomains.txt")
        if os.path.exists(p):
            self.wordlist_var.set(p)
        else:
            messagebox.showwarning("Not found", "Sample wordlist not found. Make sure wordlists/common-subdomains.txt exists.")

    def start_scan(self):
        domain = self.domain_var.get().strip()
        wlpath = self.wordlist_var.get().strip()
        if not domain:
            messagebox.showerror("Error", "Enter a target domain (you must have permission to scan).")
            return
        if not wlpath or not os.path.exists(wlpath):
            messagebox.showerror("Error", "Select a valid wordlist file.")
            return
        try:
            with open(wlpath, "r") as f:
                subs = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        except Exception as e:
            messagebox.showerror("Error", f"Cannot read wordlist: {e}")
            return

        self.results = []
        self.stop_event.clear()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.status_var.set(f"Scanning 0/{len(subs)} ...")

        def found_cb(res):
            # called from scanner threads -> schedule UI update in main thread
            self.root.after(0, self._on_found, res)

        def progress_cb(scanned, total):
            self.root.after(0, lambda: self.status_var.set(f"Scanning {scanned}/{total} ..."))

        def worker():
            try:
                results = scanner.scan(domain, subs,
                                       callback=found_cb,
                                       progress_callback=progress_cb,
                                       max_workers=self.workers_var.get(),
                                       timeout=self.timeout_var.get(),
                                       stop_event=self.stop_event)
                self.root.after(0, self._on_done, results)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _on_found(self, res):
        line = f"{res['fqdn']}  |  {res['ip']}"
        if res.get("status") is not None:
            line += f"  |  HTTP:{res['status']}"
        self.output.insert(tk.END, line + "\n")
        self.output.see(tk.END)
        self.results.append(res)

    def _on_done(self, results):
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set(f"Done. {len(results)} subdomains found.")

    def stop_scan(self):
        self.stop_event.set()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("Stopping...")

    def save_results(self):
        if not self.results:
            messagebox.showinfo("No results", "No results to save.")
            return
        default = f"found_{self.domain_var.get().strip().replace('.', '_')}_{int(time.time())}.txt"
        path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=default,
                                            filetypes=[("Text files", "*.txt")])
        if not path:
            return
        with open(path, "w") as f:
            for r in self.results:
                f.write(f"{r['fqdn']}\t{r['ip']}\t{r.get('status')}\n")
        messagebox.showinfo("Saved", f"Saved {len(self.results)} records to {path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
