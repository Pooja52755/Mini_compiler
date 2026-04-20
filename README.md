# 🧠 Mini Compiler (LEX + C)

## 📌 Overview

This project implements a **Mini Compiler** covering all major phases from the compiler design syllabus:

* Lexical Analysis using **LEX (Flex)**
* Syntax Analysis using **Recursive Descent Parser**
* LL(1) Parsing Table Generation
* SLR Parsing Table Generation
* Intermediate Code Generation (Three Address Code)
* Code Optimization (Basic)
* Target Code Generation (Assembly-like)

---

## 📁 Project Structure

```
MINI_COMPILER/
│
├── lexer.l            # Lexical Analyzer (LEX)
├── parser.c           # Recursive Descent Parser
├── ll1.c              # LL(1) Parsing Table
├── slr.c              # SLR Parsing Table
├── intermediate.c     # Intermediate Code Generation
├── optimizer.c        # Code Optimization
├── codegen.c          # Target Code Generation
├── main.c             # Driver (optional)
│
├── input.txt          # Sample input
```

---

## ⚙️ Requirements

* Linux / WSL / Ubuntu
* flex (LEX)
* gcc

### Install:

```
sudo apt update
sudo apt install flex gcc
```

---

## 🚀 How to Run (ALL COMMANDS)

### 1️⃣ Lexical Analysis

```
flex lexer.l
gcc lex.yy.c -o lexer -lfl
./lexer < input.txt
```

---

### 2️⃣ Parser (Recursive Descent)

```
gcc parser.c -o parser
./parser
```

---

### 3️⃣ LL(1) Parsing Table

```
gcc ll1.c -o ll1
./ll1
```

---

### 4️⃣ SLR Parsing Table

```
gcc slr.c -o slr
./slr
```

---

### 5️⃣ Intermediate Code Generation

```
gcc intermediate.c -o inter
./inter
```

---

### 6️⃣ Code Optimization

```
gcc optimizer.c -o opt
./opt
```

---

### 7️⃣ Target Code Generation

```
gcc codegen.c -o codegen
./codegen
```

---

## 🧪 Sample Input

```
a = b + c * d;
```

---

## 📤 Sample Output (Intermediate Code)

```
t1 = c * d
t2 = b + t1
a = t2
```

---

## ⚡ Features

* Token recognition using **regular expressions**
* Syntax validation using **LL(1) grammar**
* Table construction for **LL(1) and SLR**
* Intermediate code using **Three Address Code**
* Basic optimization (**constant folding**)
* Simple assembly-like **target code generation**

---

## 🎤 Viva Explanation (Short)

> This mini compiler implements lexical analysis using LEX, syntax analysis using recursive descent parsing, generates LL(1) and SLR parsing tables, produces intermediate three-address code, applies basic optimizations, and finally generates simple target assembly code.

---

## ⚠️ Notes

* This project is designed strictly as per **compiler design lab syllabus**
* Uses **simple grammar and limited language constructs**
* Focus is on demonstrating **compiler phases**, not full language support

---

## 👩‍💻 Author

Mini Compiler Lab Project
