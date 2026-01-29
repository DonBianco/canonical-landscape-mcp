# 🔒 Security Policy

## ⚠️ Important Security Notice

**This is a community project and NOT officially supported by Canonical Ltd.**

Security issues in this MCP server should be reported via this repository's GitHub Issues. For security issues with **official Canonical Landscape**, please contact Canonical directly through their official support channels.

## Supported Versions

As this is a community project, there is no formal support matrix. Users should always use the latest version from the `master` branch for the most up-to-date code.

| Version | Supported          |
| ------- | ------------------ |
| Latest (master) | :white_check_mark: Community support |
| Older versions  | :x: Not supported |

## Reporting a Vulnerability

### For Issues in This MCP Server

If you discover a security vulnerability in **this MCP server project**, please:

1. **Do NOT open a public GitHub issue for sensitive security problems**
2. Open a GitHub Issue with the tag `security` (if non-sensitive)
3. For sensitive vulnerabilities, contact the maintainer privately
4. Provide as much detail as possible:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

**Response Time:** As this is a community project maintained by volunteers, response times may vary. There is no guaranteed SLA.

### For Issues in Canonical Landscape

If you discover a security issue in **Canonical Landscape itself** (not this MCP server):

**DO NOT report it here.** Contact Canonical directly:
- 🔒 Canonical Security: https://ubuntu.com/security/disclosure-policy
- 📧 Security Team: security@canonical.com
- 🆘 Official Support: https://ubuntu.com/support

## Security Best Practices

### API Credentials

**CRITICAL: Never commit API credentials to version control!**

1. **Use environment variables:**
   ```bash
   export LANDSCAPE_API_URI="https://landscape.example.com/api/"
   export LANDSCAPE_API_KEY="your-key"
   export LANDSCAPE_API_SECRET="your-secret"
   ```

2. **Use `.env` files (excluded from git):**
   ```bash
   echo 'LANDSCAPE_API_URI=https://landscape.example.com/api/' > .env
   echo 'LANDSCAPE_API_KEY=your-key' >> .env
   echo 'LANDSCAPE_API_SECRET=your-secret' >> .env
   ```

3. **For production deployments:**
   - Use systemd environment files
   - Use secrets management tools (Vault, AWS Secrets Manager, etc.)
   - Never hardcode credentials in Python files
   - Restrict file permissions (`chmod 600` for config files)

### Network Security

1. **HTTPS Only:** Always use HTTPS URLs for `LANDSCAPE_API_URI`
2. **Firewall Rules:** If running HTTP server, restrict access with firewall rules
3. **Private Networks:** Deploy on private networks when possible
4. **VPN/Bastion:** Access remote deployments via VPN or bastion hosts

### API Key Management

1. **Principle of Least Privilege:** Use read-only API keys if possible
2. **Key Rotation:** Rotate API keys regularly
3. **Separate Keys:** Use different API keys for dev/staging/production
4. **Audit Logs:** Monitor API usage in Landscape audit logs
5. **Revoke Immediately:** If keys are compromised, revoke them in Landscape immediately

### Deployment Security

#### Local (stdio) Deployment

- Credentials stored in environment variables or `landscape_mcp.py`
- Access limited to local user running Claude Code
- Lower risk as it's single-user, local access

#### HTTP Server Deployment

⚠️ **Higher Risk** - Exposing HTTP endpoint requires additional security:

1. **Authentication:** The current HTTP server has NO authentication
   - Only deploy on trusted networks
   - Use reverse proxy with authentication (nginx + basic auth)
   - Consider adding custom authentication layer

2. **Network Isolation:**
   - Bind to `127.0.0.1` for local-only access
   - Use firewall rules to restrict access
   - Deploy behind VPN or within private network

3. **TLS/SSL:**
   - Use reverse proxy (nginx, caddy) for HTTPS
   - Never expose HTTP server directly to internet without TLS

4. **Monitoring:**
   - Monitor access logs
   - Set up alerting for unusual activity
   - Review systemd journal logs regularly

### Code Security

1. **Review the Code:** This is open source - review it before deployment
2. **Dependencies:** Keep dependencies updated (`uv pip install --upgrade`)
3. **Python Version:** Use supported Python versions (3.10+)
4. **Vulnerability Scanning:** Run security scanners on dependencies

### Infrastructure Security

1. **Landscape Server:** Ensure your Landscape server is properly secured
2. **Client Machines:** This tool queries client data - secure your clients
3. **API Permissions:** Review what this MCP server can access via API
4. **Data Handling:** This tool doesn't persist data, but Claude Code logs may contain query results

## Security Limitations

**Important:** This project has the following security limitations:

1. ❌ **No security audit has been performed**
2. ❌ **No authentication in HTTP mode**
3. ❌ **No rate limiting implemented**
4. ❌ **No input sanitization beyond API client**
5. ❌ **No encryption at rest (credentials in config files)**
6. ❌ **Logging may expose sensitive data**

**Users accept these limitations by using this software.**

## Disclaimer

This security policy is provided for community benefit but comes with **NO GUARANTEES**.

- The maintainers are NOT responsible for security breaches
- The maintainers are NOT liable for data exposure
- Users are responsible for their own security posture
- This is NOT a security-certified product

For enterprise-grade, security-certified infrastructure management, please use official Canonical products and services.

## Data Privacy

This MCP server:
- ✅ Does NOT store any data persistently
- ✅ Does NOT send data to third parties
- ✅ Only queries your Landscape API as requested
- ⚠️ Query results may appear in Claude Code logs
- ⚠️ Claude Code may send queries to Anthropic's API (see Claude's privacy policy)

## Compliance

This project has NOT been evaluated for compliance with:
- GDPR
- HIPAA
- SOC 2
- ISO 27001
- PCI DSS
- Any other security/privacy standards

**Users are responsible for ensuring compliance with applicable regulations.**

## Updates and Patches

- Security updates will be pushed to the `master` branch
- No formal CVE tracking or security advisories
- Watch the repository for updates
- Subscribe to GitHub notifications for security-related commits

## Contact

For security questions about this project:
- Open a GitHub Issue (for non-sensitive matters)
- Check existing issues first

For security questions about official Canonical products:
- Contact Canonical directly
- Visit https://ubuntu.com/security

---

**Last Updated:** January 2026

**Remember:** This is a community tool. Use at your own risk. For production/enterprise use, thoroughly evaluate security implications for your specific environment.
