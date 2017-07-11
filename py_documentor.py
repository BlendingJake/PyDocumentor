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
from os.path import isfile, isdir
from importlib import import_module
from inspect import getmembers, signature, isclass, isfunction, ismethod


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
        self._collected_data = {}

        if len(sys.argv) > 0 and sys.argv[0] == '-F':
            self._folder_mode = True
        else:
            self._folder_mode = False

        self._collect_file_names()
        self._import_modules()

        print(self._collected_data)

    def _collect_class_info(self, cls):
        inspected = getmembers(cls)
        data = {'methods': [], 'constants': [], 'static_methods': []}
        methods_functions = []
        method_dict = []

        # collect names of method and __dict__ to use to check for static methods
        for name, memb in inspected:
            if isfunction(memb) or ismethod(memb):
                methods_functions.append([name, memb])

            if name == '__dict__':
                method_dict = memb

        # use method_dict and names of functions or methods to determine whether it is a static function
        for name, memb in methods_functions:
            if name in method_dict:
                if isinstance(method_dict[name], staticmethod):
                    data['static_methods'].append(self._collect_function_info(memb))
                elif not callable(memb) and (len(name) < 2 or name[0:2] != "__"):  # is this a constant?
                    data['constants'].append({'name': name, 'val': memb})
                else:
                    data['methods'].append(self._collect_function_info(memb))

        return data

    def _collect_file_names(self):
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

    @staticmethod
    def _collect_function_info(func: callable):
        data = {'doc': func.__doc__ if func.__doc__ is not None else "", 'parameters': []}
        sig = signature(func)

        for param in sig.parameters.values():
            param_data = {'name': param.name, 'kind': param.kind}
            if param.default is not param.empty:
                param_data['default'] = param.default

            data['parameters'].append(param_data)

        return data

    def _collect_module_info(self, mod):
        inspected = getmembers(mod)
        data = {'classes': [], 'functions': []}

        for name, memb in inspected:
            if isclass(memb):
                data['classes'].append(self._collect_class_info(memb))
            elif isfunction(memb):
                data['functions'].append(self._collect_function_info(memb))

        return data

    def _import_modules(self):
        for file_name in self._file_names:
            try:
                mod = import_module(file_name)
                self._collected_data[file_name] = self._collect_module_info(mod)
            except ImportError as e:
                print(e)
                print("There was an error importing <{}>".format(file_name))
                quit()
