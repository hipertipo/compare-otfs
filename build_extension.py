# build RoboFont Extension

import os
import shutil

from mojo.extensions import ExtensionBundle

lib_path = os.path.dirname(__file__)
extension_file = 'CompareOTFs.roboFontExt'
extension_path = os.path.join(lib_path, extension_file)
# extension_html = os.path.join(lib_path, "_docs")
extension_lib_path = os.path.join(extension_path, 'lib')

print 'building extension...',
B = ExtensionBundle()
B.name = u"CompareOTFs"
B.developer = u'Gustavo Ferreira'
B.developerURL = 'http://hipertipo.com/'
B.version = "0.1"
B.mainScript = ""
B.launchAtStartUp = 0
B.addToMenu = [
    {
        'path' : 'compare-otfs.py',
        'preferredName' : 'CompareOTFs',
        'shortKey' : '',
    },
]
B.requiresVersionMajor = '1'
B.requiresVersionMinor = '5'
B.infoDictionary["html"] = 0
B.save(extension_path, libPath=lib_path, htmlPath=None, resourcesPath=None, pycOnly=False)
print 'done.\n'

print 'cleaning up extension files...'

# remove git repository from extension

if os.path.exists(extension_path):
    # remove git repository
    git_path = os.path.join(extension_lib_path, '.git')
    if os.path.exists(git_path):
        print '\tremoving git repository from extension...'
        shutil.rmtree(git_path)
    # remove gitignore file
    gitignore_path = os.path.join(extension_lib_path, '.gitignore')
    if os.path.exists(gitignore_path):
        print '\tremoving .gitignore file from extension...'
        os.remove(gitignore_path)

# remove extension from extension (!!)

if os.path.exists(extension_path):
    duplicate_extension_path = os.path.join(extension_lib_path, extension_file)
    if os.path.exists(duplicate_extension_path):
        print '\tremoving extension from extension...'
        shutil.rmtree(duplicate_extension_path)

# removing .pyc files from extension

if os.path.exists(extension_path):
    all_files = os.listdir(extension_lib_path)
    print '\tremoving .pyc files from extension...'
    for file_ in all_files:
        if os.path.splitext(file_)[1] == '.pyc':
            file_path = os.path.join(extension_lib_path, file_)
            os.remove(file_path)

print
print '...done.\n'
