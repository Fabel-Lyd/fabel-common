# Consuming the package
Add to Pipfile specifying release version (manually change correct version @1.1.0):
```
fabelcommon = {git = "https://github.com/Fabel-Lyd/fabel-common.git@1.1.0"}
```
# Releasing the package

1. All folders and **subfolders**, i.e., as they are called in Python `packages`, which are intended to be published as part of the common library, should contain files `__init__.py`.
2. Change file `setup.py`:
    1. update `version` using semantic versioning https://semver.org/ approach. For debugging purposes, use release candidates. 
    2. update `packages` (including subfolders)
3. Create GitHub Release and tag using the same version number:
    1. Release candidate - create a release from your feature branch
    2. Release - create the release after PR is approved and merged into the master
4. Cleanup redundant release candidates and their tags:
```commandline
git push --delete origin x.y.z 
```
