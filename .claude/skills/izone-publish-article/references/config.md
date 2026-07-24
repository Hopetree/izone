# Configuration Reference

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `IZONE_API_TOKEN` | **yes** | — | DRF auth token, created in Admin at `/adminx/authtoken/token/` |
| `IZONE_API_BASE` | no | `http://127.0.0.1:8000/openapi/v1` | Blog API base URL, no trailing slash |

The article author is automatically set to the user associated with the token.

Set them in your shell profile (`.zshrc`, `.bashrc`) or per-session:

```bash
export IZONE_API_TOKEN="your-token-here"
export IZONE_API_BASE="http://127.0.0.1:8090/openapi/v1"
```

## Token Management

Tokens are managed in Django Admin (`/adminx/authtoken/token/`). Each token belongs to a user.
