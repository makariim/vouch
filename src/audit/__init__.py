"""Evidence audit: every requirement in a job post, checked against the resume."""

# Before anything else in the package. Importing `audit.anything` runs this
# file first -- that is a language guarantee, not a convention -- so this is the
# one place that is reliably earlier than every entry point: the CLI, the
# server, and the tests alike.
#
# Earlier matters. `model.py` reads `AUDIT_PROVIDER` and the model ids at
# module level, so doing this inside `build_model()` would be too late for
# those: the module has already been imported and has already read an
# environment that did not have the file's values in it yet. Here, one line,
# before the first `from .`, fixes the key and those together.
from .env import load as _load_env

_load_env()

from .graph import AuditError, build_graph, run, run_stream  # noqa: E402

__all__ = ["AuditError", "build_graph", "run", "run_stream"]
