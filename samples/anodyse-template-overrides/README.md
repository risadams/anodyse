# Anodyse Template Override Sample

This sample shows how to override Anodyse's built-in Jinja2 templates using a local `/.anodyse/templates/` folder.

## What this sample contains

- `templates/playbook.md.j2`
- `templates/role.md.j2`
- `templates/index.md.j2`

These files intentionally use a visibly different layout so you can confirm your custom templates are being loaded.

## How to use

From the repository root:

```bash
# 1) Create the override folder expected by Anodyse
mkdir -p .anodyse/templates

# 2) Copy sample templates into it
cp samples/anodyse-template-overrides/templates/*.j2 .anodyse/templates/

# 3) Generate docs as usual
anodyse samples/web-server/deploy-nginx.yml --output docs/custom-templates --verbose
```

On PowerShell (Windows):

```powershell
New-Item -ItemType Directory -Path .anodyse/templates -Force | Out-Null
Copy-Item samples/anodyse-template-overrides/templates/*.j2 .anodyse/templates/
anodyse samples/web-server/deploy-nginx.yml --output docs/custom-templates --verbose
```

## Expected behavior

- Anodyse checks `/.anodyse/templates/` first
- If a template file exists there, it overrides the package default
- If a file is missing, Anodyse falls back to the built-in template

## Notes

- Template names must match exactly: `playbook.md.j2`, `role.md.j2`, `index.md.j2`
- The override path is resolved from your current working directory
