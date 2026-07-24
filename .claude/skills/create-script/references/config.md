# API Configuration

## Environment Variables

```bash
IZONE_API_TOKEN="<your-token>"
IZONE_API_BASE="https://tendcode.com/openapi/v1"
```

- **IZONE_API_TOKEN**: API authentication token. Created in Admin at `/adminx/authtoken/token/`.
- **IZONE_API_BASE**: API base URL. Production: `https://tendcode.com/openapi/v1`, Development: `http://127.0.0.1:8090/openapi/v1`.

## Verification

```bash
curl -s -H "Authorization: Token $IZONE_API_TOKEN" "$IZONE_API_BASE/skill/meta/"
```
