from __future__ import print_function

import glob
import os
import sys

import pyembroidery


def formatted_string(string, pattern=None, filename=None):
    if "%" not in string:
        return string
    if filename is not None:
        if "%f" in string:
            string = string.replace("%f", filename)
        if "%F" in string:
            filename_suffix = os.path.split(filename)[1]
            string = string.replace("%F", filename_suffix)
        if "%e" in string:
            ext = os.path.splitext(filename)[1][1:]
            string = string.replace("%e", ext)
        if "%d" in string:
            directory = os.path.split(filename)[0]
            string = string.replace("%d", directory)
        if "%n" in string:
            filename_suffix = os.path.split(filename)[1]
            name = os.path.splitext(filename_suffix)[0]
            string = string.replace("%n", name)
        if pattern is not None:
            if "%S" in string:
                string = string.replace("%S", str(len(pattern.stitches)))
            if "%s" in string:
                string = string.replace("%s", str(pattern.count_stitch_commands(pyembroidery.STITCH)))
            if "%j" in string:
                string = string.replace("%j", str(pattern.count_stitch_commands(pyembroidery.JUMP)))
            if "%c" in string:
                count = pattern.count_stitch_commands(pyembroidery.COLOR_CHANGE)
                count += pattern.count_stitch_commands(pyembroidery.NEEDLE_SET)
                string = string.replace("%c", str(count))
            if "%t" in string:
                count = pattern.count_stitch_commands(pyembroidery.TRIM)
                string = string.replace("%t", str(count))
            if "%x" in string or "%X" in string or "%y" in string or "%Y" in string or "%w" in string or "%h" in string:
                bounds = pattern.bounds()
                string = string.replace("%x", str(bounds[0]))
                string = string.replace("%y", str(bounds[1]))
                string = string.replace("%X", str(bounds[2]))
                string = string.replace("%Y", str(bounds[3]))
                string = string.replace("%w", str(bounds[2] - bounds[0]))
                string = string.replace("%h", str(bounds[3] - bounds[1]))
            if "%l" in string:
                try:
                    label = pattern.extras["name"]
                except KeyError:
                    label = ""
                string = string.replace("%l", str(label))
        return string


class PyEmb:
    def __init__(self, arguments):
        self.log = print
        self.elements = list(reversed(arguments))
        self.command_lookup = {
            "-i": self.command_input,
            "-o": self.command_output,
            "-c": self.command_conditional,
            "-f": self.command_format,
            "-s": self.command_scale,
            "-r": self.command_rotate,
            "-t": self.command_translate,
            "-e": self.command_encode_setting,
            "-q": self.command_quiet,
            "-v": self.command_verbose,
        }

    def get(self):
        return self.elements.pop()

    def v(self):
        if not self.elements:
            return None
        if self.elements[-1] not in self.command_lookup:
            return self.get()
        else:
            return None

    def execute(self):
        values = []
        while self.elements:
            command = self.get()
            if command not in self.command_lookup:
                continue
            values = self.command_lookup[command](values)

    def command_input(self, values):
        v = self.v()
        input_files = glob.glob(v)
        patterns = []
        for input_file in input_files:
            self.log("Loading:", input_file)
            emb_pattern = pyembroidery.read(input_file)
            if emb_pattern is None:
                continue
            patterns.append((emb_pattern, input_file, {}))
        return patterns

    def command_output(self, values):
        out_path = []
        v = self.v()
        while v is not None:
            out_path.append(v)
            v = self.v()
        for value in values:
            if not isinstance(value, tuple):
                continue
            pattern = value[0]
            filename = value[1]
            settings = value[2]
            for path in out_path:
                path = formatted_string(path, pattern, filename)
                ext_split = os.path.splitext(path)
                name = ext_split[0]
                ext = ext_split[1]
                if ext == ".*":
                    for file_type in pyembroidery.supported_formats():
                        if 'writer' in file_type:
                            out_file = name + '.' + file_type['extension']
                            self.log("Saving:", out_file)
                            pyembroidery.write_embroidery(file_type['writer'], pattern, out_file, settings)
                else:
                    self.log("Saving:", path)
                    pyembroidery.write(pattern, path, settings)
        return []

    def command_format(self, values):
        string_format = self.v()
        for value in values:
            string = string_format
            if not isinstance(value, tuple):
                continue
            pattern = value[0]
            filename = value[1]
            string = formatted_string(string, pattern, filename)
            print(string)
        return values

    def command_scale(self, values):
        sx = self.v()
        sy = self.v()
        x = self.v()
        y = self.v()
        if sx is not None:
            sx = float(sx)
        if sy is not None:
            sy = float(sy)
        if x is not None:
            x = float(x)
        if y is not None:
            y = float(y)
        matrix = pyembroidery.EmbMatrix()
        matrix.post_scale(sx, sy, x, y)
        for value in values:
            if not isinstance(value, tuple):
                continue
            pattern = value[0]
            pattern.transform(matrix)
            self.log("Scaled", pattern, "by", sx, sy)
        return values

    def command_rotate(self, values):
        theta = self.v()
        x = self.v()
        y = self.v()
        if theta is not None:
            theta = float(theta)
        if x is not None:
            x = float(x)
        if y is not None:
            y = float(y)
        matrix = pyembroidery.EmbMatrix()
        matrix.post_rotate(theta, x, y)
        for value in values:
            if not isinstance(value, tuple):
                continue
            pattern = value[0]
            pattern.transform(matrix)
            self.log("Rotated", pattern, "by", theta, "degrees.")
        return values

    def command_translate(self, values):
        x = self.v()
        y = self.v()
        if x is not None:
            x = float(x)
        if y is not None:
            y = float(y)
        matrix = pyembroidery.EmbMatrix()
        matrix.post_translate(x, y)
        for value in values:
            if not isinstance(value, tuple):
                continue
            pattern = value[0]
            pattern.transform(matrix)
            self.log("Transformed", pattern, "by", x, y)
        return values

    def command_conditional(self, values):
        new_values = []
        v0 = self.v()
        for value in values:
            if not isinstance(value, tuple):
                continue
            pattern = value[0]
            filename = value[1]
            formatted = formatted_string(v0, pattern, filename)
            conditional_met = eval(formatted)
            if conditional_met:
                new_values.append(value)
                self.log("Included", pattern, formatted, conditional_met)
            else:
                self.log("Excluded", pattern, formatted, conditional_met)
        self.log("Conditional Finished", len(new_values), "of", len(values), "passed")
        return new_values

    def command_encode_setting(self, values):
        add_settings = {}
        v0 = self.v()
        v1 = self.v()
        while v1 is not None:
            add_settings[v0] = v1
            v0 = self.v()
            v1 = self.v()

        for i, value in enumerate(values):
            if not isinstance(value, tuple):
                continue
            settings = value[2]
            settings.update(add_settings)
        return values

    def command_quiet(self, values):
        self.log = self.no_operation
        return values

    def command_verbose(self, values):
        self.log = print
        return values

    def no_operation(self, *args):
        pass


argv = sys.argv
pyemb = PyEmb(argv)
pyemb.execute()
