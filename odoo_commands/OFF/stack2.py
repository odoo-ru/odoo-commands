@PathEntryFinder.register
class MetaFileFinder:
    """
    A 'middleware', if you will, between the PathFinder sys.meta_path hook,
    and sys.path_hooks hooks--particularly FileFinder.

    The hook returned by FileFinder.path_hook is rather 'promiscuous' in that
    it will handle *any* directory.  So if one wants to insert another
    FileFinder.path_hook into sys.path_hooks, that will totally take over
    importing for any directory, and previous path hooks will be ignored.

    This class provides its own sys.path_hooks hook as follows: If inserted
    on sys.path_hooks (it should be inserted early so that it can supersede
    anything else).  Its find_spec method then calls each hook on
    sys.path_hooks after itself and, for each hook that can handle the given
    sys.path entry, it calls the hook to create a finder, and calls that
    finder's find_spec.  So each sys.path_hooks entry is tried until a spec is
    found or all finders are exhausted.
    """

    class hook:
        """
        Use this little internal class rather than a function with a closure
        or a classmethod or anything like that so that it's easier to
        identify our hook and skip over it while processing sys.path_hooks.
        """

        def __init__(self, basepath=None):
            self.basepath = os.path.abspath(basepath)

        def __call__(self, path):
            if not os.path.isdir(path):
                raise ImportError('only directories are supported', path=path)
            elif not self.handles(path):
                raise ImportError(
                    'only directories under {} are supported'.format(
                        self.basepath), path=path)

            return MetaFileFinder(path)

        def handles(self, path):
            """
            Return whether this hook will handle the given path, depending on
            what its basepath is.
            """

            path = os.path.abspath(path)

            return (self.basepath is None or
                    os.path.commonpath([self.basepath, path]) == self.basepath)

    def __init__(self, path):
        self.path = path
        self._finder_cache = {}

    def __repr__(self):
        return '{}({!r})'.format(self.__class__.__name__, self.path)

    def find_spec(self, fullname, target=None):
        if not sys.path_hooks:
            return None

        last = len(sys.path_hooks) - 1

        for idx, hook in enumerate(sys.path_hooks):
            if isinstance(hook, self.__class__.hook):
                continue

            finder = None
            try:
                if hook in self._finder_cache:
                    finder = self._finder_cache[hook]
                    if finder is None:
                        # We've tried this finder before and got an ImportError
                        continue
            except TypeError:
                # The hook is unhashable
                pass

            if finder is None:
                try:
                    finder = hook(self.path)
                except ImportError:
                    pass

            try:
                self._finder_cache[hook] = finder
            except TypeError:
                # The hook is unhashable for some reason so we don't bother
                # caching it
                pass

            if finder is not None:
                spec = finder.find_spec(fullname, target)
                if (spec is not None and
                        (spec.loader is not None or idx == last)):
                    # If no __ini
