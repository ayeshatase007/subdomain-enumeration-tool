# Subfinder-GUI

A simple **GUI-based subdomain enumeration tool** built in Python.  
It allows users to scan for subdomains of a target domain using a predefined wordlist, with an easy-to-use graphical interface.  
This is useful for **bug bounty hunters**, **security researchers**, and **penetration testers** to quickly discover potential subdomains.

---

## 📂 Project Structure

subfinder-gui/
│
├── utils/
│ ├── init.py # Marks utils as a Python package
│ ├── scanner.py # Core scanning logic for subdomain enumeration
│
├── wordlists/
│ ├── common-subdomains.txt # List of common subdomains for brute-forcing
│
├── .gitignore # Files & folders ignored by Git
├── LICENSE # License for the project
├── README.md # Project documentation (you’re reading it!)
├── gui_subfinder.py # Main Python file to launch the GUI tool
├── requirements.txt # Python dependencies

---

## ✨ Features

- **GUI Interface** – No need to use the terminal for enumeration.
- **Custom Wordlist Support** – Easily replace `common-subdomains.txt` with your own.
- **Fast Enumeration** – Uses concurrent requests for faster results.
- **Beginner-Friendly** – Simple installation and usage.

---

## ⚙️ Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/subfinder-gui.git
cd subfinder-gui

2️⃣ Install Requirements
Make sure you have Python 3.8+ installed.
pip install -r requirements.txt

🚀 Usage
python gui_subfinder.py
Enter the target domain (e.g., example.com).

Select the wordlist file (common-subdomains.txt by default).

Click Scan to start the enumeration.

View the discovered subdomains in the results box.

🛠 How It Works
The GUI (gui_subfinder.py) takes user input for:

Target domain

Wordlist

The scanning logic in utils/scanner.py:

Reads subdomains from the wordlist

Sends HTTP requests to check if they are live

Displays valid results in the GUI

The wordlist in wordlists/common-subdomains.txt contains commonly used subdomain names.

⚠️ Disclaimer
This tool is intended for educational and authorized security testing only.
The author is not responsible for any misuse or damage caused.

Author: Ayesha Tase