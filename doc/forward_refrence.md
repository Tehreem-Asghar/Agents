# Python Type Hints, Future Annotations & Forward References  

## ❓ Question  
Jab hum ek simple function banate hain aur parameter ki type `str` set karte hain to hover par wo `str` bina quotes ke dikhata hai.  
Lekin `Agent` class me parameter ki type quotes ke andar (`"str"`) dikh rahi hai, aisa kyun hota hai?  

---

## ✅ Short Answer  
Ye is liye hota hai kyunki `Agent` class wali file me `from __future__ import annotations` use hua hai.  
Is import ki wajah se Python type hints ko turant resolve karne ke bajaye **string form me store karta hai** (jaise `"str"`), taa ke forward references handle kiye ja saken.  

---

## 🔹 Forward Reference  

### Definition (Simple Words Me)  
**Forward Reference** ka matlab hota hai jab tum type hint me **kisi aisi cheez ka naam use karo jo abhi code me define nahi hui**.  
Normally Python confuse ho jata hai, lekin `from __future__ import annotations` isko string ki tarah treat karke solve kar deta hai.  

---

### Example  

```python
# Without forward reference → Error
class School:
    def get_teacher(self) -> Teacher:   # Teacher abhi bana hi nahi
        return Teacher()

class Teacher:
    pass
```


```
# With forward reference → Works fine
from __future__ import annotations

class School:
    def get_teacher(self) -> "Teacher":   # Teacher baad me define hoga
        return Teacher()

class Teacher:
    pass


```



# Real Life Example

- Tum kisi dost ko bolo: “Kal ek naya teacher aayega.”
(Abhi teacher ka naam/shakl nahi pata → ye forward reference hai).

- Jab teacher kal aa jata hai tab sabko samajh aa jata hai kaun hai.