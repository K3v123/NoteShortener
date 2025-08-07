import re
import tkinter as tk
from tkinter import scrolledtext
import threading

# Ordered shorthand replacement rules
SHORTHAND_RULES = [
    (r"\boperating system\b", "os"),
    (r"\boperating systems\b", "os's"),
    (r"\bleft hand side\b", "lhs"),
    (r"\bright hand side\b", "rhs"),
    (r"\bis not\b", "!="),
    (r"\bis\b|\bare\b", "="),
    (r"\bdefinition\b|\bdefine\b", "def"),
    (r"\bbecause\b", "bc"),
    (r"\bcannot\b", "!can"),
    (r"\bexample\b", "eg"),
    (r"\band\b", "&"),
    (r"\bor\b", "/"),
    (r"\bconfiguration\b", "config"),
    (r"\bhardware\b", "hardw"),
    (r"\bsoftware\b", "softw"),
    (r"\bcomputer\b", "pc"),
    (r"\bfunction\b", "func"),
    (r"\bremoved\b", "rm'd"),
    (r"\bone\b", "1"),
    (r"\btwo\b", "2"),
    (r"\bapplication\b", "app"),
    (r"\barchitecture\b", "arch"),
    (r"\bthousands\b", "thousands"),
    (r"\bprocess\b", "proc"),
    (r"\bgeneral\b", "gen"),
    (r"\bsupproted\b", "suppor'd"),
    (r"\bsystem\b", "sys"),
    (r"\bincrease\b", "incr"),
    (r"\bincreases\b", "incr's"),
    (r"\bincreases\b|\bincrease's\b", "def"),
    (r"\bdecrease\b", "decr"),
    (r"\bdecreases\b|\bdecrease's\b", "def"),
    (r"\blanguage\b", "lang"),
    (r"\blanguages\b|\blanguage's\b", "lang's"),
    (r"\bpower\b", "pow"),
    (r"\bpowers\b|\bpower's\b", "pow's"),
    (r"\bcritical\b", "crit"),
    (r"\bdescribe\b", "descri"),
    (r"\bdescribes\b|\bdescribe's\b", "descri's"),
    (r"\binformation\b", "info"),
    (r"\binformations\b|\bversion's\b", "info's"),
    (r"\bdocument\b", "doc"),
    (r"\bdocuments\b|\bdocument's\b", "doc's"),
    (r"\bsimple\b", "simp"),
    (r"\bresource\b", "rss"),
    (r"\bresources\b|\bresource's\b", "rss's"),
    (r"\berror\b", "err"),
    (r"\berrors\b|\berror's\b", "err's"),
    (r"\bconfigure\b", "config"),
    (r"\bversion\b", "ver"),
    (r"\bversions\b|\bversion's\b", "ver's"),
    (r"\benvironment\b", "enviro"),
    (r"\benvironments\b|\benvironment's\b", "enviro's"),
    (r"\bcorrect\b", "correc"),
    (r"\b([a-zA-Z]+)ies\b", r"\1's"),
    (r"\bdifferent\b", "diff"),
    (r"\bautomatic\b", "auto"),
    (r"\bmessage\b", "msg"),
    (r"\btext\b", "txt"),
    (r"\bthrough\b", "thru"),
    (r"\bsignificant\b", "sig"),
    (r"\bcalculation\b", "cal"),
    (r"\bcalculations\b|\bcalculation's\b", "cal's"),
]


class ShorthandConverter:
    def __init__(self):
        self.changes = []

    def apply_shorthand(self, text: str) -> str:
        """Apply shorthand replacements and track exact positions."""
        self.changes = []

        # Create a list to track character positions
        char_map = list(range(len(text)))  # Maps current positions to original positions
        result = text

        for pattern, repl in SHORTHAND_RULES:
            new_result = ""
            new_char_map = []
            pos = 0

            for match in re.finditer(pattern, result, flags=re.IGNORECASE):
                start, end = match.span()
                original = match.group()

                # Add text before match
                new_result += result[pos:start]
                new_char_map.extend(char_map[pos:start])

                # Add replacement
                new_result += repl
                # Map all replacement characters to the start position of original text
                new_char_map.extend([char_map[start]] * len(repl))

                # Record the change with original positions
                if pos < len(char_map):
                    orig_start = char_map[start]
                    orig_end = char_map[end - 1] + 1 if end > start else char_map[start]
                    self.changes.append((orig_start, orig_end, original, repl))

                pos = end

            # Add remaining text
            new_result += result[pos:]
            new_char_map.extend(char_map[pos:])

            result = new_result
            char_map = new_char_map

        return result


def process_text():
    """Fetch input, apply shorthand, display output with highlighting."""
    raw = input_box.get("1.0", tk.END)
    # Remove the extra newline that tkinter adds
    if raw.endswith('\n'):
        raw = raw[:-1]

    # Process in background thread to prevent UI freezing
    def worker():
        converter = ShorthandConverter()
        transformed = converter.apply_shorthand(raw)
        changes = converter.changes

        # Update UI in main thread
        root.after(0, lambda: update_output(raw, transformed, changes))

    threading.Thread(target=worker, daemon=True).start()


def update_output(original, transformed, changes):
    """Update output display with syntax highlighting."""
    # Clear both text boxes
    output_box.delete("1.0", tk.END)
    input_box.tag_remove("changed_input", "1.0", tk.END)

    # Insert transformed text
    output_box.insert("1.0", transformed)

    # Apply highlighting to input box (original text)
    for start, end, original_text, replacement in changes:
        tk_start_input = f"1.0+{start}c"
        tk_end_input = f"1.0+{end}c"
        input_box.tag_add("changed_input", tk_start_input, tk_end_input)

    # For output highlighting, we need to find where each replacement ended up
    # We'll rebuild the transformation and track output positions
    output_positions = []
    current_output_pos = 0
    last_processed_end = 0
    sorted_changes = sorted(changes, key=lambda x: x[0])

    for orig_start, orig_end, original_text, replacement in sorted_changes:
        # Add text before this change to our position tracking
        text_before = original[last_processed_end:orig_start]
        current_output_pos += len(text_before)

        # Record where this replacement appears in output
        replacement_start = current_output_pos
        replacement_end = current_output_pos + len(replacement)
        output_positions.append((replacement_start, replacement_end, original_text, replacement))

        # Update positions
        current_output_pos = replacement_end
        last_processed_end = orig_end

    # Apply highlighting to output box (transformed text)
    for start, end, original_text, replacement in output_positions:
        tk_start_output = f"1.0+{start}c"
        tk_end_output = f"1.0+{end}c"
        output_box.tag_add("changed_output", tk_start_output, tk_end_output)

    # Configure tags
    input_box.tag_config("changed_input", foreground="#4FC3F7", background="#1A237E")
    output_box.tag_config("changed_output", foreground="#FF8A80", background="#4A148C")


def sync_scrollbars(*args):
    """Synchronize scrolling between input and output text boxes."""
    # Get the current view of the input box
    input_yview = input_box.yview()
    input_xview = input_box.xview()

    # Apply the same view to the output box
    output_box.yview_moveto(input_yview[0])
    output_box.xview_moveto(input_xview[0])


def on_mousewheel(event):
    """Handle mouse wheel scrolling for both text boxes."""
    # Scroll both text widgets vertically
    input_box.yview_scroll(int(-1 * (event.delta / 120)), "units")
    output_box.yview_scroll(int(-1 * (event.delta / 120)), "units")
    return "break"  # Prevent default scrolling


def on_shift_mousewheel(event):
    """Handle shift + mouse wheel for horizontal scrolling."""
    # Scroll both text widgets horizontally
    input_box.xview_scroll(int(-1 * (event.delta / 120)), "units")
    output_box.xview_scroll(int(-1 * (event.delta / 120)), "units")
    return "break"  # Prevent default scrolling


# Set up GUI window with resizable properties
root = tk.Tk()
root.title("Shorthand Note Converter")
root.geometry("1200x800")  # Default size
root.minsize(800, 600)  # Minimum size for resizing
root.configure(bg="#0F0F0F")

# Configure window resizing weights
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Main frame with expandable properties
main_frame = tk.Frame(root, bg="#0F0F0F")
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
main_frame.grid_rowconfigure(2, weight=1)  # Text area expands
main_frame.grid_columnconfigure(0, weight=1)

# Header with modern styling
header_frame = tk.Frame(main_frame, bg="#1A1A1A", relief=tk.FLAT, bd=0)
header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
header_frame.grid_columnconfigure(0, weight=1)

title_label = tk.Label(
    header_frame,
    text="SHORTHAND NOTE CONVERTER",
    font=("Segoe UI", 22, "bold"),
    bg="#1A1A1A",
    fg="#BB86FC",
    pady=20
)
title_label.grid(row=0, column=0, sticky="ew")

subtitle_label = tk.Label(
    header_frame,
    text="Transform your notes into concise shorthand notation",
    font=("Segoe UI", 12),
    bg="#1A1A1A",
    fg="#A0A0A0"
)
subtitle_label.grid(row=1, column=0, sticky="ew")

# Text frames container
text_container = tk.Frame(main_frame, bg="#0F0F0F")
text_container.grid(row=2, column=0, sticky="nsew")
text_container.grid_rowconfigure(0, weight=1)
text_container.grid_columnconfigure(0, weight=1)
text_container.grid_columnconfigure(1, weight=1)

# Input frame with modern styling
input_frame = tk.Frame(text_container, bg="#1A1A1A", relief=tk.FLAT, bd=1)
input_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

input_header = tk.Frame(input_frame, bg="#2D2D2D", relief=tk.FLAT)
input_header.pack(fill=tk.X)

input_label = tk.Label(
    input_header,
    text="ORIGINAL TEXT",
    font=("Segoe UI", 12, "bold"),
    bg="#2D2D2D",
    fg="#03DAC6",
    padx=15,
    pady=10
)
input_label.pack(side=tk.LEFT)

input_box = scrolledtext.ScrolledText(
    input_frame,
    wrap=tk.WORD,
    undo=True,
    bg="#252526",
    fg="#E0E0E0",
    insertbackground="#BB86FC",
    selectbackground="#3A3A3A",
    font=("Consolas", 12),
    relief=tk.FLAT,
    padx=15,
    pady=15,
    bd=0
)
input_box.pack(fill=tk.BOTH, expand=True)

# Output frame with modern styling
output_frame = tk.Frame(text_container, bg="#1A1A1A", relief=tk.FLAT, bd=1)
output_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

output_header = tk.Frame(output_frame, bg="#2D2D2D", relief=tk.FLAT)
output_header.pack(fill=tk.X)

output_label = tk.Label(
    output_header,
    text="SHORTHAND OUTPUT",
    font=("Segoe UI", 12, "bold"),
    bg="#2D2D2D",
    fg="#03DAC6",
    padx=15,
    pady=10
)
output_label.pack(side=tk.LEFT)

output_box = scrolledtext.ScrolledText(
    output_frame,
    wrap=tk.WORD,
    undo=True,
    bg="#252526",
    fg="#E0E0E0",
    insertbackground="#BB86FC",
    selectbackground="#3A3A3A",
    font=("Consolas", 12),
    relief=tk.FLAT,
    padx=15,
    pady=15,
    bd=0
)
output_box.pack(fill=tk.BOTH, expand=True)

# Process button with modern styling
btn_frame = tk.Frame(main_frame, bg="#0F0F0F")
btn_frame.grid(row=3, column=0, sticky="ew", pady=(25, 15))
btn_frame.grid_columnconfigure(0, weight=1)

convert_btn = tk.Button(
    btn_frame,
    text="TRANSFORM TO SHORTHAND",
    command=process_text,
    bg="#BB86FC",
    fg="#121212",
    font=("Segoe UI", 13, "bold"),
    activebackground="#9A67EA",
    activeforeground="#121212",
    relief=tk.FLAT,
    padx=40,
    pady=15,
    cursor="hand2",
    bd=0
)
convert_btn.grid(row=0, column=0)

# Footer with instructions
footer_frame = tk.Frame(main_frame, bg="#0F0F0F")
footer_frame.grid(row=4, column=0, sticky="ew")
footer_frame.grid_columnconfigure(0, weight=1)

instructions = tk.Label(
    footer_frame,
    text="💡 Tip: Scroll vertically to navigate paragraphs • Hold SHIFT + Scroll for horizontal navigation • Blue highlight = original text • Red highlight = transformed text",
    font=("Segoe UI", 11),
    bg="#0F0F0F",
    fg="#A0A0A0",
    wraplength=900
)
instructions.grid(row=0, column=0, pady=(15, 0))

# Bind scroll events for synchronization
input_box.configure(yscrollcommand=lambda *args: sync_scrollbars())

# Bind mouse wheel events
input_box.bind("<MouseWheel>", on_mousewheel)
output_box.bind("<MouseWheel>", on_mousewheel)
input_box.bind("<Shift-MouseWheel>", on_shift_mousewheel)
output_box.bind("<Shift-MouseWheel>", on_shift_mousewheel)

# Configure tags for highlighting
input_box.tag_config("changed_input", foreground="#4FC3F7", background="#1A237E")
output_box.tag_config("changed_output", foreground="#FF8A80", background="#4A148C")

# Add some sample text for demonstration
sample_text = """Inter-thread communication with conditions doesn't allow information to pass through. Queues = an effecient & easy way to pass info betw threads & also provide synchronisation. A queue = a data type that allows 1 process to add data into the queue, whereas another process can retrieve data from the queue. In case the buffer associated with the queue = full, a process adding data would wait. In case the buffer = empty, a process trying to retrieve data would wait as well."""

input_box.insert("1.0", sample_text)

# Run the application
root.mainloop()