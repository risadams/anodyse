# Missing Required Comments Sample

This sample intentionally omits Anodyse annotation comments (like `@title`, `@description`, `@param`, `@warning`, `@example`, `@tag`).

## Purpose

Use this sample to validate fallback behavior when required documentation comments are missing.

## Run

```bash
anodyse samples/missing-comments/deploy-unannotated.yml --output docs/samples --verbose
```

PowerShell:

```powershell
anodyse samples/missing-comments/deploy-unannotated.yml --output docs/samples --verbose
```

## Expected output behavior

- Output markdown is still generated.
- Default/fallback text is used where annotations are absent.
