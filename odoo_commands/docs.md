
```python
>>> sys.path_hooks
[
    <class 'zipimport.zipimporter'>, 
    <function FileFinder.path_hook.<locals>.path_hook_for_FileFinder at 0x7f182221edc0>,
]
>>> ff_hook = sys.path_hooks[-1]
>>> ff_hook('.')
FileFinder('.')
>>> sys.meta_path
[
    <class '_frozen_importlib.BuiltinImporter'>,
    <class '_frozen_importlib.FrozenImporter'>,
    <class '_frozen_importlib_external.PathFinder'>,
]

```
path based finder search in `sys.path` dirs. for subpackages use __path__
sys.path_hooks 
