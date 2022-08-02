import os
import re
import subprocess
import itertools

class SourceAddress:
    def __init__(self, addr, name=None, filename=None, line=None):
        self.addr = addr
        self.name = name
        self.filename = filename
        self.line = line

    def __str__(self):
        return self.name or '0x%x' % self.addr

class DummyResolver(object):
    def __init__(self):
        self.cache = {}

    def __call__(self, addr):
        result = self.cache.get(addr, None)
        if not result:
            result = [SourceAddress(addr)]
            self.cache[addr] = result
        return result

class SymbolResolver(object):
    inline_prefix = ' (inlined by) '

    def __init__(self, object_path, fallback_resolver=DummyResolver(), show_inline=True):
        if not os.path.exists(object_path):
            raise Exception(f'File not found: {object_path}')
        self.show_inline = show_inline
        self.fallback_resolver = fallback_resolver
        flags = '-Cfp'
        if show_inline:
            flags += 'i'
        self.addr2line = subprocess.Popen(['addr2line', '-e', object_path, flags],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        self.cache = {}

    def next_line(self):
        return self.addr2line.stdout.readline().rstrip('\n')

    def consume_unknown(self, line):
        if m := re.match(r'^\?\?$', line):
            line = self.next_line()
            if not re.match(r'^\?\?:0$', line):
                raise Exception(f'Unexpected response: {line}')
            return True

        if m := re.match(r'^\?\? \?\?:0$', line):
            return True

    def parse_line(self, addr, line):
        if self.consume_unknown(line):
            return self.fallback_resolver(addr)

        if m := re.match(
            r'(?P<name>.*) at ((?P<file>.*?)|\?+):((?P<line>\d+)|\?+)', line
        ):
            return [SourceAddress(addr, m['name'], m['file'], m['line'])]
        else:
            raise Exception(f'addr2line response not matched: {line}')

    def __call__(self, addr):
        """
        Returns an iterable of SourceAddress objects for given addr.

        """

        result = self.cache.get(addr, None)
        if result:
            return result

        self.addr2line.stdin.write('0x%x\n' % addr)

        if self.show_inline:
            self.addr2line.stdin.write('0\n')

        self.addr2line.stdin.flush()
        result = self.parse_line(addr, self.next_line())

        if self.show_inline:
            line = self.next_line()
            while line.startswith(self.inline_prefix):
                result.extend(self.parse_line(addr, line[len(self.inline_prefix):]))
                line = self.next_line()
            self.consume_unknown(line)

        self.cache[addr] = result
        return result

    def close():
        self.addr2line.stdin.close()
        self.addr2line.wait()

def resolve_all(resolver, raw_addresses):
    """
    Returns iterable of SourceAddress objects for given list of raw addresses
    using supplied resolver.

    """
    return itertools.chain.from_iterable(map(resolver, raw_addresses))
