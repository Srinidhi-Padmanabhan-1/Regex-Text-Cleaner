import tkinter as tk
import re

# Global state to track if personal info is currently hidden
pii_hidden = False

def identify_text():
    # Clear any previous highlights
    tags_to_clear = [
        "url_highlight", "slang_highlight", "address_highlight", 
        "email_highlight", "phone_highlight", "handle_highlight", "hashtag_highlight"
    ]
    for tag in tags_to_clear:
        text_in.tag_remove(tag, "1.0", tk.END)

    content = text_in.get("1.0", tk.END)

    # 1. Identify URLs
    url_pattern = r'(?:https?://)?www\.[a-zA-Z0-9.-]+[^\s]*[a-zA-Z0-9/]'
    for match in re.finditer(url_pattern, content):
        text_in.tag_add("url_highlight", f"1.0 + {match.start()}c", f"1.0 + {match.end()}c")

    # 2. Identify Hardcoded Slang
    slang_patterns = [
        r'\bh+e+y+\b', r'\bp+l+e+a+s+e+\b', r'\bh+e+l+o+\b', 
        r'\bh+i+\b', r'\bs+o+\b', r'\bv+e+r+y+\b'
    ]
    for pattern in slang_patterns:
        for match in re.finditer(pattern, content, flags=re.IGNORECASE):
            text_in.tag_add("slang_highlight", f"1.0 + {match.start()}c", f"1.0 + {match.end()}c")

    # 3. Identify Phone Numbers (Indian context exactly 10 digits)
    phone_pattern = r'\b(?:\d[ ]*){9}\d\b'
    for match in re.finditer(phone_pattern, content):
        text_in.tag_add("phone_highlight", f"1.0 + {match.start()}c", f"1.0 + {match.end()}c")

    # 4. Identify Address Blocks
    address_pattern = r'(?:\b\d{1,3}\b|\bAL[-\s]?\d+\b)(?:(?!\n\n).)*?\b\d{6}\b'
    for match in re.finditer(address_pattern, content, flags=re.DOTALL | re.IGNORECASE):
        text_in.tag_add("address_highlight", f"1.0 + {match.start()}c", f"1.0 + {match.end()}c")

    # 5. Identify Emails
    for match in re.finditer(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', content):
        text_in.tag_add("email_highlight", f"1.0 + {match.start()}c", f"1.0 + {match.end()}c")

    # 6. Identify Social Media Handles
    handle_pattern = r'\B@[a-zA-Z0-9_]+'
    for match in re.finditer(handle_pattern, content):
        text_in.tag_add("handle_highlight", f"1.0 + {match.start()}c", f"1.0 + {match.end()}c")

    # 7. Identify Social Media Trends / Hashtags
    hashtag_pattern = r'#[a-zA-Z0-9_]+'
    for match in re.finditer(hashtag_pattern, content):
        text_in.tag_add("hashtag_highlight", f"1.0 + {match.start()}c", f"1.0 + {match.end()}c")

    # Unlock the processing buttons forever so user can continuously edit
    btn_clean.config(state=tk.NORMAL)
    btn_redact.config(state=tk.NORMAL)

def process_text(redact_pii=False):
    """Handles both normal cleaning and the hiding of personal info"""
    content = text_in.get("1.0", tk.END)

    # 1. Clean URLs
    content = re.sub(r'(?:https?://)?www\.([a-zA-Z0-9.-]+[^\s]*[a-zA-Z0-9/])', r'\1', content)

    # 2. Clean Hardcoded Slang
    slang_dict = {
        r'\bh+e+y+\b': 'hey',
        r'\bp+l+e+a+s+e+\b': 'please',
        r'\bh+e+l+o+\b': 'hello',
        r'\bh+i+\b': 'hi',
        r'\bs+o+\b': 'so',
        r'\bv+e+r+y+\b': 'very'
    }
    for pattern, replacement in slang_dict.items():
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

    # 3. Clean OR Redact Phone Numbers
    phone_pattern = r'\b(?:\d[ ]*){9}\d\b'
    if redact_pii:
        content = re.sub(phone_pattern, '[PHONE]', content)
    else:
        def clean_phone(match):
            return match.group(0).replace(" ", "")
        content = re.sub(phone_pattern, clean_phone, content)

    # 4. Clean Address Blocks
    def clean_address_block(match):
        text = match.group(0)
        cleaned = text.replace('\n', ' ')             
        cleaned = re.sub(r' +', ' ', cleaned)         
        cleaned = re.sub(r'\s+,', ',', cleaned)       
        return cleaned.strip()

    address_pattern = r'(?:\b\d{1,3}\b|\bAL[-\s]?\d+\b)(?:(?!\n\n).)*?\b\d{6}\b'
    content = re.sub(address_pattern, clean_address_block, content, flags=re.DOTALL | re.IGNORECASE)

    # 5. Redact Emails (Only if redaction is active)
    if redact_pii:
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        content = re.sub(email_pattern, '[EMAIL]', content)

    # --- OUTPUT ---
    text_out.config(state=tk.NORMAL)
    text_out.delete("1.0", tk.END)
    text_out.insert("1.0", content.strip())
    text_out.config(state=tk.DISABLED)

# --- Button Functions ---
def clean_only():
    global pii_hidden
    # Runs the clean process respecting whatever the current toggle state is
    process_text(redact_pii=pii_hidden)

def toggle_personal_info():
    global pii_hidden
    pii_hidden = not pii_hidden # Flip the state
    
    if pii_hidden:
        # If we just hid the info, change button to "Show" (Green color)
        btn_redact.config(text="Show Personal Info", bg="#c8e6c9") 
        process_text(redact_pii=True)
    else:
        # If we just showed the info, change button to "Hide" (Red color)
        btn_redact.config(text="Hide Personal Info", bg="#ffcccb") 
        process_text(redact_pii=False)


# ==========================================
# GUI Setup
# ==========================================
root = tk.Tk()
root.title("Regex Text Cleaner - Assessment Version")
# ENLARGED WINDOW to fit the much bigger fonts
root.geometry("1200x850") 

text_frame = tk.Frame(root)
text_frame.pack(pady=15)

# TITLES: Font size increased to 16
lbl_in = tk.Label(text_frame, text="Raw Input Text", font=("Arial", 16, "bold"))
lbl_in.grid(row=0, column=0, pady=(0, 5))

lbl_out = tk.Label(text_frame, text="Cleaned Standardized Output", font=("Arial", 16, "bold"))
lbl_out.grid(row=0, column=1, pady=(0, 5))

# TEXT BOXES: Font size increased to 14
text_in = tk.Text(text_frame, height=20, width=45, font=("Arial", 14), wrap=tk.WORD)
text_in.grid(row=1, column=0, padx=15)

text_out = tk.Text(text_frame, height=20, width=45, font=("Arial", 14), bg="#f0f0f0", state=tk.DISABLED, wrap=tk.WORD)
text_out.grid(row=1, column=1, padx=15)

# Configure Highlighter Colors
text_in.tag_configure("url_highlight", background="lightblue")
text_in.tag_configure("slang_highlight", background="lightgreen")
text_in.tag_configure("address_highlight", background="orange")
text_in.tag_configure("email_highlight", background="yellow")
text_in.tag_configure("phone_highlight", background="magenta", foreground="white") 
text_in.tag_configure("handle_highlight", background="cyan") 
text_in.tag_configure("hashtag_highlight", background="#d8b4e2") 

# LEGEND: Font size increased to 14 (Header) and 12 (Items)
legend_frame = tk.LabelFrame(root, text="Highlight Color Key", font=("Arial", 14, "bold"), padx=10, pady=10)
legend_frame.pack(pady=10, padx=20)

legend_items = [
    ("URLs", "lightblue", "black"),
    ("Exaggerated Slang", "lightgreen", "black"),
    ("Indian Phone Numbers", "magenta", "white"),
    ("Multi-Line Addresses", "orange", "black"),
    ("Email Addresses", "yellow", "black"),
    ("Social Media Handles", "cyan", "black"),
    ("Trending Hashtags", "#d8b4e2", "black")
]

for i, (text, bg, fg) in enumerate(legend_items):
    row = i // 4  
    col = i % 4
    # Increased width slightly to 22 so text fits inside the bigger font
    lbl = tk.Label(legend_frame, text=text, bg=bg, fg=fg, font=("Arial", 12, "bold"), width=22, relief="solid", bd=1)
    lbl.grid(row=row, column=col, padx=10, pady=8)

# Sample text
sample_text = (
    "Heyyyyyy check this out: https://www.google.com/search?q=test\n\n"
    "Shoutout to @CodeMaster for the #NLP help!\n\n"
    "Call me at 987 65 432 10 or email me.\n"
    "Contact the team at admin.support@company.com pleaaaaase.\n"
    "It is veryyyy important sooooo do it quickly.\n\n"
    "Deliver to this address:\n"
    "103, B-Wing,\n"
    "suraj apartments,\n"
    "sector-5, Navi Mumbai 400706.\n\n"
    "Or the office here:\n"
    "AL-6, 21,\n"
    "Tech Park, New Delhi 110011."
)
text_in.insert("1.0", sample_text)

# BUTTONS: Font size increased to 14, widened to 18
btn_frame = tk.Frame(root)
btn_frame.pack(pady=15)

btn_identify = tk.Button(btn_frame, text="Identify Text", command=identify_text, width=18, font=("Arial", 14, "bold"), bg="#d9d9d9")
btn_identify.grid(row=0, column=0, padx=15)

btn_clean = tk.Button(btn_frame, text="Clean All Matches", command=clean_only, state=tk.DISABLED, width=18, font=("Arial", 14, "bold"), bg="#d9d9d9")
btn_clean.grid(row=0, column=1, padx=15)

btn_redact = tk.Button(btn_frame, text="Hide Personal Info", command=toggle_personal_info, state=tk.DISABLED, width=18, font=("Arial", 14, "bold"), bg="#ffcccb")
btn_redact.grid(row=0, column=2, padx=15)

root.mainloop()
