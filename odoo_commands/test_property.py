from functools import cached_property


class Test:
    @cached_property
    def env(self):
        try:
            print('enter')
            yield 'value'
        finally:
            print('finally')


t = Test()
print(t.prop)
print('before exit')
