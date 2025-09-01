# Python `inspect` Module Notes

The `inspect` module in Python is used for **introspection**.  
It allows us to inspect live objects (functions, classes, methods, modules, etc.) and extract useful information.

---

## ✅ Why use `inspect`?
- Debugging: Understand how functions/classes are defined.
- Documentation: Extract docstrings and function signatures.
- Code analysis: Know what arguments a function accepts.
- Tools & frameworks: Frameworks like Django, Flask, etc., internally use `inspect` for introspection.

---

## 🔑 Common Functions of `inspect`

### 1. Get Function Signature
```python
import inspect

def greet(name, age=18):
    return f"Hello {name}, you are {age} years old."

print(inspect.signature(greet))
```
**Output:**
```
(name, age=18)
```

---

### 2. Get Docstring
```python
print(inspect.getdoc(greet))
```
**Output:**
```
This function greets a person.
```

---

### 3. Get Source Code
```python
print(inspect.getsource(greet))
```
**Output:**
```python
def greet(name, age=18):
    return f"Hello {name}, you are {age} years old."
```

---

### 4. Get Module of an Object
```python
print(inspect.getmodule(greet))
```
**Output:**
```
<module '__main__'>
```

---

### 5. Get Members of an Object
```python
print(inspect.getmembers(greet))
```
➡️ Returns a list of all attributes of the function.

---

### 6. Object Type Info
```python
print(inspect.isfunction(greet))  # True
print(inspect.isclass(list))      # True
```

---

## ⚠️ Common Error

If you try:
```python
inspect.getsource(my_object)
```
and `my_object` is an **instance** (not a class/function),  
you will get:
```
TypeError: module, class, method, function... was expected
```

✅ Fix → use `inspect.getsource(ClassName)` instead of `inspect.getsource(instance)`.

---

## 🛠 Real-Life Example
Suppose you are building a plugin system where users can provide custom functions.  
You can validate them using `inspect`:

```python
def user_function(x, y):
    return x + y

sig = inspect.signature(user_function)
if len(sig.parameters) != 2:
    print("❌ Function must accept 2 arguments")
else:
    print("✅ Function is valid")
```

---

## 📌 Summary
- `inspect` is a **microscope for Python code**.  
- It helps you explore functions, classes, and modules at runtime.  
- Very useful for debugging, documentation, and frameworks.
