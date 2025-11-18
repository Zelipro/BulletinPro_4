#!/usr/bin/env python3
"""Crée la structure .deb pour Ubuntu/Debian"""

import os
import shutil
from pathlib import Path

def create_deb_structure():
    project_root = Path(__file__).parent.parent
    dist_dir = project_root / "dist"
    pkg_dir = dist_dir / "bulletinpro-1.0.0"
    
    print("📦 Création de la structure .deb...")
    
    # Créer l'arborescence
    dirs = [
        pkg_dir / "DEBIAN",
        pkg_dir / "usr" / "bin",
        pkg_dir / "usr" / "share" / "applications",
        pkg_dir / "usr" / "share" / "pixmaps",
    ]
    
    for size in [16, 32, 48, 64, 128, 256, 512]:
        dirs.append(pkg_dir / "usr" / "share" / "icons" / "hicolor" / f"{size}x{size}" / "apps")
    
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Fichier DEBIAN/control
    control = """Package: bulletinpro
Version: 1.0.0
Section: education
Priority: optional
Architecture: amd64
Depends: libc6 (>= 2.31), libgtk-3-0
Maintainer: Votre Nom <votre@email.com>
Homepage: https://github.com/votre-username/BulletinPro
Description: Système de gestion de bulletins scolaires
 BulletinPro est une application complète pour la gestion
 des notes, élèves, professeurs et génération de bulletins
 scolaires au format PDF.
"""
    
    with open(pkg_dir / "DEBIAN" / "control", "w") as f:
        f.write(control)
    
    # Fichier .desktop
    desktop = """[Desktop Entry]
Version=1.0
Type=Application
Name=BulletinPro
GenericName=Gestion de Bulletins Scolaires
Comment=Gérez les notes et bulletins de votre établissement
Exec=/usr/bin/bulletinpro
Icon=bulletinpro
Terminal=false
Categories=Education;Office;
Keywords=école;notes;bulletins;
StartupNotify=true
"""
    
    with open(pkg_dir / "usr" / "share" / "applications" / "bulletinpro.desktop", "w") as f:
        f.write(desktop)
    
    # Scripts post-installation
    postinst = """#!/bin/bash
set -e
gtk-update-icon-cache /usr/share/icons/hicolor -f > /dev/null 2>&1 || true
update-desktop-database /usr/share/applications > /dev/null 2>&1 || true
echo "✅ BulletinPro installé avec succès !"
exit 0
"""
    
    postinst_path = pkg_dir / "DEBIAN" / "postinst"
    with open(postinst_path, "w") as f:
        f.write(postinst)
    os.chmod(postinst_path, 0o755)
    
    # Copier l'exécutable
    exe_src = dist_dir / "bulletinpro"
    exe_dst = pkg_dir / "usr" / "bin" / "bulletinpro"
    if exe_src.exists():
        shutil.copy2(exe_src, exe_dst)
        os.chmod(exe_dst, 0o755)
        print("  ✅ Exécutable copié")
    
    # Copier les icônes
    icons_dir = project_root / "assets" / "icons"
    for size in [16, 32, 48, 64, 128, 256, 512]:
        icon_src = icons_dir / f"app_icon_{size}x{size}.png"
        icon_dst = pkg_dir / "usr" / "share" / "icons" / "hicolor" / f"{size}x{size}" / "apps" / "bulletinpro.png"
        if icon_src.exists():
            shutil.copy2(icon_src, icon_dst)
    
    # Copier vers pixmaps
    main_icon = icons_dir / "app_icon.png"
    if main_icon.exists():
        shutil.copy2(main_icon, pkg_dir / "usr" / "share" / "pixmaps" / "bulletinpro.png")
    
    print("✅ Structure .deb créée avec succès !")

if __name__ == "__main__":
    create_deb_structure()
