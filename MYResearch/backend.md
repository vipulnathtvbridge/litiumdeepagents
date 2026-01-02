Implement Policy hooks 
class GuardedBackend(FilesystemBackend):
    ALLOWED_PREFIXES = ["/project/components/", "/project/styles/"]
    BLOCKED_FILES = ["package.json", "tsconfig.json"]

    def write(self, file_path: str, content: str):
        if not any(file_path.startswith(p) for p in self.ALLOWED_PREFIXES):
            return WriteResult(error="Writes outside allowed directories are blocked")

        if any(file_path.endswith(f) for f in self.BLOCKED_FILES):
            return WriteResult(error="Editing this file is forbidden")

        return super().write(file_path, content)

🧩 How This Fits with CompositeBackend

Your full stack now looks like:

Agent
 ├── CompositeBackend
 │   ├── /agent → FilesystemBackend (logs)
 │   └── /project → GuardedBackend (protected)
 │
 └── Policy Hooks (write/edit)


✔ Clean
✔ Safe
✔ Auditable
✔ Production-grade

######################### Styling only Policy ##########3

from deepagents.backends.protocol import BackendProtocol, WriteResult, EditResult
from pathlib import Path

class StylingPolicy(BackendProtocol):
    """
    Enforces styling-only changes:
    - Allows UI component edits
    - Blocks config, build, backend files
    - Prevents dangerous writes
    """

    ALLOWED_DIRS = [
        "/project/components/",
        "/project/styles/",
        "/project/app/",
        "/project/pages/",
    ]

    ALLOWED_EXTENSIONS = {
        ".tsx", ".ts", ".jsx", ".css", ".scss", ".module.css"
    }

    BLOCKED_FILES = {
        "package.json",
        "package-lock.json",
        "tsconfig.json",
        "next.config.js",
        ".env",
    }

    def __init__(self, inner: BackendProtocol):
        self.inner = inner

    # -----------------------
    # Helpers
    # -----------------------

    def _is_allowed_path(self, path: str) -> bool:
        return any(path.startswith(d) for d in self.ALLOWED_DIRS)

    def _is_allowed_file(self, path: str) -> bool:
        ext = Path(path).suffix
        name = Path(path).name
        return (
            ext in self.ALLOWED_EXTENSIONS and
            name not in self.BLOCKED_FILES
        )

    def _deny(self, path: str) -> bool:
        return not (
            self._is_allowed_path(path) and
            self._is_allowed_file(path)
        )

    # -----------------------
    # Backend methods
    # -----------------------

    def write(self, file_path: str, content: str) -> WriteResult:
        if self._deny(file_path):
            return WriteResult(
                error=f"❌ Styling policy violation: write not allowed → {file_path}"
            )
        return self.inner.write(file_path, content)

    def edit(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False
    ) -> EditResult:
        if self._deny(file_path):
            return EditResult(
                error=f"❌ Styling policy violation: edit not allowed → {file_path}"
            )
        return self.inner.edit(file_path, old_string, new_string, replace_all)

    # Passthroughs
    def read(self, *args, **kwargs):
        return self.inner.read(*args, **kwargs)

    def ls_info(self, *args, **kwargs):
        return self.inner.ls_info(*args, **kwargs)

    def glob_info(self, *args, **kwargs):
        return self.inner.glob_info(*args, **kwargs)

    def grep_raw(self, *args, **kwargs):
        return self.inner.grep_raw(*args, **kwargs)


backend = CompositeBackend(
    routes={
        "/project/": StylingPolicy(
            FilesystemBackend(
                root_dir=r"C:\ecommerce\trendcart\gleemart-fe"
            )
        ),
        "/agent/": FilesystemBackend(
            root_dir=r"C:\ecommerce\trendcart\deepagent"
        )
    }
)


agent = create_deep_agent(
    model=model,
    backend=backend,
    system_prompt=orchestrator_prompt
)

############ Tool design not to bypass backend #######
# While creating backend edit tools
from deepagents.tools import tool

@tool
def write_file(path: str, content: str):
    return backend.write(path, content)