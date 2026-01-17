import PyInstaller.__main__
import customtkinter
import os
import platform

# Dosya yolları (Scriptin 'scripts' klasöründe veya rootta çalışmasına göre ayarla)
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir) if os.path.basename(script_dir) == "scripts" else script_dir

app_name = "BarkodPOS"
main_script = os.path.join(root_dir, "main.py")
icon_file = os.path.join(root_dir, "assets", "pos_icon.png")

# Çıktı klasörü (Root içinde 'dist' olsun)
dist_dir = os.path.join(root_dir, "dist")
work_dir = os.path.join(root_dir, "build")

# CustomTkinter kütüphanesinin yolu (Tema ve font dosyaları için gerekli)
ctk_path = os.path.dirname(customtkinter.__file__)

# İşletim sistemine göre ayırıcı (Windows için ; Linux/Mac için :)
separator = ";" if platform.system() == "Windows" else ":"

print("🔨.exe oluşturuluyor...")
print(f"📦 CustomTkinter yolu: {ctk_path}")

try:
    PyInstaller.__main__.run([
        main_script,
        f'--name={app_name}',
        '--onefile',
        '--windowed',
        f'--icon={icon_file}',
        f'--add-data={ctk_path}{separator}customtkinter',
        '--clean',
        '--noconfirm',
        f'--distpath={dist_dir}',
        f'--workpath={work_dir}',
        f'--specpath={work_dir}',
    ])
    
    print(f"\n✅ BAŞARILI! '{app_name}.exe' dosyası '{dist_dir}' yolunda oluşturuldu.")
    print("📝 Not: 'stock.db' veritabanı dosyası .exe ile aynı klasörde olmalı/oluşturulacaktır.")
    
except Exception as e:
    print(f"\n❌ HATA OLUŞTU: {e}")
    input("Çıkmak için Enter'a basın...")
