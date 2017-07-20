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

"""
py_documentor.py contains five different classes. The primary one is PyDocumentor, which uses the others.
PyDocumentor gives access to a console-based program that takes Python files and creates documentation for them using
class and function definitions and any available docstrings. To use, just run this module, or, create an instance of 
PyDocumentor and then call its export() method.

Extra information can be provided in the docstrings to help build better documentation. 
:param name:, :return: both work only with functions and allow more information to be added about those items
:exclude: allows a module, class, or function to not be included in the documentation
:exclude_children: works for classes, prevents constants or methods from being documented
:exclude_methods [func1, func2...]: works for classes, allows specific methods to be excluded, or if no methods are
given, then all methods are excluded
:include_methods func1, func2...: only for a class, allows specific functions to be included despite an exclude_methods. 
This will also override and collect a private method even if that option is False.
"""

from os import walk, mkdir, sep
from os.path import isfile, isdir, split as path_split, exists as path_exists, join as path_join
import importlib.util
from inspect import getmembers, signature, isclass, isfunction, ismethod, Parameter
import re
from typing import Optional


class Formatter:
    """
    Basic class to provide a backbone for any format classes. Guarantees that all method calls work within
    PyDocumentor.export(), even if the individual format classes don't implement that specific method.
    :exclude_methods free_run:
    """
    FILE_EXT = ""  # file extension for the format

    def __init__(self, options):
        """
        Take in the user options from PyDocumentor to provide a way for things like adding css to each html file
        :param options: a collection of all the user options
        """
        self.options = options

    def free_run(self):
        """
        Run at the beginning of the module, before anything is formatted.
        """
        pass

    def top_of_file(self) -> str:
        """
        Returns a string for the very top of the module file. This call happens right after free_run() is called
        :return: 
        """
        return ""

    # --------------------------------------------------------------------------------
    # MISC
    # --------------------------------------------------------------------------------
    @classmethod
    def general_function_signature(cls, func_name: str, parameters: list) -> str:
        """
        The function signature used is the same no matter what format is being used. This generates that signature as 
        func_name(a, b, ..., x=3, y="2", *args, **kwargs)
        :param func_name: the name of the function
        :param parameters: a dictionary of the parameters of this function. Formatted as collected by
        PyDocumentor._collect_function_info()
        :return: the function signature
        """
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
        """
        Format the title/header of the module
        :param title: the name of the module
        :param prefix: parent's name
        :param indent: how much to indent
        :return: the formatted title/header of the module
        """
        return ""

    @classmethod
    def module_start(cls, indent=0):
        """
        Start the body of the module
        :param indent: how much to indent
        :return: the formatted start of the body of the module
        """
        return ""

    @classmethod
    def module_doc(cls, doc, prefix="", indent=0):
        """
        format the docstring for the module
        :param doc: the doc for the module
        :param prefix: the parent's name
        :param indent: how much to indent
        :return: the formatted docstring for the module
        """
        return ""

    @classmethod
    def module_end(cls, indent=0):
        """
        Format the end of the body of the module
        :param indent: how much to indent 
        :return: the formatted end of the body of the module
        """
        return ""

    # ---------------------------------------------------------------------------------
    # TABLE OF CONTENTS
    # ---------------------------------------------------------------------------------
    @classmethod
    def table_of_contents_start(cls, indent=0):
        """
        format the start of the table of contents
        :param indent: how much to indent
        :return: the formatted start of the table of contents
        """
        return ""

    @classmethod
    def table_of_contents_title(cls, prefix="", indent=0):
        """
        format the title of the table of contents, typically this is Table of Contents
        :param prefix: the parent's name
        :param indent: how much to indent
        :return: the formatted title of the table of contents
        """
        return ""

    @classmethod
    def table_of_contents_body_start(cls, indent=0):
        """
        format the start of the body of the table of contents
        :param indent: how much to indent
        :return: the formatted start of the body of the table of contents
        """
        return ""

    @classmethod
    def table_of_contents_function(cls, name, static=False, prefix="", indent=0):
        """
        format a function in the table of contents
        :param name: the name of the function
        :param static: whether the function is static or not
        :param prefix: the parent's name
        :param indent: how much to indent
        :return: the formatted function
        """
        return ""

    @classmethod
    def table_of_contents_class(cls, name, prefix="", indent=0):
        """
        format the class for the table of contents
        :param name: the name of the class
        :param prefix: the parent's name
        :param indent: how much to indent
        :return: the formatted class 
        """
        return ""

    @classmethod
    def table_of_contents_class_start(cls, indent=0):
        """
        format the start of the body of a class in the table of contents, can be used to indent methods
        :param indent: how much to indent
        :return: the formatted start of the body of the class
        """
        return ""

    @classmethod
    def table_of_contents_constant(cls, name, prefix="", indent=0):
        """
        format a constant/field for the table of contents
        :param name: the name of the constant/field
        :param prefix: the parent's name
        :param indent: how much to indent
        :return: the formatted constant/field
        """
        return ""

    @classmethod
    def table_of_contents_class_end(cls, indent=0):
        """
        format the end of a class in the table of contents
        :param indent: how much to indent
        :return: the formatted end of a class
        """
        return ""

    @classmethod
    def table_of_contents_body_end(cls, indent=0):
        """
        format the end of the body of the table of contents
        :param indent: how much to indent
        :return: the formatted end of the body of the table of contents
        """
        return ""

    @classmethod
    def table_of_contents_end(cls, indent=0):
        """
        format the end of the table of contents
        :param indent: how much to indent
        :return: the formatted end of the table of contents
        """
        return ""

    # ---------------------------------------------------------------------------------
    # FUNCTIONS
    # ---------------------------------------------------------------------------------
    @classmethod
    def function_block_start(cls, indent=0):
        """
        format the start of a group of functions
        :param indent: how much to indent
        :return: formatted start of a group of functions
        """
        return ""

    @classmethod
    def function_start(cls, indent=0):
        """
        format the start of an individual function
        :param indent: how much to indent
        :return: formatted start of a function
        """
        return ""

    @classmethod
    def function_signature(cls, func_name: str, parameters: list, prefix="", indent=0):
        """
        format the function signature, typically calls general_function_signature()
        :param func_name: the name of the function
        :param parameters: the function's parameters
        :param prefix: the parent's name
        :param indent: how much to indent 
        :return: formatted signature of the function
        """
        return ""

    @classmethod
    def function_body_start(cls, indent=0):
        """
        format the start of the body of a function where the doc and parameters go
        :param indent: how much to indent
        :return: formatted start of the body of a function
        """
        return ""

    @classmethod
    def function_doc(cls, func_doc: str, indent=0):
        """
        format the docstring of the function
        :param func_doc: the docstring of the function
        :param indent: how much to indent
        :return: formatted docstring
        """
        return ""

    @classmethod
    def function_parameters(cls, parameters: list, indent=0):
        """
        format the parameters of the function each with their own docstring if it exists
        :param parameters: the list of parameters of the function
        :param indent: how much to indent
        :return: formatted list of parameters
        """
        return ""

    @classmethod
    def function_return_parameter(cls, return_doc, indent=0):
        """
        format the return parameter of the function
        :param return_doc: the return parameters documentation
        :param indent: how much to indent
        :return: formatted return parameter
        """
        return ""

    @classmethod
    def function_body_end(cls, indent=0):
        """
        format the end of the body of the function
        :param indent: how much to indent
        :return: formatted end of the body of the function
        """
        return ""

    @classmethod
    def function_end(cls, indent=0):
        """
        format the end of the function
        :param indent: how much to indent
        :return: formatted end of function
        """
        return ""

    @classmethod
    def function_block_end(cls, indent=0):
        """
        format the end of a group of functions
        :param indent: how much to indent
        :return: formatted end of a group of functions
        """
        return ""

    # ---------------------------------------------------------------------------------
    # CLASSES
    # ---------------------------------------------------------------------------------
    @classmethod
    def class_start(cls, indent=0):
        """
        format the start of a class
        :param indent: how much to indent
        :return: formatted start of class
        """
        return ""

    @classmethod
    def class_title(cls, title, prefix="", indent=0):
        """
        format the name of the class
        :param title: the name of the class
        :param prefix: the parent's name
        :param indent: how much to indent
        :return: formatted name/header/title of the class
        """
        return ""

    @classmethod
    def class_body_start(cls, indent=0):
        """
        format the start of the body of the class
        :param indent: how much to indent
        :return: formatted start of the body of the class
        """
        return ""

    @classmethod
    def class_doc(cls, doc, indent=0):
        """
        format the docstring of the class
        :param doc: docstring of the class
        :param indent: how much to indent
        :return: formatted docstring of the class
        """
        return ""

    # CONSTANTS
    @classmethod
    def class_constants_title(cls, prefix="", indent=0):
        """
        format the title of the constants section for a class, typically just Constants
        :param prefix: the parent's name
        :param indent: how much to indent
        :return: formatted title of the constants section
        """
        return ""

    @classmethod
    def class_constants_start(cls, indent=0):
        """
        format the start of the constants section of a class
        :param indent: how much to indent
        :return: formatted start of the constants section
        """
        return ""

    @classmethod
    def class_constant(cls, name, value, prefix="", indent=0):
        """
        format a constant in a class
        :param name: the name of the constant
        :param value: the constants value
        :param prefix: the parent's name
        :param indent: how much to indent
        :return: formatted constant
        """
        return ""

    @classmethod
    def class_constants_end(cls, indent=0):
        """
        format the end of the constants section
        :param indent: how much to indent
        :return: formatted end of the constants section
        """
        return ""

    # EXTRA TITLES
    @classmethod
    def static_function_title(cls, prefix="", indent=0):
        """
        format the title of the static methods section in a class, typically Static Methods
        :param prefix: the parent's name
        :param indent: how much to indent
        :return: formatted title of the static methods section
        """
        return ""

    @classmethod
    def methods_title(cls, prefix="", indent=0):
        """
        format the title for the methods section in a class, typically Methods
        :param prefix: the parent's name
        :param indent: how much to indent
        :return: formatted title for the methods section
        """
        return ""

    @classmethod
    def class_body_end(cls, indent=0):
        """
        format the end of the body of a class
        :param indent: how much to indent
        :return: formatted end of the body of a class
        """
        return ""

    @classmethod
    def class_end(cls, indent=0):
        """
        format the end of a class
        :param indent: how much to indent
        :return: formatted end of a class
        """
        return ""


class HtmlFormatter(Formatter):
    """
    An implementation of Formatter which formats everything in HTML. Look at the notes on Formatter for method specifics
    :exclude_methods:
    """
    FILE_EXT = ".html"

    def __init__(self, options):
        super(HtmlFormatter, self).__init__(options)
        self.css = ""

    def free_run(self):
        # generate in-line css
        css_file_path = path_split(__file__)[0] + sep + "style.css"
        css_file = open(css_file_path, 'r')

        self.css = "".join([line for line in css_file.readlines()])
        css_file.close()

        # write css to file
        if not self.options.add_css_to_each_file:
            new_fp = self.options.output_directory + sep + "style.css"
            new_css_file = open(new_fp, "w")
            new_css_file.write(self.css)
            new_css_file.close()

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
    def module_doc(cls, doc, prefix="", indent=0):
        return "<p>{}</p>".format(doc)

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
        return "<a href='#{}.{}'>{}.{}</a><br>".format(prefix, name, prefix, name)

    @classmethod
    def table_of_contents_class_start(cls, indent=0):
        return "<div class='table_of_contents_class'>"

    @classmethod
    def table_of_contents_constant(cls, name, prefix="", indent=0):
        return "<a href='#{}.{}'>{}.{}</a><br>".format(prefix, name, prefix, name)

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
            if i['name'] not in ('self', 'cls') and 'doc' in i and i['doc']:
                if 'default' in i:
                    out.append("<p class='parameter'><a>{} (optional):</a> {}</p>".format(i['name'], i['doc']))
                else:
                    out.append("<p class='parameter'><a>{}:</a> {}</p>".format(i['name'], i['doc']))

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
        if isinstance(value, str):
            value = "\"{}\"".format(value)
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
        return "</div>"


class MarkdownFormatter(Formatter):
    """
    An implementation of Formatter which formats everything in Markdown. Look at the notes on Formatter for method 
    specifics
    :exclude_methods:
    :include_methods _indentify:
    """
    FILE_EXT = '.md'

    # ---------------------------------------------------------------------------------
    # MISC
    # ---------------------------------------------------------------------------------
    @classmethod
    def _indentify(cls, indent: int):
        """
        Take the indent amount and convert it to space to properly indent
        :param indent: the levels of indentation
        :return: two spaces for every level of indentation
        """
        return "".join(["  " for _ in range(indent)])

    # ---------------------------------------------------------------------------------
    # MODULES
    # ---------------------------------------------------------------------------------
    @classmethod
    def module_title(cls, title, prefix="", indent=0):
        return "# {}".format(title)

    @classmethod
    def module_doc(cls, doc, prefix="", indent=0):
        # add > after each newline to make sure all the doc stays in the same block of text
        doc_list = []
        indent_str = cls._indentify(indent)

        for i in doc:
            doc_list.append(i)
            if i == "\n":
                doc_list.append("{}> ".format(indent_str))

        return "{}> {}".format(indent_str, "".join(doc_list))

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
            if i['name'] not in ('self', 'cls') and 'doc' in i and i['doc']:
                if 'default' in i:
                    out.append("* `{}` (optional): {}".format(i['name'], i['doc']))
                else:
                    out.append("* `{}`: {}".format(i['name'], i['doc']))

        # put indentation on first item
        if out:
            out[0] = cls._indentify(indent) + out[0]

        return "\n{}".format(cls._indentify(indent)).join(out)

    @classmethod
    def function_return_parameter(cls, return_doc, indent=0):
        return "{}* `return:` {}".format(cls._indentify(indent), return_doc)

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
        if isinstance(value, str):
            value = "\"{}\"".format(value)
        return "{}* <a name='{}.{}'>`{}`</a> = {}".format(cls._indentify(indent), prefix, name, name, value)

    # EXTRA TITLES
    @classmethod
    def static_function_title(cls, prefix="", indent=0):
        return "{}* ### Static Methods".format(cls._indentify(indent))

    @classmethod
    def methods_title(cls, prefix="", indent=0):
        return "{}* ### Methods".format(cls._indentify(indent))


class UserOptions:
    """
    Collect together all the user modifiable options in one class to provide easy access and a simple way to pass
    these parameters into the formatter's.
    """
    # basic options
    folder_mode = False
    advanced_mode = False

    directory = ""
    output_directory = ""
    output_folder_name = ""
    output_format = None

    table_of_contents = True

    # advanced options
    add_css_to_each_file = True
    collect_private_methods = False


class PyDocumentor:
    """
    Collect and export documentation in the appropriate format for whatever modules are specified in the console-based
    interface. HTML and Markdown are both available as export formats.
    """
    HTML, MARK_DOWN = [i for i in range(2)]
    FORMATS = [HTML, MARK_DOWN]

    @staticmethod
    def _analyze_function_docs(doc: str) -> dict:
        """
        Analyze the doc string of a function and look for documentation for parameters and return values based on the
        same format that PyCharm uses.
        :param doc: func.__doc__ from the function
        :return: a dictionary of parameter_name -> doc, also included are FUNCTION which includes the documentation 
        not about the parameters, and RETURN.
        """
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
    def _check_exclusion(doc, exclusion: str) -> bool:
        """
        Check and see if this doc contains :exclusion: where exclusion is the parameter. 
        :param doc: the doc to see if the module/class/function is excluded
        :param exclusion: the exclusion level to look for in exclude, exclude_children, exclude_methods
        :return: whether the correct pattern is found in doc based on exclusion
        """
        if doc:
            return re.search(":[ \t]*{}[ \t]*:[ \t]*\n".format(exclusion), doc) is not None
        else:
            return False

    @staticmethod
    def _file_writer(output_dir: str, data: dict, file_ext: str):
        """
        Take the data and write it to output_dir
        :param output_dir: the directory to write all the files in 
        :param data: a dict of {file_path: formatted_string}
        :param file_ext: The file extension that the data is formatted for
        """
        for file_path in data.keys():
            folder, file_name_ext = path_split(file_path)
            file_name = str(file_name_ext.split('.')[0])
            new_fp = path_join(output_dir, file_name + file_ext)

            file = open(new_fp, 'w')
            module_str = data[file_path]
            file.write(module_str)
            file.close()

    @staticmethod
    def _format_functions(out: list, ft, funcs: list, cls: dict, indent: int):
        """
        Execute the proper Formatter function calls to add this block of functions to out
        :param out: the list being used to collected all the formatted data
        :param ft: the Formatter class to use to format the data
        :param funcs: a list of the functions to format
        :param cls: the class
        :param indent: the indentation of this block of functions
        """
        out.append(ft.function_block_start(indent=indent - 1))
        for func in funcs:
            out.append(ft.function_start(indent=indent))
            out.append(ft.function_signature(func['name'], func['parameters'], prefix=cls['name'], indent=indent))
            out.append(ft.function_body_start(indent=indent))
            out.append(ft.function_doc(func['doc'], indent=indent + 1))
            out.append(ft.function_parameters(func['parameters'], indent=indent + 1))

            if func['return']:
                out.append(ft.function_return_parameter(func['return'], indent=indent + 1))

            out.append(ft.function_body_end(indent=indent))
            out.append(ft.function_end(indent=indent))
        out.append(ft.function_block_end(indent=indent - 1))

    @staticmethod
    def _get_exclusion(doc):
        """
        get a list of the excluded functions for a class if they are specified
        :param doc: the doc to look through for excluded functions
        :return: a set of the names of the excluded functions, or False if exclude_methods not in doc, or True
        if it is in doc, but not methods are specified.
        """
        if doc:
            match = re.search(":\s*exclude_methods\s*((?:\s*\w+\s*)(?:,\s*\w+\s*)*)?:", doc)

            if match:
                if match.group(1) is None:  # there was a match, but no function names were collected
                    return True
                else:
                    return set([i.strip() for i in match.group(1).split(",")])

        return False

    @staticmethod
    def _get_exclusion_level(memb: dict) -> Optional[str]:
        """
        Get the broadest exclusion level in memb if there is one at all
        :param memb: the module/class/function to see it it is excluded in some way
        :return: the broadest level of exclusion, or None
        """
        ordered_levels = ['exclude', 'exclude_children', 'exclude_methods']
        for level in ordered_levels:
            if level in memb and memb[level]:
                return level

        return None

    @staticmethod
    def _get_inclusion(doc) -> set:
        """
        get a list of the included functions for a class if they are specified
        :param doc: the doc to look through for included functions
        :return: a set of the names of the included functions
        """
        out = set()
        if doc:
            match = re.search(":\s*include_methods\s*((?:\s*\w+\s*)(?:,\s*\w+\s*)*):", doc)

            if match:
                out = set([i.strip() for i in match.group(1).split(",")])

        return out

    @staticmethod
    def _is_method_excluded(name, included: set, exclude_children: bool, exclude_methods) -> bool:
        """
        Determine whether or not this method is excluded from a class. 
        :param name: the name of the method
        :param included: a set containing the names of the included method for the class
        :param exclude_children: whether or not all children are excluded for the class
        :param exclude_methods: is True if all methods need to be excluded, False if no methods need excluded, or a set 
            with names of methods if only specific methods need excluded
        :return: a boolean of whether or not to exclude this method
        """
        if name in included:  # if this is specifically included, then there is no reason to exclude it
            return False
        elif exclude_children:  # exclude if all children are
            return True
        elif isinstance(exclude_methods, bool) and exclude_methods:  # exclude if all methods are
            return True
        elif isinstance(exclude_methods, set) and name in exclude_methods:  # exclude if method is specifically excluded
            return True
        else:  # no reason to exclude
            return False

    @staticmethod
    def _input_to_bool(yes_no: str) -> bool:
        """
        Go from a yes/no response to a boolean
        :param yes_no: a string of either y, yes, n, no
        :return: a boolean of True for y or yes, else False
        """
        return yes_no in ("yes", "y")

    @staticmethod
    def _user_input(prompt: str, error="", validator=None) -> str:
        """
        Get user input, if there is a validator given, then continue to collect input until the data is good
        :param prompt: The prompt to output
        :param error: The error to show if there is a validator and it fails
        :param validator: A callable to use to make sure the data is in a valid format
        :return: the valid input
        """
        while True:
            result = input(prompt + ": ").strip()

            if validator is None or (validator is not None and validator(result)):
                return result
            else:
                print("<{}>".format(error), end="\n\n")

    def __init__(self):
        """
        Collect format options and needed file/folder locations. Then collect the data from those files.
        """
        self.options = UserOptions()
        self._collected_data = {}
        self.options.folder_mode = self._input_to_bool(self._user_input("Collect all files in folder Y/N",
                                                                        "Choice must be yes or no",
                                                                        lambda x: x.lower() in ("yes", "no", "y", "n")))
        self.options.advanced_mode = self._input_to_bool(self._user_input("Enter advanced mode Y/N",
                                                                          "Choice must be yes or no",
                                                                          lambda x: x.lower() in ("yes", "no", "y", "n"
                                                                                                  )))
        print()

        self._collect_file_names()
        self._get_user_options()

        # import
        modules = self._import_modules()

        # collect module info
        for mod in modules:
            data = self._collect_module_info(mod)
            if data is not None:
                self._collected_data[mod.__file__] = data

    def _collect_class_info(self, cls) -> Optional[dict]:
        """
        Inspect a class and get its methods, constants, static_methods, doc and name. 
        :param cls: The class to collect the data from
        :return: A dictionary of the collected data with the keys as shown below, or None if class is excluded
        """
        inspected = getmembers(cls)
        if not self._check_exclusion(cls.__doc__, 'exclude'):
            data = {
                'methods': [],
                'constants': [],
                'static_methods': [],
                'doc': cls.__doc__.strip() if cls.__doc__ is not None else "",
                'name': cls.__name__,
            }
            methods_functions = []
            method_dict = {}

            exclude_children = self._check_exclusion(data['doc'], 'exclude_children')
            exclude_methods = self._get_exclusion(data['doc'])
            include_methods = self._get_inclusion(data['doc'])

            # collect names of method, constants and __dict__ to use to check for static methods
            for name, memb in inspected:
                if isfunction(memb) or ismethod(memb):  # check if it is a function or method
                    if not self._is_method_excluded(name, include_methods, exclude_children, exclude_methods):
                        methods_functions.append([name, memb])
                elif not callable(memb) and name[0] != "_" and not exclude_children:  # constants
                    data['constants'].append({'name': name, 'value': memb})

                if name == '__dict__':
                    method_dict = memb

            # use method_dict and names of functions or methods to determine whether it is a static function
            for name, memb in methods_functions:
                if name in method_dict:
                    if isinstance(method_dict[name], staticmethod) and (self.options.collect_private_methods
                                                                        or name[0] != "_" or name in include_methods):
                            func = self._collect_function_info(memb)
                            if func is not None:
                                data['static_methods'].append(func)
                    elif self.options.collect_private_methods or name[0] != '_' or name in include_methods:
                        func = self._collect_function_info(memb)
                        if func is not None:
                            data['methods'].append(func)

            return data
        else:
            return None

    def _collect_file_names(self):
        """
        Collect all the file names for the modules that will have documentation created. If in folder_mode, then
        walk through the folder and all of its child folders recursively, collecting all Python files.
        """
        if self.options.folder_mode:
            folder_path = self._user_input("Folder Path", "Invalid folder path", isdir)
            self.options.directory = folder_path
            self._file_paths = []

            # walk through sub-directories and collect python files
            for (dirpath, dirnames, file_names) in walk(folder_path):
                for filename in file_names:
                    if filename.endswith(".py"):
                        self._file_paths.append(dirpath + filename)
        else:
            file_path = self._user_input("File Path", "Invalid file path", isfile)
            self.options.directory, _ = path_split(file_path)
            self._file_paths = [file_path]

    def _collect_function_info(self, func: callable) -> Optional[dict]:
        """
        Inspect and collect the data from a function. Get its name, documentation, and parameters.
        :param func: The function to inspect and collect data on
        :return: A dictionary containing the keys shown below, or None if the function is excluded
        """
        if not self._check_exclusion(func.__doc__, 'exclude'):
            docs = PyDocumentor._analyze_function_docs(func.__doc__ if func.__doc__ is not None else "")
            data = {
                'name': func.__name__,
                'doc': docs['FUNCTION'] if 'FUNCTION' in docs else "",
                'parameters': [],
                'return': docs['RETURN'].strip() if 'RETURN' in docs else "",
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
        else:
            return None

    def _collect_module_info(self, mod) -> Optional[dict]:
        """
        Inspect and collect data from the module given. Collect information from all of its classes and functions as
        well.
        :param mod: the module to inspect and collect data from 
        :return: a dictionary with the keys shown below, or None if the module is excluded
        """
        inspected = getmembers(mod)
        if not self._check_exclusion(mod.__doc__, 'exclude'):
            data = {
                'classes': [],
                'functions': [],
                'name': mod.__name__,
                'doc': mod.__doc__.strip() if mod.__doc__ else "",
            }

            for name, memb in inspected:
                if isclass(memb) and memb.__module__ == mod.__name__:
                    cls = self._collect_class_info(memb)
                    if cls is not None:
                        data['classes'].append(cls)
                # if this is a function, make sure it wasn't imported, and that it isn't private
                elif isfunction(memb) and memb.__module__ == mod.__name__:
                    if self.options.collect_private_methods or name[0] != "_":
                        func = self._collect_function_info(memb)
                        if func is not None:
                            data['functions'].append(func)

            return data
        return None

    def _get_user_options(self):
        """
        Collect options from the user that allows them to customize the output 
        """
        # output directory
        out_d = self._user_input("Output Directory (leave blank to export where modules are)", "Invalid directory",
                                 isdir)
        self.options.output_directory = out_d if out_d != "" else self.options.directory

        # export folder name
        self.options.output_folder_name = self._user_input("Output Folder Name")
        print()

        # export format
        self.options.output_format = int(self._user_input("Output Format (HTML=0, Markdown=1)",
                                                          "Value must be number between 0-{}".format(
                                                              len(self.FORMATS) - 1),
                                                          lambda x: x.isdigit() and int(x) in self.FORMATS))

        # add table of contents per page
        self.options.table_of_contents = self._input_to_bool(self._user_input("Add table of contents to each file Y/N",
                                                                              "Choice must be yes or no",
                                                                              lambda x: x.lower() in ("yes", "no", "y",
                                                                                                      "n")))
        print()

        # ADVANCED OPTIONS
        if self.options.advanced_mode:
            # format independent
            self.options.collect_private_methods = self._input_to_bool(
                self._user_input("Collect methods prefixed with '_' Y/N",
                                 "Choice must be yes or no", lambda x: x.lower() in ("yes", "no", "y", "n")))

            # format dependent
            if self.options.output_format == self.HTML:
                self.options.add_css_to_each_file = self._input_to_bool(self._user_input("Add CSS to each file Y/N",
                                                                                         "Choice must be yes or no",
                                                                                         lambda x: x.lower() in (
                                                                                               "yes", "no", "y", "n")))

    def _import_modules(self) -> list:
        """
        Go through all the file paths collected earlier and import those modules so that the information can be 
        collected on the modules
        :return: A list of all the imported modules
        """
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

    def display_overview(self):
        """
        Display the names of the modules collected and the classes in each        
        """
        print("\nCollected Modules & Classes:")

        for mod in self._collected_data.values():
            if self._get_exclusion_level(mod) is not None:
                print("{}.py ({})".format(mod['name'], self._get_exclusion_level(mod)))
            else:
                print("{}.py".format(mod['name']))

            for cls in mod['classes']:
                if self._get_exclusion_level(cls) is not None:
                    print("\t{} ({})".format(cls['name'], self._get_exclusion_level(cls)))
                else:
                    print("\t{}".format(cls['name']))

    def export(self):
        """
        Create an export directory, then create the correct Formatter and use it to call of the functions needed to
        format all of the collected data.
        """
        # create export directory
        dir_path = self.options.output_directory + sep + self.options.output_folder_name
        if not path_exists(dir_path):
            try:
                mkdir(dir_path)
            except PermissionError:
                print("<PermissionError trying to create folder <{}>>".format(dir_path))
                exit()

        ft = None  # formatter
        if self.options.output_format == self.HTML:
            # self._export_as_html(dir_path)
            ft = HtmlFormatter(self.options)
        elif self.options.output_format == self.MARK_DOWN:
            ft = MarkdownFormatter(self.options)

        formatted_data = {}  # file path: formatted string
        for file_path in self._collected_data:
            mod = self._collected_data[file_path]

            out = []

            ft.free_run()

            out.append(ft.top_of_file())
            out.append(ft.module_title(mod['name'], indent=0))
            out.append(ft.module_start(indent=0))
            out.append(ft.module_doc(mod['doc'], indent=1))

            if self.options.table_of_contents:
                out.append(ft.table_of_contents_start(indent=0))
                out.append(ft.table_of_contents_title(prefix=mod['name'], indent=0))
                out.append(ft.table_of_contents_body_start(indent=0))

                for func in mod['functions']:
                        out.append(ft.table_of_contents_function(func['name'], prefix=mod['name'], indent=1))

                for cls in mod['classes']:
                    out.append(ft.table_of_contents_class(cls['name'], prefix=mod['name'], indent=1))

                    out.append(ft.table_of_contents_class_start(indent=1))

                    for const in cls['constants']:
                        out.append(ft.table_of_contents_constant(const['name'], prefix=cls['name'],
                                                                 indent=2))

                    for func in cls['static_methods']:
                        out.append(ft.table_of_contents_function(func['name'], static=True,
                                                                 prefix=cls['name'], indent=2))

                    for func in cls['methods']:
                        out.append(ft.table_of_contents_function(func['name'], prefix=cls['name'],
                                                                 indent=2))

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
                        out.append(ft.class_constant(const['name'], const['value'], prefix=cls['name'],
                                                     indent=3))
                    out.append(ft.class_constants_end(indent=2))

                if cls['static_methods']:
                    out.append(ft.static_function_title(indent=2))
                    self._format_functions(out, ft, cls['static_methods'], cls, indent=3)

                if cls['methods']:
                    out.append(ft.methods_title(indent=2))
                    self._format_functions(out, ft, cls['methods'], cls, indent=3)

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
    docker.display_overview()
    docker.export()
