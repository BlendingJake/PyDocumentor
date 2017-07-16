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

from os import walk, mkdir, sep
from os.path import isfile, isdir, split as path_split, exists as path_exists, join as path_join
import importlib.util
from inspect import getmembers, signature, isclass, isfunction, ismethod, Parameter
import re


class Formatter:
    FILE_EXT = ""

    def __init__(self, options):
        self.options = options

    def free_run(self) -> None:
        pass

    def top_of_file(self) -> str:
        return ""

    # --------------------------------------------------------------------------------
    # MISC
    # --------------------------------------------------------------------------------
    @classmethod
    def general_function_signature(cls, func_name, parameters):
        title = "{}(".format(func_name)
        params = []

        for i in parameters:
            temp = i['name']

            if 'default' in i:
                temp += '={}'.format(i['default'] if i['default'] != "" else '""')

            if i['kind'] == Parameter.VAR_POSITIONAL:
                temp = "*{}".format(i['name'])
            elif i['kind'] == Parameter.VAR_KEYWORD:
                temp = "**{}".format(i['name'])

            params.append(temp)

        return title + ", ".join(params) + ")"

    # ---------------------------------------------------------------------------------
    # MODULES
    # ---------------------------------------------------------------------------------
    @classmethod
    def module_title(cls, title, prefix="", indent=0):
        return ""

    @classmethod
    def module_start(cls, indent=0):
        return ""

    @classmethod
    def module_end(cls, indent=0):
        return ""

    # ---------------------------------------------------------------------------------
    # TABLE OF CONTENTS
    # ---------------------------------------------------------------------------------
    @classmethod
    def table_of_contents_start(cls, indent=0):
        return ""

    @classmethod
    def table_of_contents_title(cls, prefix="", indent=0):
        return ""

    @classmethod
    def table_of_contents_body_start(cls, indent=0):
        return ""

    @classmethod
    def table_of_contents_function(cls, name, static=False, prefix="", indent=0):
        return ""

    @classmethod
    def table_of_contents_class(cls, name, prefix="", indent=0):
        return ""

    @classmethod
    def table_of_contents_class_start(cls, indent=0):
        return ""

    @classmethod
    def table_of_contents_constant(cls, name, prefix="", indent=0):
        return ""

    @classmethod
    def table_of_contents_class_end(cls, indent=0):
        return ""

    @classmethod
    def table_of_contents_body_end(cls, indent=0):
        return ""

    @classmethod
    def table_of_contents_end(cls, indent=0):
        return ""

    # ---------------------------------------------------------------------------------
    # FUNCTIONS
    # ---------------------------------------------------------------------------------
    @classmethod
    def function_block_start(cls, indent=0):
        return ""

    @classmethod
    def function_start(cls, indent=0):
        return ""

    @classmethod
    def function_signature(cls, func_name: str, parameters: list, prefix="", indent=0):
        return ""

    @classmethod
    def function_body_start(cls, indent=0):
        return ""

    @classmethod
    def function_doc(cls, func_doc: str, indent=0):
        return ""

    @classmethod
    def function_parameters(cls, parameters: list, indent=0):
        return ""

    @classmethod
    def function_return_parameter(cls, return_doc, indent=0):
        return ""

    @classmethod
    def function_body_end(cls, indent=0):
        return ""

    @classmethod
    def function_end(cls, indent=0):
        return ""

    @classmethod
    def function_block_end(cls, indent=0):
        return ""

    # ---------------------------------------------------------------------------------
    # CLASSES
    # ---------------------------------------------------------------------------------
    @classmethod
    def class_start(cls, indent=0):
        return ""

    @classmethod
    def class_title(cls, title, prefix="", indent=0):
        return ""

    @classmethod
    def class_body_start(cls, indent=0):
        return ""

    @classmethod
    def class_doc(cls, doc, indent=0):
        return ""

    # CONSTANTS
    @classmethod
    def class_constants_title(cls, prefix="", indent=0):
        return ""

    @classmethod
    def class_constants_start(cls, indent=0):
        return ""

    @classmethod
    def class_constant(cls, name, value, prefix="", indent=0):
        return ""

    @classmethod
    def class_constants_end(cls, indent=0):
        return ""

    # EXTRA TITLES
    @classmethod
    def static_function_title(cls, prefix="", indent=0):
        return ""

    @classmethod
    def methods_title(cls, prefix="", indent=0):
        return ""

    @classmethod
    def class_body_end(cls, indent=0):
        return ""

    @classmethod
    def class_end(cls, indent=0):
        return ""


class HtmlFormatter(Formatter):
    FILE_EXT = ".html"

    def __init__(self, options):
        super(HtmlFormatter, self).__init__(options)
        self.css = ""

    def free_run(self):
        if self.options.add_css_to_each_file:
            # generate in-line css
            css_file_path = path_split(__file__)[0] + sep + "style.css"
            css_file = open(css_file_path, 'r')

            self.css = "".join([line for line in css_file.readlines()])
            css_file.close()

    def top_of_file(self):
        if self.options.add_css_to_each_file:
            return "<head><style>{}</style></head>".format(self.css)
        else:
            return "<head><link rel='stylesheet' type='text/css' href='style.css'></head>"

    # ---------------------------------------------------------------------------------
    # MODULES
    # ---------------------------------------------------------------------------------
    @classmethod
    def module_title(cls, title, prefix="", indent=0):
        return "<div class='module_header'><h2>{}.py</h2></div>".format(title)

    @classmethod
    def module_start(cls, indent=0):
        return "<div class='module'>"

    @classmethod
    def module_end(cls, indent=0):
        return "</div>"

    # ---------------------------------------------------------------------------------
    # TABLE OF CONTENTS
    # ---------------------------------------------------------------------------------
    @classmethod
    def table_of_contents_start(cls, indent=0):
        return "<div class='table_of_contents'>"

    @classmethod
    def table_of_contents_title(cls, prefix="", indent=0):
        return "<h3>Table of Contents</h4>"

    @classmethod
    def table_of_contents_body_start(cls, indent=0):
        return "<div class='left_padded'>"

    @classmethod
    def table_of_contents_function(cls, name, static=False, prefix="", indent=0):
        if static:
            return "<a href='#{}.{}'>{}.{}() (static)</a><br>".format(prefix, name, prefix, name)
        else:
            return "<a href='#{}.{}'>{}.{}()</a><br>".format(prefix, name, prefix, name)

    @classmethod
    def table_of_contents_class(cls, name, prefix="", indent=0):
        return "<a href='#{}.{}'>{}.{}</a>".format(prefix, name, prefix, name)

    @classmethod
    def table_of_contents_class_start(cls, indent=0):
        return "<div class='class'>"

    @classmethod
    def table_of_contents_constant(cls, name, prefix="", indent=0):
        return "<a href='#{}.{}'>{}.{}</a>".format(prefix, name, prefix, name)

    @classmethod
    def table_of_contents_class_end(cls, indent=0):
        return "</div>"

    @classmethod
    def table_of_contents_body_end(cls, indent=0):
        return "</div>"

    @classmethod
    def table_of_contents_end(cls, indent=0):
        return "</div>"

    # ---------------------------------------------------------------------------------
    # FUNCTIONS
    # ---------------------------------------------------------------------------------
    @classmethod
    def function_block_start(cls, indent=0):
        return "<div class='left_padded'>"

    @classmethod
    def function_start(cls, indent=0):
        return "<div class='function'>"

    @classmethod
    def function_signature(cls, func_name: str, parameters: list, prefix="", indent=0):
        return "<a id='{}.{}' class='function_title'>{}</a>".format(prefix, func_name,
                                                                    cls.general_function_signature(func_name,
                                                                                                   parameters))

    @classmethod
    def function_body_start(cls, indent=0):
        return "<div class='function_body'>"

    @classmethod
    def function_doc(cls, func_doc: str, indent=0):
        return "<p class='function_doc'>{}</p>".format(func_doc)

    @classmethod
    def function_parameters(cls, parameters: list, indent=0):
        out = []
        for i in parameters:
            if i['name'] not in ('self', 'cls'):
                if 'default' in i:
                    out.append("<p class='parameter'><a>{} (optional):</a> {}</p>".format(
                        i['name'],
                        i['doc'] if 'doc' in i else ""
                    ))
                else:
                    out.append("<p class='parameter'><a>{}:</a> {}</p>".format(i['name'],
                                                                               i['doc'] if 'doc' in i else ""))

        return "\n".join(out)

    @classmethod
    def function_return_parameter(cls, return_doc, indent=0):
        return "<p class='parameter'><a>return:</a> {}</p>".format(return_doc)

    @classmethod
    def function_body_end(cls, indent=0):
        return "</div>"

    @classmethod
    def function_end(cls, indent=0):
        return "</div>"

    @classmethod
    def function_block_end(cls, indent=0):
        return "</div>"

    # ---------------------------------------------------------------------------------
    # CLASSES
    # ---------------------------------------------------------------------------------
    @classmethod
    def class_start(cls, indent=0):
        return "<div class='class'>"

    @classmethod
    def class_title(cls, title, prefix="", indent=0):
        return "<h3 id='{}.{}' >class {}</h3>".format(prefix, title, title)

    @classmethod
    def class_body_start(cls, indent=0):
        return "<div class='class_body'>"

    @classmethod
    def class_doc(cls, doc, indent=0):
        return "<p>{}</p>".format(doc)

    # CONSTANTS
    @classmethod
    def class_constants_title(cls, prefix="", indent=0):
        return "<h4>Constants</h4>"

    @classmethod
    def class_constants_start(cls, indent=0):
        return "<div class='left_padded'>"

    @classmethod
    def class_constant(cls, name, value, prefix="", indent=0):
        return "<a id='{}.{}' class='constant'>{} = {}</a><br>".format(prefix, name, name, value)

    @classmethod
    def class_constants_end(cls, indent=0):
        return "</div>"

    # EXTRA TITLES
    @classmethod
    def static_function_title(cls, prefix="", indent=0):
        return "<h4>Static Methods</h4>"

    @classmethod
    def methods_title(cls, prefix="", indent=0):
        return "<h4>Methods</h4>"

    @classmethod
    def class_body_end(cls, indent=0):
        return "</div>"

    @classmethod
    def class_end(cls, indent=0):
        return "</div"


class MarkdownFormatter(Formatter):
    FILE_EXT = '.md'

    # ---------------------------------------------------------------------------------
    # MISC
    # ---------------------------------------------------------------------------------
    @classmethod
    def _indentify(cls, indent):
        return "".join(["  " for _ in range(indent)])

    # ---------------------------------------------------------------------------------
    # MODULES
    # ---------------------------------------------------------------------------------
    @classmethod
    def module_title(cls, title, prefix="", indent=0):
        return "# {}".format(title)

    # ---------------------------------------------------------------------------------
    # TABLE OF CONTENTS
    # ---------------------------------------------------------------------------------
    @classmethod
    def table_of_contents_title(cls, prefix="", indent=0):
        return "### Table of Contents"

    @classmethod
    def table_of_contents_function(cls, name, static=False, prefix="", indent=0):
        if static:
            return "{}* [`{}.{}()`](#{}.{}) (static)".format(cls._indentify(indent), prefix, name, prefix, name)
        else:
            return "{}* [`{}.{}()`](#{}.{})".format(cls._indentify(indent), prefix, name, prefix, name)

    @classmethod
    def table_of_contents_class(cls, name, prefix="", indent=0):
        return "{}* [`{}.{}`](#{}.{})".format(cls._indentify(indent), prefix, name, prefix, name)

    @classmethod
    def table_of_contents_constant(cls, name, prefix="", indent=0):
        return "{}* [`{}.{}`](#{}.{})".format(cls._indentify(indent), prefix, name, prefix, name)

    # ---------------------------------------------------------------------------------
    # FUNCTIONS
    # ---------------------------------------------------------------------------------

    @classmethod
    def function_signature(cls, func_name: str, parameters: list, prefix="", indent=0):
        return "{}* #### <a name='{}.{}'>{}</a>".format(cls._indentify(indent), prefix, func_name,
                                                        cls.general_function_signature(func_name, parameters))

    @classmethod
    def function_doc(cls, func_doc: str, indent=0):
        return "{}> {}".format(cls._indentify(indent), func_doc)

    @classmethod
    def function_parameters(cls, parameters: list, indent=0):
        out = []
        for i in parameters:
            if i['name'] not in ('self', 'cls'):
                if 'default' in i:
                    out.append("* `{}` (optional): {}".format(i['name'],
                                                              i['doc'] if 'doc' in i else ""))
                else:
                    out.append("* `{}`: {}".format(i['name'], i['doc'] if 'doc' in i else ""))

        # put indentation on first item
        if out:
            out[0] = cls._indentify(indent) + out[0]

        return "\n{}".format(cls._indentify(indent)).join(out)

    @classmethod
    def function_return_parameter(cls, return_doc, indent=0):
        return "{}* return: {}".format(cls._indentify(indent), return_doc)

    # ---------------------------------------------------------------------------------
    # CLASSES
    # ---------------------------------------------------------------------------------

    @classmethod
    def class_title(cls, title, prefix="", indent=0):
        return "{}* ## <a name='{}.{}'>class {}</a>".format(cls._indentify(indent), prefix, title, title)

    @classmethod
    def class_doc(cls, doc, indent=0):
        return "{}> {}".format(cls._indentify(indent), doc)

    # CONSTANTS
    @classmethod
    def class_constants_title(cls, prefix="", indent=0):
        return "{}* ### Constants".format(cls._indentify(indent))

    @classmethod
    def class_constant(cls, name, value, prefix="", indent=0):
        return "{}* <a name='{}.{}'>`{}`</a> = {}".format(cls._indentify(indent), prefix, name, name, value)

    # EXTRA TITLES
    @classmethod
    def static_function_title(cls, prefix="", indent=0):
        return "{}* ### Static Methods".format(cls._indentify(indent))

    @classmethod
    def methods_title(cls, prefix="", indent=0):
        return "{}* ### Methods".format(cls._indentify(indent))


class FormatOptions:
    def __init__(self):
        self.add_css_to_each_file = True


class PyDocumentor:
    HTML, MARK_DOWN = [i for i in range(2)]
    FORMATS = [HTML, MARK_DOWN]

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
    def _file_writer(output_dir: str, data, file_ext: str):
        for file_path in data.keys():
            folder, file_name_ext = path_split(file_path)
            file_name = str(file_name_ext.split('.')[0])
            new_fp = path_join(output_dir, file_name + file_ext)

            file = open(new_fp, 'w')
            module_str = data[file_path]
            file.write(module_str)
            file.close()

    @staticmethod
    def _format_functions(out: list, ft, funcs, prefix, indent):
        out.append(ft.function_block_start(indent=indent - 1))
        for func in funcs:
            out.append(ft.function_start(indent=indent))
            out.append(ft.function_signature(func['name'], func['parameters'], prefix=prefix, indent=indent))
            out.append(ft.function_body_start(indent=indent))
            out.append(ft.function_doc(func['doc'], indent=indent + 1))
            out.append(ft.function_parameters(func['parameters'], indent=indent + 1))

            if func['return']:
                out.append(ft.function_return_parameter(func['return'], indent=indent + 1))

            out.append(ft.function_body_end(indent=indent))
            out.append(ft.function_end(indent=indent))
        out.append(ft.function_block_end(indent=indent - 1))

    @staticmethod
    def _input_to_bool(yes_no):
        return yes_no in ("yes", "y")

    @staticmethod
    def _user_input(prompt, error="", validator=None):
        while True:
            result = input(prompt + ": ").strip()

            if validator is None or (validator is not None and validator(result)):
                return result
            else:
                print("<{}>".format(error), end="\n\n")

    def __init__(self):
        self.f_options = FormatOptions()
        self._collected_data = {}
        self._folder_mode = self._input_to_bool(self._user_input("Collect all files in folder Y/N",
                                                                 "Choice must be yes or no",
                                                                 lambda x: x.lower() in ("yes", "no", "y", "n")))
        self._advanced_mode = self._input_to_bool(self._user_input("Enter advanced mode Y/N",
                                                                   "Choice must be yes or no",
                                                                   lambda x: x.lower() in ("yes", "no", "y", "n")))
        print()

        self._collect_file_names()
        self._get_user_options()

        # import
        modules = self._import_modules()

        # collect module info
        for mod in modules:
            self._collected_data[mod.__file__] = self._collect_module_info(mod)

    def _collect_class_info(self, cls):
        inspected = getmembers(cls)
        data = {
            'methods': [],
            'constants': [],
            'static_methods': [],
            'doc': cls.__doc__.strip() if cls.__doc__ is not None else "",
            'name': cls.__name__
        }
        methods_functions = []
        method_dict = []

        # collect names of method, constants and __dict__ to use to check for static methods
        for name, memb in inspected:
            if isfunction(memb) or ismethod(memb):  # check if it is a function or method
                methods_functions.append([name, memb])
            elif not callable(memb) and name[0] != "_":  # constants
                data['constants'].append({'name': name, 'value': memb})

            if name == '__dict__':
                method_dict = memb

        # use method_dict and names of functions or methods to determine whether it is a static function
        for name, memb in methods_functions:
            if name in method_dict:
                if isinstance(method_dict[name], staticmethod):
                    if self._collect_private_methods or (not self._collect_private_methods and name[0] != '_'):
                        data['static_methods'].append(self._collect_function_info(memb))
                elif self._collect_private_methods or (not self._collect_private_methods and name[0] != '_'):
                    data['methods'].append(self._collect_function_info(memb))

        return data

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

    def _collect_function_info(self, func: callable):
        docs = PyDocumentor._analyze_function_docs(func.__doc__ if func.__doc__ is not None else "")
        data = {
            'name': func.__name__,
            'doc': docs['FUNCTION'] if 'FUNCTION' in docs else "",
            'parameters': [],
            'return': docs['RETURN'].strip() if 'RETURN' in docs else ""
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

    def _collect_module_info(self, mod):
        inspected = getmembers(mod)
        data = {'classes': [], 'functions': [], 'name': mod.__name__}

        for name, memb in inspected:
            if isclass(memb) and memb.__module__ == mod.__name__:
                data['classes'].append(self._collect_class_info(memb))
            # if this is a function, make sure it wasn't imported, and that it isn't private
            elif isfunction(memb) and memb.__module__ == mod.__name__:
                if self._collect_private_methods or (not self._collect_private_methods and name[0] != "_"):
                    data['functions'].append(self._collect_function_info(memb))

        return data

    def _get_user_options(self):
        # output directory
        out_d = self._user_input("Output Directory (leave blank to export where modules are)", "Invalid directory",
                                 isdir)
        self._output_directory = out_d if out_d != "" else self._directory

        # export folder name
        self._output_folder_name = self._user_input("Output Folder Name")
        print()

        # export format
        self._output_format = int(self._user_input("Output Format (HTML=0, Markdown=1)",
                                                   "Value must be number between 0-{}".format(len(self.FORMATS) - 1),
                                                   lambda x: x.isdigit() and int(x) in self.FORMATS))

        # add table of contents per page
        self._table_of_contents = self._input_to_bool(self._user_input("Add table of contents to each file Y/N",
                                                                       "Choice must be yes or no",
                                                                       lambda x: x.lower() in ("yes", "no", "y", "n")))
        print()

        # ADVANCED OPTIONS
        self._collect_private_methods = False

        if self._advanced_mode:
            if self._output_format == self.HTML:
                self.f_options.add_css_to_each_file = self._input_to_bool(self._user_input("Add CSS to each file Y/N",
                                                                                           "Choice must be yes or no",
                                                                                           lambda x: x.lower() in (
                                                                                               "yes", "no", "y", "n")))

            self._collect_private_methods = self._input_to_bool(
                self._user_input("Collect methods prefixed with '_' Y/N",
                                 "Choice must be yes or no",
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
            except ImportError:
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

        ft = None  # formatter
        if self._output_format == self.HTML:
            # self._export_as_html(dir_path)
            ft = HtmlFormatter(self.f_options)
        elif self._output_format == self.MARK_DOWN:
            ft = MarkdownFormatter(self.f_options)

        formatted_data = {}  # file path: formatted string
        for file_path in self._collected_data:
            mod = self._collected_data[file_path]
            out = []

            ft.free_run()

            out.append(ft.top_of_file())
            out.append(ft.module_title(mod['name'], prefix="", indent=0))
            out.append(ft.module_start(indent=0))

            if self._table_of_contents:
                out.append(ft.table_of_contents_start(indent=0))
                out.append(ft.table_of_contents_title(prefix=mod['name'], indent=0))
                out.append(ft.table_of_contents_body_start(indent=0))

                for func in mod['functions']:
                    out.append(ft.table_of_contents_function(func['name'], prefix=mod['name'], indent=1))

                for cls in mod['classes']:
                    out.append(ft.table_of_contents_class_start(indent=1))
                    out.append(ft.table_of_contents_class(cls['name'], prefix=mod['name'], indent=1))

                    for const in cls['constants']:
                        out.append(ft.table_of_contents_constant(const['name'], prefix=cls['name'], indent=2))

                    for func in cls['static_methods']:
                        out.append(ft.table_of_contents_function(func['name'], static=True, prefix=cls['name'],
                                                                 indent=2))

                    for func in cls['methods']:
                        out.append(ft.table_of_contents_function(func['name'], prefix=cls['name'], indent=2))

                    out.append(ft.table_of_contents_class_end(indent=1))
                out.append(ft.table_of_contents_body_end(indent=0))
                out.append(ft.table_of_contents_end(indent=0))

            if mod['functions']:
                self._format_functions(out, ft, mod['functions'], mod['name'], indent=1)

            for cls in mod['classes']:
                out.append(ft.class_start(indent=1))
                out.append(ft.class_title(cls['name'], prefix=mod['name'], indent=1))
                out.append(ft.class_body_start(indent=1))
                out.append(ft.class_doc(cls['doc'], indent=2))

                if cls['constants']:
                    out.append(ft.class_constants_title(indent=2))
                    out.append(ft.class_constants_start(indent=2))
                    for const in cls['constants']:
                        out.append(ft.class_constant(const['name'], const['value'], prefix=cls['name'], indent=3))
                    out.append(ft.class_constants_end(indent=2))

                if cls['static_methods']:
                    out.append(ft.static_function_title(indent=2))
                    self._format_functions(out, ft, cls['static_methods'], cls['name'], indent=3)

                if cls['methods']:
                    out.append(ft.methods_title(indent=2))
                    self._format_functions(out, ft, cls['methods'], cls['name'], indent=3)

                out.append(ft.class_body_end(indent=1))
                out.append(ft.class_end(indent=1))

            out.append(ft.module_end(indent=0))

            # clean empty str
            cleaned = []
            for i in out:
                if i:
                    cleaned.append(i)

            formatted_data[file_path] = "\n".join(cleaned)

        self._file_writer(dir_path, formatted_data, ft.FILE_EXT)

        print("\nExport Successful!\nExiting...")

if __name__ == "__main__":
    docker = PyDocumentor()
    docker.export()
