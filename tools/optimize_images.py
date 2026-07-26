#!/usr/bin/env python3
"""Optimise toutes les images du dossier output pour le PDF Marp (< 5 Mo).
Redimensionne à max 1024px de large, convertit PNG en JPEG quand possible,
compresse JPEG à 80%. Les originaux sont sauvegardés dans output/_BACKUP/."""

import os
import shutil
from PIL import Image

IMAGES_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')
PHOTO_DIR = os.path.join(IMAGES_DIR, '_PHOTO')
BACKUP_DIR = os.path.join(IMAGES_DIR, '_BACKUP_OPTIM')
MAX_WIDTH = 1024
JPEG_QUALITY = 80

os.makedirs(BACKUP_DIR, exist_ok=True)

def optimize_image(filepath, max_width=MAX_WIDTH, quality=JPEG_QUALITY):
    """Redimensionne et compresse une image. Retourne (avant, apres) en octets."""
    size_before = os.path.getsize(filepath)

    # Backup
    relpath = os.path.relpath(filepath, IMAGES_DIR)
    backup_path = os.path.join(BACKUP_DIR, relpath.replace('/', '_'))
    if not os.path.exists(backup_path):
        shutil.copy2(filepath, backup_path)

    img = Image.open(filepath)

    # Redimensionner si trop large
    if img.width > max_width:
        ratio = max_width / img.width
        new_size = (max_width, int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    # Sauvegarder
    ext = os.path.splitext(filepath)[1].lower()
    if ext in ('.jpg', '.jpeg'):
        img.save(filepath, 'JPEG', quality=quality, optimize=True)
    elif ext == '.png':
        # PNG avec transparence : garder PNG mais optimiser
        if img.mode == 'RGBA':
            img.save(filepath, 'PNG', optimize=True)
        else:
            # PNG sans transparence : convertir en JPEG (gain majeur)
            # Sauf si c'est un schema/graphique (texte fin = garder PNG)
            basename = os.path.basename(filepath).lower()
            if any(k in basename for k in ['schema', 'graphique', 'nboc', 'cycle_etape', 'montecarlo']):
                # Schemas : garder PNG mais reduire taille
                img.save(filepath, 'PNG', optimize=True)
            else:
                # Photos/illustrations : convertir en JPEG
                rgb = img.convert('RGB')
                new_path = os.path.splitext(filepath)[0] + '.jpg'
                rgb.save(new_path, 'JPEG', quality=quality, optimize=True)
                if new_path != filepath:
                    os.remove(filepath)
                    filepath = new_path

    size_after = os.path.getsize(filepath)
    return size_before, size_after, filepath

# Traiter toutes les images racine output/
total_before = 0
total_after = 0
count = 0

for root, dirs, files in os.walk(IMAGES_DIR):
    # Skip backup et archive et raw
    if any(skip in root for skip in ['_BACKUP', 'ARCHIVE', '_RAW']):
        continue
    for f in sorted(files):
        if f.lower().endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(root, f)
            try:
                before, after, new_path = optimize_image(filepath)
                saving = (1 - after/before) * 100 if before > 0 else 0
                total_before += before
                total_after += after
                count += 1
                status = "OK" if saving > 5 else "skip"
                print(f"  {status} {os.path.relpath(new_path, IMAGES_DIR):50s} "
                      f"{before//1024:>6d} Ko -> {after//1024:>6d} Ko  ({saving:+.0f}%)")
            except Exception as e:
                print(f"  ERR {f}: {e}")

print()
print(f"{'='*60}")
print(f"  {count} images traitees")
print(f"  Avant : {total_before//1024:,d} Ko ({total_before/1024/1024:.1f} Mo)")
print(f"  Apres : {total_after//1024:,d} Ko ({total_after/1024/1024:.1f} Mo)")
print(f"  Gain  : {(total_before-total_after)//1024:,d} Ko ({(1-total_after/total_before)*100:.0f}%)")
print(f"  Originaux sauvegardes dans output/_BACKUP_OPTIM/")
