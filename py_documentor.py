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

import sys
from os import walk, mkdir, sep
from os.path import isfile, isdir, split as path_split, exists as path_exists, join as path_join, abspath
import importlib.util
from inspect import getmembers, signature, isclass, isfunction, ismethod, Parameter
import re


class PyDocumentor:

    @staticmethod
    def _analyze_function_docs(doc: str):
        data = {}
        pattern = "(:\s*param |:\s*return:)"
        splt = re.split(pattern, doc)

        if not re.match(pattern, splt[0]):
            data['FUNCTION'] = splt[0].strip()
            del splt[0]

        for i in range(0, len(splt), 2):
            if ":" in splt[i + 1]:
                name, info = splt[i + 1].split(":", 1)
            else:
                name, info = '', splt[i + 1]

            if "param" in splt[i]:
                data[name.strip()] = info.strip()
            elif "return" in splt[i]:
                data["RETURN"] = info.strip()

        return data

    @staticmethod
    def _collect_class_info(cls):
        inspected = getmembers(cls)
        data = {
            'methods': [],
            'constants': [],
            'static_methods': [],
            'doc': cls.__doc__ if cls.__doc__ is not None else "",
            'name': cls.__name__
        }
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
                if isinstance(method_dict[name], staticmethod) and name[0] != "_":
                    data['static_methods'].append(PyDocumentor._collect_function_info(memb))
                elif not callable(memb) and not (len(name) > 2 or name[0:2] == "__"):  # is this a constant?
                    data['constants'].append({'name': name, 'value': memb})
                elif name[0] != "_" and not (len(name) > 2 and name[0:2] == "__"):  # make sure this isn't a private method
                    data['methods'].append(PyDocumentor._collect_function_info(memb))

        return data

    @staticmethod
    def _collect_function_info(func: callable):
        docs = PyDocumentor._analyze_function_docs(func.__doc__ if func.__doc__ is not None else "")
        data = {
            'name': func.__name__,
            'doc': docs['FUNCTION'] if 'FUNCTION' in docs else "",
            'parameters': [],
            'return': docs['RETURN'] if 'RETURN' in docs else ""
        }
        sig = signature(func)

        for param in sig.parameters.values():
            param_data = {'name': param.name, 'kind': param.kind}
            if param.default is not param.empty:
                param_data['default'] = param.default
            if param.name in docs:
                param_data['doc'] = docs[param.name]

            data['parameters'].append(param_data)

        return data

    @staticmethod
    def _collect_module_info(mod):
        inspected = getmembers(mod)
        data = {'classes': [], 'functions': [], 'name': mod.__name__}

        for name, memb in inspected:
            if isclass(memb) and memb.__module__ == mod.__name__:
                data['classes'].append(PyDocumentor._collect_class_info(memb))
            # if this is a function, make sure it wasn't imported, and that it isn't private
            elif isfunction(memb) and name[0] != "_" and memb.__module__ == mod.__name__:
                data['functions'].append(PyDocumentor._collect_function_info(memb))

        return data

    @staticmethod
    def _generate_class_html(cls: dict):
        out = [
            "<div class='class'>",
            "<h3>class {}</h3>".format(cls['name']),
            "<br><div class='class_body'>"
            "<p>{}</p>".format(cls['doc'])
        ]

        if len(cls['constants']):
            out.append("<h4>Constants</h4><div class='left_padded'>")
            for i in cls['constants']:
                out.append("<a class='constant'>{}: {}</a><br>".format(i['name'], i['value']))
            out.append('</div>')

        if len(cls['static_methods']):
            out.append("<h4>Static Methods</h4><div class='left_padded'>")
            for i in cls['static_methods']:
                out.append(PyDocumentor._generate_function_html(i))
            out.append('</div>')

        if len(cls['methods']):
            out.append("<h4>Methods</h4><div class='left_padded'>")
            for i in cls['methods']:
                out.append(PyDocumentor._generate_function_html(i))
            out.append('</div>')

        out.append("</div></div>")

        return "\n".join(out)

    @staticmethod
    def _generate_function_html(func: dict):
        return '\n'.join([
            "<div class='function'>",
            "<a class='function_title'>{}</a>".format(PyDocumentor._generate_function_signature(func)),
            "<div class='function_body'>"
            "<p class='function_doc'>{}</p>".format(func['doc']),
            PyDocumentor._generate_parameters_html(func['parameters']),
            "<p class='parameter'><a>return:</a> " + func['return'] + "</p>" if func['return'] != '' else "",
            "</div></div>"
        ])

    @staticmethod
    def _generate_function_signature(func):
        title = "{}(".format(func['name'])
        params = []

        for i in func['parameters']:
            temp = i['name']

            if 'default' in i:
                temp += '={}'.format(i['default'] if i['default'] != "" else '""')

            if i['kind'] == Parameter.VAR_POSITIONAL:
                temp = "*{}".format(i['name'])
            elif i['kind'] == Parameter.VAR_KEYWORD:
                temp = "**{}".format(i['name'])

            params.append(temp)

        return title + ", ".join(params) + ")"

    @staticmethod
    def _generate_parameters_html(parameters: dict):
        out = []
        for i in parameters:
            if i['name'] not in ('self', 'cls'):
                if 'default' in i.keys():
                    out.append("<p class='parameter'><a>{} (optional):</a> {}</p>".format(
                        i['name'],
                        i['doc'] if 'doc' in i else ""
                    ))
                else:
                    out.append("<p class='parameter'><a>{}:</a> {}</p>".format(i['name'],
                                                                               i['doc'] if 'doc' in i else ""))

        return "\n".join(out)

    @staticmethod
    def _input_to_bool(yes_no):
        return yes_no in ("yes", "y")

    @staticmethod
    def _user_input(prompt, error="", validator=None):
        while True:
            result = input(prompt + ": ")

            if validator is None or (validator is not None and validator(result)):
                return result
            else:
                print("<{}>".format(error), end="\n\n")

    def __init__(self):
        self._collected_data = {}
        self._folder_mode = '-F' in sys.argv
        self._advanced_mode = '-A' in sys.argv

        self._collect_file_names()
        modules = self._import_modules()

        # collect module info
        for mod in modules:
            self._collected_data[mod.__file__] = self._collect_module_info(mod)

        # get export settings from user
        self._get_user_options()

    def _collect_file_names(self):
        if self._folder_mode:
            folder_path = self._user_input("Folder Path", "Invalid folder path", isdir)
            self._directory = folder_path
            self._file_paths = []

            # walk through sub-directories and collect python files
            for (dirpath, dirnames, file_names) in walk(folder_path):
                for filename in file_names:
                    if filename.endswith(".py"):
                        self._file_paths.append(dirpath + filename)
        else:
            file_path = self._user_input("File Path", "Invalid file path", isfile)
            self._directory, _ = path_split(file_path)
            self._file_paths = [file_path]

    def _generate_css(self):
        if self._advanced_mode and not self._add_css_to_html:
            return "<head><link rel='stylesheet' type='text/css' href='style.css'></head>"
        else:
            # generate in-line css
            css_file_path = path_split(__file__)[0] + sep + "style.css"
            css_file = open(css_file_path, 'r')

            css = "".join([line for line in css_file.readlines()])
            css_file.close()
            return "<head><style>{}</style></head>".format(css)

    def _generate_module_html(self, mod):
        out = [
            PyDocumentor._generate_css(self),
            "<div class='module_header'><h2>{}.py</h2></div><div class='module'>".format(mod['name'])
        ]

        for func in mod['functions']:
            out.append(PyDocumentor._generate_function_html(func))

        for cls in mod['classes']:
            out.append(PyDocumentor._generate_class_html(cls))

        out.append("</div>")
        return "\n".join(out)

    def _get_user_options(self):
        # output directory
        out_d = self._user_input("Output Directory (leave blank to export where modules are)", "Invalid directory",
                                 isdir)
        self._output_directory = out_d if out_d != "" else self._directory

        # export folder name
        self._output_folder_name = self._user_input("Output Folder Name")
        print()

        # advanced options
        self._add_css_to_html = True

        if self._advanced_mode:
            # css settings
            self._add_css_to_html = self._input_to_bool(self._user_input("Add CSS to Each File Y/N",
                                                                         "Answer must be yes or no",
                                                                         lambda x: x.lower() in ("yes", "no", "y", "n")
                                                                         ))

    def _import_modules(self):
        modules = []

        for file_path in self._file_paths:
            try:
                _, file_name = path_split(file_path)
                file_name = file_name.split('.')[0]

                module_spec = importlib.util.spec_from_file_location(file_name, file_path)
                mod = importlib.util.module_from_spec(module_spec)
                module_spec.loader.exec_module(mod)
                modules.append(mod)
            except ImportError as e:
                print("There was an error importing <{}>".format(file_path))
                quit()

        return modules

    def export(self):
        # create export directory
        dir_path = self._output_directory + sep + self._output_folder_name
        if not path_exists(dir_path):
            try:
                mkdir(dir_path)
            except PermissionError:
                print("<PermissionError trying to create folder <{}>>".format(dir_path))
                exit()

        self.export_as_html()

        print("\nExport Successful!\nExiting...")

    def export_as_html(self):
        out_d = self._output_directory + sep + self._output_folder_name

        for file_path in self._collected_data.keys():
            folder, file_name_ext = path_split(file_path)
            file_name = str(file_name_ext.split('.')[0])
            new_fp = path_join(out_d, file_name + '.html')

            file = open(new_fp, 'w')
            module_str = self._generate_module_html(self._collected_data[file_path])
            file.write(module_str)
            file.close()

            if self._advanced_mode and not self._add_css_to_html:
                # write css file
                css_file_path = path_split(__file__)[0] + sep + "style.css"
                css_file = open(css_file_path, 'r')

                to_css_file_path = path_join(out_d, 'style.css')
                to_css_file = open(to_css_file_path, 'w')

                for line in css_file.readlines():
                    to_css_file.write(line)

                css_file.close()
                to_css_file.close()

if __name__ == "__main__":
    docker = PyDocumentor()
    docker.export()
