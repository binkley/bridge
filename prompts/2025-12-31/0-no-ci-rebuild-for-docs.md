The most idiomatic way to handle recursive file ignoring in GitHub Actions is
to use the Globstar (`**`) pattern. While your current pattern `'**.md'` is
technically valid and should match recursively in GitHub's implementation, the
standard and most explicit industry convention is `'**/*.md'`.

Here is the refined, idiomatic configuration for your CI pipeline:

## 1. The Standard Recursive Ignore

To catch Markdown files in the project root, your prompt subdirectories, and
any other nested folders, use this structure:

```yaml
on:
  push:
    paths-ignore:
      - '**/*.md'     # Matches .md files in any directory recursively
      - 'images/**'   # Matches everything inside the images folder
  pull_request:
    paths-ignore:
      - '**/*.md'
      - 'images/**'
  workflow_dispatch:  # Manual trigger remains unaffected by path filters
```

## 2. Why this is the "Idiomatic" approach

* Recursive Matching: In GitHub Actions globbing, `**` matches zero or more
  directories. By using `**/*.md`, you explicitly signal to other developers
  that you are targeting the file extension regardless of its depth in the tree.
* Clarity vs. `**.md`: While GitHub often treats `**.md` as recursive, some
  glob implementations treat it differently than `**/*.md`. Using the slash
  (`/`) is the standard way to denote "any directory and then a file".

### Alternative: The "Positive Filter" Pattern (Cleanest)

If your project follows a standard structure (e.g., all code is in src/ or
app/), it is often considered "cleaner" to define what should trigger the
build rather than a long list of what shouldn't. This prevents the pipeline
from accidentally running when you add other non-code files (like
`.gitignore`, `.txt`, or `.pdf`).

```yaml
on:
  push:
    paths:
      - 'src/**'      # Only run CI if files in src/ are changed
      - 'package.json' # Or specific root-level config files
```

## Manual "One-Off" Ignore

If you ever need to push a specific change that should have triggered the CI
but you want to skip it manually, you can include `[skip ci]` or `[ci skip]`
anywhere in your commit message. This is a built-in GitHub feature that
bypasses both `push` and `pull_request` workflows for that specific commit.
