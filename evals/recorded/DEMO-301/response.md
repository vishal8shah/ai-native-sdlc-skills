Completed DEMO-301 in `/tmp/demo-301-2gfnrdn1`.

```python
def request_is_valid(value=None):
    return isinstance(value, str) and bool(value.strip())
```

Actual verification:

```text
python3 -m unittest -v test_request_validation.py
Ran 4 tests in 0.000s
OK
Exit code: 0
```

The tests cover 20 input cases, including omitted arguments, `None`, Unicode whitespace, nonblank strings, and non-string values.

Preserved outputs:

- [Implementation](sandbox:/tmp/demo-301-2gfnrdn1/request_validation.py)
- [Tests](sandbox:/tmp/demo-301-2gfnrdn1/test_request_validation.py)
- [Plan and result](sandbox:/tmp/demo-301-2gfnrdn1/plan-result.md)
- [Actual output and SHA-256 evidence](sandbox:/tmp/demo-301-2gfnrdn1/verification.txt)
- [Supplied source context](sandbox:/tmp/demo-301-2gfnrdn1/source-context.md)

No external services or production actions. Whitespace follows Python’s `str.strip()` semantics. The artifact records completed implementation and verification, with owner acceptance unrecorded.
