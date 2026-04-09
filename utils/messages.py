rep = 60

def done(message):
    print(f"✅ {message}.")

def error(message):
    print(f"❌ {message}.")

def warning(message):
    print(f"⚠️ {message}.")

def info(message):
    print(f"ℹ️ {message}.")

def waiting(message):
    print(f"⏳ {message}...")

def starting(message):
    print(f"🚀 {message}...")

def stopping(message):
    print(f"🛑 {message}...")

def cleaning(message):
    print(f"🧹 {message}...")

def copying(message):
    print(f"📁 {message}...")

def recording(message):
    print(f"🎥 {message}...")

def analyzing(message):
    print(f"🔍 {message}...")

def processing(message):
    print(f"⚙️ {message}...")

def finishing(message):
    print(f"🏁🎉 {message}... ")

def decompressing(message):
    print(f"📦 {message}...")

def item(message):
    print(f"📌 {message}")

def line_break():
    print("\n")

def separation_line():
    #🦠💀☣️👾🛡️☣☢️🚨
    print(f"👾"*rep)

def title(message):
    message = f" {message} "
    exedentes = (rep - len(message)) // 2    
    separation_line()
    print("⠀⠀ "*exedentes + message)
    separation_line()
    line_break()