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

class search_tools:
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