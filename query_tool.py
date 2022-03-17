import inspect
import re

class RegexError(Exception):
    """Custom exception class for non-existant patterns."""

    __module__ = 'builtins'

    def __init__(self, *args) -> None:
        if args:
            self.errmessage = args[0]
        else:
            self.errmessage = None

    def __repr__(self) -> str:
        if self.errmessage:
            return '{0} '.format(self.errmessage)
        else:
            return 'RegexError has been raised'

class __tools:
    def __init__(self, fl, pattern) -> None:
        self.fl = fl
        self.pattern = pattern

    def _fl_parser(self):
        
        assert self.fl
        if self.fl.endswith('.txt'):
            with open(self.fl, "r") as txt:
                lines = txt.readlines()
                txt.seek(0)
                all_lines = []
                for index, line in enumerate(lines):
                    ln_index = str(index)+': '+line
                    ln_index = ln_index.replace('\n', '')
                    all_lines.append(ln_index)
        return all_lines

    def _get_matches(self):
        
        ln_lst = self._fl_parser()
        found = {}
        lst_str = ''.join(ln_lst)
        a = re.findall(self.pattern, lst_str)
        if len(a) == 0:
            raise RegexError(f"pattern: {self.pattern}, doesn't exist!")
        for i in ln_lst:
            if re.search(self.pattern, i):
                key, value = i.split(':', 1)
                key = key.strip()
                value = value.strip()
                found[key] = value
        return found

class query_tool(__tools):
    def __init__(self, fl, pattern) -> None:
        super().__init__(fl, pattern)

    def __repr__(self) -> str:
        params = inspect.getfullargspec(__class__).args
        params.remove("self")
        return f'{__class__.__name__}({params[0]} = "{self.fl}", {params[1]} = "{self.pattern}")'

    def _dict_parser(dictionary):
        keys = []
        values = []
        for key, value in dictionary.items():
            keys.append(key)
            values.append(value)

        keys = tuple(keys)
        keys = ", ".join(keys)
        values = tuple(values)
        values = ", ".join(values)
        return keys, values

    def query(self, show_idx = True, get_matches = False):
        dictionary = __tools(fl = self.fl, pattern = self.pattern)._get_matches()
        print(f"There are {len(dictionary)} matches to the pattern {self.pattern}")
        if show_idx:
            keys = self._dict_parser(dictionary = dictionary)[0]
            if len(keys) > 1:
                print(f"Pattern can be found in lines: {keys}.")
            else:
                print(f"Pattern can be found in line {keys}.")
        if get_matches:
            return self._dict_parser(dictionary = dictionary)[0], self._dict_parser(dictionary = dictionary)[1]
        else:
            self._dict_parser(dictionary = dictionary)[0]

## Testing
if __name__ == "__main__":
    get = query_tool(fl = "an_example.txt", pattern = "html")
    get.query()
