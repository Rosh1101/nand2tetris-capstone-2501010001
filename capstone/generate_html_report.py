#!/usr/bin/env python3
"""
Compiles REPORT.md and screenshots into a self-contained, standalone HTML document (REPORT.html)
with embedded images, ready to submit on ZOSIMA or export to PDF.
"""

import os
import base64

CAPSTONE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(CAPSTONE_DIR, "screenshots")

def get_base64_img(filename):
    p = os.path.join(SCREENSHOTS_DIR, filename)
    if os.path.exists(p):
        with open(p, "rb") as f:
            b64 = base64.b64encode(f.read()).decode('utf-8')
            return f"data:image/png;base64,{b64}"
    return ""

def build_html_report():
    img_cpu = get_base64_img("screenshot_CPU.png")
    img_mem = get_base64_img("screenshot_Memory.png")
    img_add = get_base64_img("screenshot_ComputerAdd.png")
    img_max = get_base64_img("screenshot_ComputerMax.png")
    img_rect = get_base64_img("screenshot_ComputerRect.png")
    img_box_pressed = get_base64_img("screenshot_Box_KeyPressed.png")
    img_box_released = get_base64_img("screenshot_Box_KeyReleased.png")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Capstone Project Report: Make the Computer Draw a Box</title>
<style>
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        line-height: 1.6;
        color: #24292e;
        max-width: 900px;
        margin: 30px auto;
        padding: 0 25px;
    }}
    h1, h2, h3, h4 {{
        color: #0d1117;
        border-bottom: 1px solid #eaecef;
        padding-bottom: 0.3em;
    }}
    h1 {{ font-size: 2.2em; text-align: center; border: none; margin-bottom: 5px; }}
    .subtitle {{ text-align: center; color: #586069; font-size: 1.1em; margin-bottom: 30px; }}
    .badge-card {{
        background: #f6f8fa;
        border: 1px solid #d1d5da;
        border-radius: 8px;
        padding: 18px 24px;
        margin: 20px 0;
    }}
    .badge-card table {{ width: 100%; border-collapse: collapse; }}
    .badge-card td {{ padding: 6px 12px; font-size: 1.05em; }}
    .badge-card td.label {{ font-weight: bold; width: 30%; color: #444; }}
    pre, code {{
        background-color: #f6f8fa;
        border-radius: 4px;
        font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, Courier, monospace;
        font-size: 0.9em;
    }}
    pre {{
        padding: 14px;
        overflow-x: auto;
        border: 1px solid #e1e4e8;
    }}
    .screenshot-box {{
        margin: 25px 0;
        text-align: center;
        background: #fafbfc;
        border: 1px solid #e1e4e8;
        border-radius: 6px;
        padding: 15px;
    }}
    .screenshot-box img {{
        max-width: 100%;
        height: auto;
        border-radius: 4px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}
    .screenshot-caption {{
        font-weight: 600;
        margin-top: 10px;
        color: #444;
        font-size: 0.95em;
    }}
    .callout-mistake {{
        background: #fff8f2;
        border-left: 5px solid #d97706;
        padding: 16px 20px;
        margin: 20px 0;
        border-radius: 0 6px 6px 0;
    }}
    .viva-box {{
        background: #f0fdf4;
        border-left: 5px solid #16a34a;
        padding: 16px 20px;
        margin: 20px 0;
        border-radius: 0 6px 6px 0;
    }}
    @media print {{
        body {{ max-width: 100%; margin: 15mm; font-size: 10.5pt; }}
        .screenshot-box {{ page-break-inside: avoid; }}
        h2 {{ page-break-after: avoid; }}
    }}
</style>
</head>
<body>

<h1>Capstone Project: Make the Computer Draw a Box</h1>
<div class="subtitle">Computer Organization & Systems Architecture — Hack Hardware & Software Integration</div>

<div class="badge-card">
    <table>
        <tr><td class="label">Student Name:</td><td>Ryan Narula</td></tr>
        <tr><td class="label">Roll Number:</td><td>2501420041</td></tr>
        <tr><td class="label">Personal Number (K):</td><td><strong>41</strong> (Last 2 digits of Roll No.)</td></tr>
        <tr><td class="label">K mod 3 (Assembler Feature):</td><td>41 mod 3 = <strong>2</strong> (Duplicate label warnings; also supports 0 and 1)</td></tr>
        <tr><td class="label">K mod 4 (Width multiplier):</td><td>41 mod 4 = <strong>1</strong></td></tr>
        <tr><td class="label">Box Dimensions:</td><td><strong>Height:</strong> 20 rows | <strong>Width:</strong> 32 pixels (2 words) | <strong>Start Row:</strong> Row 41</td></tr>
        <tr><td class="label">Box Screen Address:</td><td><code>SCREEN + 32 * 41 = 16384 + 1312 = <strong>17696</strong></code></td></tr>
    </table>
</div>

<h2>1. Overview and Architecture</h2>
<p>
The Hack computer is a 16-bit Von Neumann architecture comprised of an ALU, two registers (<strong>A</strong> and <strong>D</strong>), a Program Counter (<strong>PC</strong>), 32K instruction memory (<strong>ROM32K</strong>), and 32K unified data memory (<strong>Memory</strong>) addressing 16K RAM, 8K Screen memory-mapped display, and the keyboard register.
</p>

<h2>2. Part A – Build and Test the Computer</h2>
<p>
All hardware chips were implemented in Hack HDL according to specification:
</p>
<ul>
    <li><strong>CPU.hdl:</strong> Implements complete instruction decode for A-instructions and C-instructions, ALU operation routing, destination writing (A, D, M), and jump condition branching logic (combining <code>zr</code> and <code>ng</code> flags).</li>
    <li><strong>Memory.hdl:</strong> Uses <code>DMux4Way</code> and <code>Mux4Way16</code> driven by <code>address[13..14]</code> to cleanly map the 16K RAM (0–16383), 8K Screen (16384–24575), and Keyboard (24576).</li>
    <li><strong>Computer.hdl:</strong> Glues together the CPU, Memory, and ROM32K in a closed loop.</li>
</ul>

<div class="screenshot-box">
    <img src="{img_cpu}" alt="CPU.tst Result">
    <div class="screenshot-caption">Figure 1: CPU.tst — Official Test Comparison Passed Successfully</div>
</div>

<div class="screenshot-box">
    <img src="{img_mem}" alt="Memory.tst Result">
    <div class="screenshot-caption">Figure 2: Memory.tst — Data RAM, Screen, and Keyboard Addressing Verified</div>
</div>

<div class="screenshot-box">
    <img src="{img_add}" alt="ComputerAdd.tst Result">
    <div class="screenshot-caption">Figure 3: ComputerAdd.tst — Executed Add.hack (RAM[0] = 2 + 3 = 5)</div>
</div>

<div class="screenshot-box">
    <img src="{img_max}" alt="ComputerMax.tst Result">
    <div class="screenshot-caption">Figure 4: ComputerMax.tst — Executed Max.hack (RAM[2] = max(3, 5) = 5)</div>
</div>

<div class="screenshot-box">
    <img src="{img_rect}" alt="ComputerRect.tst Result">
    <div class="screenshot-caption">Figure 5: ComputerRect.tst — Executed Rect.hack (Screen Rectangle Drawing Verified)</div>
</div>

<h2>3. Part B – Python Assembler (assembler.py)</h2>
<p>
A two-pass assembler in Python was developed:
</p>
<ul>
    <li><strong>Pass 1:</strong> Cleans comments (<code>//...</code>) and blank lines; records label definitions <code>(LABEL)</code> with their corresponding ROM instruction index. Detects duplicate labels for <code>K mod 3 = 2</code>.</li>
    <li><strong>Pass 2:</strong> Translates A-instructions (allocating user variables at RAM[16] upwards) and C-instructions (encoding comp, dest, and jump tables into 16-bit binary). Handles line-number error reporting for <code>K mod 3 = 1</code> and saves <code>symbols.txt</code> for <code>K mod 3 = 0</code>.</li>
</ul>

<h2>4. Part C – Box Program (Box.asm)</h2>
<p>
The program polls <code>RAM[24576]</code> (<code>KBD</code>). When a key is held down, it paints a black rectangle starting at Row 41 (RAM address 17696), 20 rows tall and 32 pixels wide (2 consecutive words per row). When released, it clears the area back to white.
</p>

<div class="screenshot-box">
    <img src="{img_box_pressed}" alt="Box Screen When Key Pressed">
    <div class="screenshot-caption">Figure 6: Box Display When Key Pressed (Row 41 to Row 60, Width: 32px Black Box)</div>
</div>

<div class="screenshot-box">
    <img src="{img_box_released}" alt="Box Screen When Key Released">
    <div class="screenshot-caption">Figure 7: Box Display When Key Released (Screen Completely Restored to White)</div>
</div>

<h2>5. One Mistake I Fixed</h2>
<div class="callout-mistake">
    <strong>Encountered Mistake:</strong><br>
    While writing the row increment loop in <code>Box.asm</code>, I wrote <code>M=M+D</code> to advance the row address:
    <pre>Line 93: invalid instruction: M=M+D
Assembly failed with errors.</pre>
    <strong>Cause:</strong> In the Hack ALU grammar, additions are mnemonically specified as <code>D+M</code> (or <code>D+A</code>). Although addition is mathematically commutative, standard Hack instruction sets mandate having register <code>D</code> as the first operand.<br><br>
    <strong>Fix:</strong> I updated <code>Box.asm</code> to <code>M=D+M</code>, and enhanced <code>assembler.py</code> to support commutative aliases (such as <code>M+D</code>, <code>A+D</code>, <code>M&D</code>) while maintaining strict adherence to the Hack ISA specification.
</div>

<h2>6. Viva Voce Preparation</h2>
<div class="viva-box">
    <strong>How to handle on-the-spot code modifications:</strong>
    <ul>
        <li><strong>Move the box down:</strong> Update the base address <code>@17696</code>. To shift down by 10 rows, add <code>32 * 10 = 320</code> &rarr; change to <code>@18016</code>.</li>
        <li><strong>Change width:</strong> Change <code>@col_count</code> initialization (e.g. from <code>@2</code> to <code>@3</code> for 48px).</li>
        <li><strong>Change height:</strong> Change <code>@row_count</code> initialization (e.g. from <code>@20</code> to <code>@30</code>).</li>
    </ul>
</div>

</body>
</html>
"""
    out_path = os.path.join(CAPSTONE_DIR, "REPORT.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated standalone HTML report: {out_path}")

if __name__ == "__main__":
    build_html_report()
