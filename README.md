# 🌄 DAMAVAND-lang

**DAMAVAND** is a programming language written in **Python** — created for fun, learning, and experimenting with interpreters.  
Now it also comes with its own **IDE** with syntax highlighting, file management, and a dark theme!  

---

## ✨ Features

- Variables (`a = 10`)
- Printing (`print`)
- Conditionals (`if / else`)
- Loops (`while`)
- Functions (`fff name(args)`)
- Comments (`//`)
- Basic error handling
- Run code from `.dam` files
- IDE with:
  - Syntax highlighting (keywords, numbers, strings, comments, operators)
  - Italic green comments
  - File menu (New, Open, Save, Save As)
  - Edit menu (Undo, Redo, Copy, Paste)
  - Dark theme

---

## 📦 Installation

Clone the repo:
```bash
git clone https://github.com/Artin-khodayari/DAMAVAND-lang.git
cd DAMAVAND-lang
```

### Run the interpreter:
```bash
python3 src/main.py examples/hello.dam
```

### Run the IDE:
```bash
python3 ide.py
```

---

## 📝 Syntax

### Variables
```damavand
a = 10
b = "DAMAVAND"
c = a + 5
```

### Printing
```damavand
print("Hello World")
print("Age: " + a)
```

### If statement
```damavand
if (x > 3) {
    print("x is big")
} else {
    print("x is small")
}
```

### While loop
```damavand
n = 3
while (n > 0) {
    print(n)
    n = n - 1
}
```

### Functions
**Note:To define a function, you have to use ``fff``**
**Why? This is a fun project, so ``fff`` means:**
---> ***Function For Fun*** ;)
```damavand
fff hello(name) {
    print("Hello, " + name)
}
```

### Comments
```damavand
# This is a comment
print("Hello")
```

---

## Example Program
```damavand
# DAMAVAND sample program
fff main() {
    a = 5
    b = 10

    if (a + b > 12) {
        print("Greater than 12")
    } else {
        print("Not greater")
    }

    while (a > 0) {
        print(a)
        a = a - 1
    }
}
```

### Example Output:
```
Greater than 12
5
4
3
2
1
```

---

**DAMAVAND started as a hobby, but it would be something more than a hobby.** 🚀  

---

# 🧑‍💻 About the Developer

This project is made by [Artin Khodayari](https://github.com/Artin-khodayari).  

📧 Contact: [Gmail-Account](mailto:ArtinKhodayari2010@gmail.com)  

***Feel free to reach out for questions, feedback, or collaborations!***

---

# 📄 License
**Also read [License](https://github.com/Artin-khodayari/DAMAVAND-lang/blob/main/License)**
