# Examples

Owner-approved outputs, one file each, used as positive examples by verifiers and as references when producing the same kind of artifact.

Each file starts with a three-line header, then the approved output verbatim:

```
what: <the kind of artifact and the request it answered>
approved: YYYY-MM-DD
feedback: FB-nnn
```

Add an example only when the owner approved the output. A rejected output belongs in `tests/fixtures/` as the failing sample for a test, not here.
