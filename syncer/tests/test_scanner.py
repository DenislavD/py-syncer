import pytest

""" Test cases:

Failures:
- Instantiation: missing / wrong Strategy
- Missing source/target directory
- !! no rights to access file (get_hash)
- currently open file
- corrupted file

Integration:
- same contents output nothing (notify user no action)
- compare changed file
- check if superfluous files in target are marked for deletion
- whole directory missing (analyze actions taken)
- whole directory RENAMED only (what happens? - delete + copytree?)
- integration test with temp directories ?? - clarify
- large files (>300 MB ?)



"""