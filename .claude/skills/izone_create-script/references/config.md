# API Configuration

## Environment Variables

```bash
IZONE_ADMIN_TOKEN="<your-admin-token>"
IZONE_API_BASE="https://tendcode.com/openapi/v1"
```

- **IZONE_ADMIN_TOKEN**: API authentication token for admin-level operations. Token must be associated with a staff/superuser account (scripts feature requires admin access). Created in Admin at `/adminx/authtoken/token/`.
- **IZONE_API_BASE**: API base URL. Production: `https://tendcode.com/openapi/v1`, Development: `http://127.0.0.1:8090/openapi/v1`.

## Difference from IZONE_API_TOKEN

- `IZONE_API_TOKEN` — used by `publish-article` skill (generic token auth, article operations)
- `IZONE_ADMIN_TOKEN` — used by `create-script` skill (admin token auth, script management)

Both tokens can share the same value if the user has admin privileges.

## Verification

```bash
curl -s -H "Authorization: Token $IZONE_ADMIN_TOKEN" "$IZONE_API_BASE/skill/scripts/?slug=test"
```
