import os
import sys
import time
import json
import sqlite3
import zipfile
import shutil
import requests

try:
    from fastapi import FastAPI, UploadFile, File, Form, HTTPException
    from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
    import uvicorn
except ImportError:
    print("Eksik kütüphaneler var! Lütfen çalıştırın: pip install fastapi uvicorn requests python-multipart")
    sys.exit(1)

CONFIG_FILE = "config.json"
DB_FILE = "ykdos.db"

def cli_setup():
    if os.path.exists(CONFIG_FILE):
        return

    print("\n" + "="*80)
    welcome_text = """Merhaba, sistemimize hoş geldiniz!

Bu sistem Telegram'ın sınırsız depolamasını kullanarak size ücretsiz bir dosya 
sistemi sunar. Yani verilerinizi, dosyalarınızı bu sisteme yükleyebilirsiniz. 

Sistemin sınırsız hafızası vardır ancak sisteme tek seferde yalnızca 1 GB 
boyutunda dosya yükleyebilirsiniz. Bunun için bir Telegram hesabına, sistemi 
tek kullanacaksanız 1 bota, ama birden fazla kullanacaksanız 1'den fazla bota 
ihtiyacınız olacak.

Enter tuşuna basarak bot tokeninizi girebilirsiniz. Bot tokeninizi girdikten 
sonra Enter tuşuna basarak daha fazla bot ekleyebilirsiniz ve bot token girme 
yani bot ekleme işleminizi bitirdikten sonra 2 kere Enter tuşuna basınız.

NOT: Sisteme eklediğiniz bütün botların tek grupta veya kanalda olması 
gerekmektedir. Kanalı veya grubu gizli yapmanız önerilir, aksi takdirde 
verileriniz çalınabilir.

İyi kullanımlar dilerim! - Yasin Emir KAHYA"""
    print(welcome_text)
    print("="*80)
    input("\nDevam etmek için Enter tuşuna basınız...")

    bot_tokens = []
    print("\n--- Bot Token Ekleme Modu ---")
    empty_enter_count = 0
    
    while True:
        token = input(f"Bot Token #{len(bot_tokens) + 1} (Bitirmek için boş bırakıp Enter'a basın): ").strip()
        if token == "":
            empty_enter_count += 1
            if empty_enter_count >= 2 or (len(bot_tokens) > 0 and empty_enter_count >= 1):
                break
        else:
            empty_enter_count = 0
            bot_tokens.append(token)
            print(f"✅ Bot Token #{len(bot_tokens)} eklendi.")

    if not bot_tokens:
        print("❌ Hiç bot tokeni girilmedi!")
        sys.exit(1)

    chat_id = input("\nHedef Telegram Grup veya Kanal ID'sini giriniz (Örn: -100123456789): ").strip()

    config = {
        "bot_tokens": bot_tokens,
        "chat_id": chat_id,
        "current_bot_index": 0
    }
    
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
    time.sleep(2)

def init_db():
    os.makedirs(TEMP_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            file_size INTEGER,
            telegram_file_id TEXT,
            bot_token TEXT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sitename TEXT UNIQUE,
            file_mapping TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

app = FastAPI()

def get_next_bot():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
    tokens = config["bot_tokens"]
    idx = config["current_bot_index"]
    token = tokens[idx]
    config["current_bot_index"] = (idx + 1) % len(tokens)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
    return token, config["chat_id"]

@app.get("/", response_class=HTMLResponse)
def read_index():
    if os.path.exists("YKDOS.html"):
        with open("YKDOS.html", "r", encoding="utf-8") as f:
            return f.read()
    return "YKDOS.html bulunamadı!"

@app.get("/api/files")
def list_files():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, file_size FROM files ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return JSONResponse(content={"files": [{"id": r[0], "name": r[1], "size": r[2]} for r in rows]})

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    file_size = len(contents)
    if file_size > 1073741824:
        raise HTTPException(status_code=400, detail="Dosya boyutu 1 GB sınırını aşamaz!")

    token, chat_id = get_next_bot()
    res = requests.post(f"https://api.telegram.org/bot{token}/sendDocument", data={'chat_id': chat_id}, files={'document': (file.filename, contents)}).json()
    if not res.get("ok"):
        raise HTTPException(status_code=500, detail="Telegram yükleme hatası.")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO files (filename, file_size, telegram_file_id, bot_token) VALUES (?, ?, ?, ?)", 
                   (file.filename, file_size, res["result"]["document"]["file_id"], token))
    conn.commit()
    conn.close()
    return {"status": "success", "filename": file.filename}

@app.get("/api/download/{file_id}")
def download_file(file_id: int):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT filename, telegram_file_id, bot_token FROM files WHERE id = ?", (file_id,))
    row = cursor.fetchone()
    conn.close()
    if not row: raise HTTPException(status_code=404, detail="Bulunamadı")
    
    res = requests.get(f"https://api.telegram.org/bot{row[2]}/getFile?file_id={row[1]}").json()
    return RedirectResponse(url=f"https://api.telegram.org/file/bot{row[2]}/{res['result']['file_path']}")

@app.delete("/api/file/{file_id}")
def delete_file(file_id: int):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}

# --- TELEGRAM TABANLI AKILLI SİTE HOSTING MİMARİSİ (Bu bölüm daha sonradan gelebilecek bir özelliktir ama gelmeyedebilir büyük ihtimalle gelmicek) ---
@app.get("/api/sites")
def list_sites():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT sitename FROM sites ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return JSONResponse(content={"sites": [{"name": r[0], "url": f"/{r[0]}"} for r in rows]})

@app.post("/api/upload-site")
async def upload_site(site_name: str = Form(...), files: list[UploadFile] = File(...)):
    clean_name = site_name.lower().strip().replace(" ", "_")
    temp_path = os.path.join(TEMP_DIR, clean_name)
    
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)
    os.makedirs(temp_path, exist_ok=True)

    extracted_files = []
    for file in files:
        filename = file.filename.replace("\\", "/")
        if "/" in filename:
            filename = "/".join(filename.split("/")[1:])
        if not filename: continue
        
        dest_path = os.path.join(temp_path, filename)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        contents = await file.read()
        with open(dest_path, "wb") as f:
            f.write(contents)
        extracted_files.append(filename)

    for f in extracted_files:
        if f.endswith(".zip"):
            zip_full = os.path.join(temp_path, f)
            with zipfile.ZipFile(zip_full, 'r') as z:
                z.extractall(temp_path)
            os.remove(zip_full)

    file_mapping = {}
    all_local_files = []
    for root, dirs, fnames in os.walk(temp_path):
        for fn in fnames:
            rel_path = os.path.relpath(os.path.join(root, fn), temp_path).replace("\\", "/")
            all_local_files.append(rel_path)
            
            token, chat_id = get_next_bot()
            with open(os.path.join(root, fn), "rb") as f_in:
                file_bytes = f_in.read()
            
            res = requests.post(
                f"https://api.telegram.org/bot{token}/sendDocument", 
                data={'chat_id': chat_id}, 
                files={'document': (fn, file_bytes)}
            ).json()
            
            if res.get("ok"):
                file_mapping[rel_path] = {
                    "file_id": res["result"]["document"]["file_id"],
                    "token": token
                }

    lower_map = {k.lower(): k for k in file_mapping.keys()}
    index_key = None
    
    if "index.html" in lower_map:
        index_key = lower_map["index.html"]
    else:
        html_keys = [k for k in file_mapping.keys() if k.endswith(".html")]
        if html_keys:
            index_key = html_keys[0]

    if index_key and index_key != "index.html":
        file_mapping["index.html"] = file_mapping[index_key]

    shutil.rmtree(temp_path)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO sites (sitename, file_mapping) VALUES (?, ?)", 
                   (clean_name, json.dumps(file_mapping)))
    conn.commit()
    conn.close()

    return {"status": "success", "site_name": clean_name, "url": f"/{clean_name}"}

@app.get("/{sitename}", response_class=HTMLResponse)
@app.get("/{sitename}/{path:path}")
def serve_site_file(sitename: str, path: str = "index.html"):

    if sitename in ["api", "favicon.ico"]:
        raise HTTPException(status_code=404, detail="Bulunamadı")

    if not path:
        path = "index.html"
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT file_mapping FROM sites WHERE sitename = ?", (sitename,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Site bulunamadı")
        
    file_mapping = json.loads(row[0])
    
    target_file = None
    if path in file_mapping:
        target_file = path
    else:
        path_lower = path.lower()
        for k in file_mapping.keys():
            if k.lower() == path_lower:
                target_file = k
                break
                
    if not target_file:
        raise HTTPException(status_code=404, detail="Dosya bulunamadı")
        
    file_info = file_mapping[target_file]
    
    res = requests.get(f"https://api.telegram.org/bot{file_info['token']}/getFile?file_id={file_info['file_id']}").json()
    if not res.get("ok"):
        raise HTTPException(status_code=500, detail="Telegram'dan dosya alınamadı")
        
    file_url = f"https://api.telegram.org/file/bot{file_info['token']}/{res['result']['file_path']}"
    return RedirectResponse(url=file_url)

@app.get("/api/download-site/{sitename}")
def download_site_zip(sitename: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT file_mapping FROM sites WHERE sitename = ?", (sitename,))
    row = cursor.fetchone()
    conn.close()
    if not row: raise HTTPException(status_code=404, detail="Site bulunamadı")
    
    file_mapping = json.loads(row[0])
    temp_zip_dir = os.path.join(TEMP_DIR, f"dl_{sitename}")
    os.makedirs(temp_zip_dir, exist_ok=True)
    
    for rel_path, info in file_mapping.items():
        if rel_path == "index.html": continue
        res = requests.get(f"https://api.telegram.org/bot{info['token']}/getFile?file_id={info['file_id']}").json()
        if res.get("ok"):
            file_bytes = requests.get(f"https://api.telegram.org/file/bot{info['token']}/{res['result']['file_path']}").content
            dest = os.path.join(temp_zip_dir, rel_path)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(file_bytes)
                
    shutil.make_archive(sitename, 'zip', temp_zip_dir)
    shutil.rmtree(temp_zip_dir)
    return FileResponse(f"{sitename}.zip", filename=f"{sitename}.zip")

@app.delete("/api/site/{sitename}")
def delete_site(sitename: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sites WHERE sitename = ?", (sitename,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}

if __name__ == "__main__":
    try:
        cli_setup()
        init_db()
        port = int(os.environ.get("PORT", 5000))
        print("\n" + "="*50)
        print("🚀 Sisteminiz Hazır!")
        print(f"Tarayıcınızda açın: http://127.0.0.1:{port}")
        print("="*50 + "\n")
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"\nHata: {e}")
        input("Çıkmak için Enter tuşuna basın...")