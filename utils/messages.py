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

def pin(message):
    print(f"   📌 {message}")

def options(message):
    print(f"▶️  {message}")

def list(message):
    print(f"📋 {message}")

def wait_key():
    input("\n--- Presione Enter para continuar ---")

def item(message):
    print(f"   > {message}")

def alarm(message):
    print(f"🚨 {message}.")

def line_break(rep):
    for i in range(rep):
        print("\n")

def separation_detault_line():
    separation_specific_line("alien")

def separation_specific_line(grapic):
    #🦠💀☣️👾🛡️☣☢️🚨
    match(grapic):
        case "virus":
            print(f"🦠"*rep)
        case "skull":
            print(f"💀"*rep)
        case "biohazard":            
            print(f"☣️ "*rep)
        case "alien":
            print(f"👾"*rep)
        case "shield":
            print(f"🛡️"*rep)
        case "radioactive":
            print(f"☢️ "*rep)
        case "alarm":
            print(f"🚨"*rep)

def title(message):
    message = f" {message} "
    exedentes = (rep - len(message)) // 2    
    separation_detault_line()
    print("⠀⠀ "*exedentes + message)
    separation_detault_line()
    line_break(1)