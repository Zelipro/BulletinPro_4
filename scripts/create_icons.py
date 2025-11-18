from PIL import Image
import os
from pathlib import Path

def create_app_icons():
    """Génère les icônes dans tous les formats"""
    
    project_root = Path(__file__).parent.parent
    logo_path = project_root / "assets" / "icons" / "logo.png"
    icons_dir = project_root / "assets" / "icons"
    
    # Créer un logo par défaut si inexistant
    if not logo_path.exists():
        print("⚠️  Logo manquant, création d'un logo par défaut...")
        img = Image.new('RGB', (512, 512), color='#2196F3')
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        draw.text((100, 200), "BP", fill='white', font=None)
    else:
        img = Image.open(logo_path)
    
    print("🎨 Génération des icônes...")
    
    # Windows .ico
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(icons_dir / "app_icon.ico", format='ICO', sizes=icon_sizes)
    print("  ✅ app_icon.ico")
    
    # Linux .png (multiples tailles)
    for size in [16, 32, 48, 64, 128, 256, 512]:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(icons_dir / f"app_icon_{size}x{size}.png")
        print(f"  ✅ app_icon_{size}x{size}.png")
    
    # Icône principale
    img.resize((512, 512), Image.Resampling.LANCZOS).save(icons_dir / "app_icon.png")
    print("  ✅ app_icon.png")
    
    print("\n✅ Toutes les icônes générées avec succès !")

if __name__ == "__main__":
    create_app_icons()
