# 🖊️ AutoTyper – Reliable Speech & Clipboard-to-Typing Engine

AutoTyper is a browser-based automation engine that converts speech transcripts or clipboard text into precise, sequential, real-time typing inside the currently focused input field.
It is engineered with strict session isolation and async-safe execution to eliminate dropped characters, overlapping processes, and stale data reuse.

---

## 🎯 Core Objectives

* Ensure **zero character loss**
* Prevent **overlapping typing sessions**
* Eliminate **clipboard reuse bugs**
* Provide **instant force-stop control**
* Maintain **cursor position accuracy**
* Guarantee **state-safe execution**

---

## 🏗 System Architecture

AutoTyper is built around a deterministic session-control model.

### 1️⃣ Operation ID Isolation

Each typing session is assigned a unique `operationId`.

* Starting a new session invalidates all previous sessions.
* Every async loop checks against the active `operationId`.
* Prevents race conditions and ghost typing.

### 2️⃣ Single Source of Truth

* Text to be typed is stored in one dedicated variable.
* Clipboard is read **once** per session.
* Speech input uses **final transcripts only**.
* No dynamic reads during typing.

### 3️⃣ Sequential Async Typing Engine

* Strict `for` loop with awaited delay.
* No `setInterval`.
* No parallel promises.
* No `Promise.all`.

This guarantees deterministic character insertion order.

### 4️⃣ Safe Text Insertion Strategy

Instead of dispatching raw keyboard events (which can drop characters), AutoTyper:

* Directly modifies `element.value`
* Preserves `selectionStart` and `selectionEnd`
* Dispatches a synthetic `input` event
* Maintains cursor positioning

This ensures full reliability across browsers.

---

## 🚀 Features

* 🎤 Speech-to-text typing
* 📋 Clipboard-to-typing support
* 🛑 Instant force-stop mechanism
* 🔄 Automatic session invalidation
* 🧠 Async-safe execution model
* 🎯 Focus and cursor preservation
* ⚡ Adjustable typing speed (recommended 30–60ms)
* 🧹 Automatic state reset before every operation

---

## 🛑 Force Stop Mechanism

Force Stop performs:

* `operationId` increment
* Async loop invalidation
* State reset
* Pending task cancellation

Typing halts immediately, even mid-character loop.

---

## 📦 Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/autotyper.git
cd autotyper
```

### (Optional) Setup Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Application

Development:

```bash
python app.py
```

Production (recommended):

```bash
gunicorn app:app
```

---

## 🧪 Execution Flow

1. User triggers speech or paste event.
2. Previous session is force-stopped.
3. New `operationId` is generated.
4. Fresh text is stored.
5. Target element is validated and focused.
6. Sequential typing begins.
7. Each iteration checks session validity.
8. Completion or cancellation ends session cleanly.

---

## 🔒 Reliability Guarantees

✔ No character skipping
✔ No duplicated content
✔ No clipboard reuse
✔ No async overlap
✔ No ghost background typing
✔ Clean restart every time

---

## 🛠 Recommended Production Settings

* Typing delay: 35–50ms
* Enforce final speech results only
* Cancel session on tab visibility change (optional)
* Enable debug logs during development

---

## 📈 Future Enhancements

* Pause / Resume capability
* Humanized typing patterns
* Chrome Extension packaging
* Multi-language speech models
* Cloud deployment configuration

---

## 📄 License

MIT License – free to use and modify.

---

