# Configuration resolution

Language: English · [简体中文](configuration.zh-CN.md)

`strategy_pipeline.config` provides generic configuration loading for public integrations. It reads YAML from filesystem paths or installed package resources, resolves aliases and `extends`, and deep-merges nested mappings. It does not define strategy presets or require a particular workspace layout. Callers supply their own aliases and search paths.

## Resolve a configuration

```python
from strategy_pipeline.config import resolve_config

resolved = resolve_config(
    "experiment",
    aliases={"experiment": "experiment.yml"},
    search_paths=["configs"],
)
config = resolved.data
```

`resolve_config(ref, *, package=None, default_name=None, aliases=None, search_paths=None, normalizer=None)` accepts a path or reference. When `ref` is empty, `default_name` is required. It returns a `ResolvedConfig` containing the resolved mapping, a label, the filesystem path when applicable, and the source identifier.

## Reference lookup order

The initial reference is resolved in this order:

1. Search filesystem candidates. Absolute paths are checked directly. Relative references are checked against the current config file's directory (for inherited configs), the current working directory, then each caller-provided `search_paths` root. For each search root, both the full relative reference and its basename are checked.
2. If filesystem lookup fails and `package` is provided, try the reference basename as a resource in that package.
3. If the reference still cannot be loaded and `aliases` is provided, look up the original reference exactly, then by its lowercase form. Resolve the alias target using the same filesystem and package lookup rules.

`extends` references use the same filesystem and package lookup rules. They do not use the top-level alias mapping.

YAML documents must have a mapping at the root. Empty YAML is treated as an empty mapping. Missing files, unreadable or invalid YAML, and non-mapping roots produce `SystemExit` errors with a message describing the failure.

## Inheritance and merge behavior

The `extends` key accepts one string or a list of strings. Each base is resolved recursively. Bases are merged in list order, then the local mapping is applied, so later bases and the child take precedence. Nested mappings merge recursively; other values, including lists, replace the previous value. The `extends` key is removed from the returned mapping.

If a `normalizer` is supplied, it runs on each loaded mapping before its `extends` field is processed and before that mapping participates in the merge. A circular inheritance chain raises `SystemExit`.

## Result metadata

`ResolvedConfig` contains:

- `data`: the merged configuration mapping.
- `label`: the stem of the final reference or alias target.
- `path`: the resolved filesystem path, or `None` for a package resource.
- `source`: the absolute filesystem path or `package:<package>/<filename>` identifier.

The loader does not validate application-specific keys or types beyond requiring each YAML document's root to be a mapping. The caller remains responsible for schema validation and interpreting the resolved values.

The behavior is covered by `tests/orchestration/test_config.py`, including nested merge precedence, aliases, relative inheritance, search-root basename fallback, circular-inheritance rejection, and an injected normalizer.
