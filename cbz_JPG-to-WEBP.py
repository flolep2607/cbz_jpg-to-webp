import platform
import argparse
import glob
import os
import shutil
from pathlib import Path
from zipfile import ZipFile

from PIL import Image
from progressbar import ProgressBar

my_parser = argparse.ArgumentParser(
    description='Find and convert comics from jpg to webp')
my_parser.add_argument('file_path', help='file(cbz) path')
my_parser.add_argument('-b', '--backup', dest='backup_path', help='backup path')
my_parser.add_argument('-s', '--small', dest='small', help='Keep smaller file', action='store_true')

args = my_parser.parse_args()
backup = args.backup_path
small = args.small

Image.MAX_IMAGE_PIXELS = None

print('Select folder to scan for eComics...')
path = Path(args.file_path)
if backup:
    print('Select folder to store backups...',backup)
print('Creating list of comics to search.')
file_list = [str(pp) for pp in path.glob("**/*.cbz")]
jpg_list = []
badfiles = []

print(path)
def Contents():
    contents = [temp_path(os.path.join(temppath, f)) for f in os.listdir(temppath)]
    return contents

def temp_path(dos_path, encoding=None):
    path = os.path.abspath(dos_path)
    if platform.system()=='Linux':
        if path[0]=='/':return "/tmp" + path
        return "/tmp/" + path
    else:
        if path.startswith(u"\\\\"):
            return u"\\\\?\\UNC\\" + path[2:]
        return u"\\\\?\\" + path

def convert_image(image_path, image_type):
    im = Image.open(image_path)
    im = im.convert('RGB')
    image_name = image.replace('.jpg', '.webp')

    if image_type == 'jpg' or image_type == 'png':
        im.save(f"{image_name}", 'webp')
    else:
        print('Images are not of type jpg or png.')


pbar = ProgressBar()
print('Searching folder and subfolders for comics with jpg images.')
for file in pbar(file_list):
    try:
        MyZip = ZipFile(file)
        zipcontents = ZipFile.namelist(MyZip)
        if any('.jpg' in s for s in zipcontents):
            jpg_list.append(file)
    except:
        badfiles.append(file)

print('Found ', str(len(jpg_list)), ' out of ', str(
    len(file_list)), ' comics with jpg images.')

for cbz in jpg_list:
    splitpath = os.path.split(cbz)
    if backup:
        print('Saving backup of ', cbz)
        shutil.copy2(cbz, os.path.join(bupath, cbz))
    print('Converting ', splitpath[1])
    MyZip = ZipFile(cbz)
    NewZip = cbz + '.new'
    temppath = temp_path(os.path.join(splitpath[0], 'temp'))
    try:
        MyZip.extractall(path=temppath)
    except:
        shutil.rmtree(temppath)

    for root, directory, files in os.walk(temppath):
        for file in files:
            if file.startswith('._'):
                os.remove(os.path.join(root,file))

    # convert to webp
    images = [str(pp) for pp in Path(temppath).glob("**/*.jpg")]
    if len(images) == 0:
        print('No images to convert')
        continue
    print('Converting Images')
    pbar = ProgressBar()
    for image in pbar(images):
        if image.endswith('jpg') or image.endswith('jpeg'):
            try:
                convert_image(image, 'jpg')
            except:
                badfiles.append(cbz)

    # delete original images
    for file in images:
        path_to_file = os.path.join(temppath, file)
        os.remove(path_to_file)

    #contents = Contents()
    with ZipFile(NewZip, 'w') as archive:
        for root, directory, files in os.walk(temppath):
            for file in files:
                f = os.path.join(root,file)
                archive.write(f, os.path.relpath(f, temppath))

#     if backup:
#         print('Saving backup of ', splitpath[1])
#         shutil.copy2(cbz, os.path.join(bupath, cbz))

    if small:
        if os.path.getsize(NewZip) < os.path.getsize(cbz):
            shutil.move(NewZip, cbz)
        else:
            os.remove(NewZip)
    else:
        shutil.move(NewZip, cbz)

    shutil.rmtree(temppath)

if len(badfiles) > 0:
    print('Bad Zip Files:\n')
    for file in badfiles:
        print(file)
