# PyDocumentor is a command-line script to create HTML documentation for Python
# Copyright (C) 2017 Jacob Morris
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from inspect import signature
import sys
from os import walk
from os.path import isfile, join, isdir


class PyDocumentor:

    @staticmethod
    def _user_input(prompt, error="", validator=None):
        result = None
        while result is None:
            result = input(prompt + ": ")

            if validator is not None and validator(result):
                break
            else:
                print(error, end="\n\n")

        return result

    def __init__(self):
        if len(sys.argv) > 0 and sys.argv[0] == '-F':
            self._folder_mode = True
        else:
            self._folder_mode = False

        self._collect_filenames()

    def _collect_filenames(self):
        if self._folder_mode:
            folder_path = self._user_input("Folder Path")
            if isdir(folder_path):
                self._file_names = []

                # walk through sub-directories and collect python files
                for (dirpath, dirnames, file_names) in walk(folder_path):
                    for filename in file_names:
                        if filename.endswith(".py"):
                            self._file_names.append(dirpath + filename)
        else:
            file_path = self._user_input("File Path")
            if isfile(file_path):
                self._file_names = [file_path]
