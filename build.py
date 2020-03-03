# build RoboFont Extension

import os
import shutil

from mojo.extensions import ExtensionBundle

version = 0.2

base_folder = os.path.dirname(__file__)
extension_filename = 'CompareOTFs.roboFontExt'
source_folder = os.path.join(base_folder, 'source')
extension_folder = os.path.join(base_folder, 'build')
extension_path = os.path.join(extension_folder, extension_filename)

if not os.path.exists(extension_folder):
    os.mkdir(extension_folder)

print('building extension...', end='')

B = ExtensionBundle()
B.name = "CompareOTFs"
B.developer = 'Gustavo Ferreira'
B.developerURL = 'http://hipertipo.com/'
B.version = str(version)
B.mainScript = ""
B.launchAtStartUp = 0
B.requiresVersionMajor = '1'
B.requiresVersionMinor = '5'
B.infoDictionary["html"] = 0
B.addToMenu = [{
    'path'          : 'compareOTFs.py',
    'preferredName' : 'CompareOTFs',
    'shortKey'      : '',
}]

B.save(extension_path, libPath=source_folder, htmlPath=None, resourcesPath=None, pycOnly=False)

print('done.\n')
