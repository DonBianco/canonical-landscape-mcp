# Changelog

All notable changes to Landscape MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- Planned features for future releases

## [1.0.0] - 2026-01-27

### 🎉 Initial Release

First public release of Landscape MCP Server!

### Added

#### Core Features
- MCP server implementation with stdio transport for Claude Code integration
- HTTP server variant with SSE transport for remote deployment
- Six MCP tools for comprehensive Landscape API access:
  - `landscape_query_computers` - Query computers by tags, hostname, status
  - `landscape_query_packages` - Search for packages across infrastructure
  - `landscape_query_activities` - Get audit logs and activity history
  - `landscape_query_alerts` - Check system alerts
  - `landscape_query_offline` - Find computers that haven't checked in
  - `landscape_fast_package_lookup` - Quick package version check on specific host

#### Installation & Setup
- Automated installation script (`install.sh`) using UV package manager
- Environment variable support for API credentials
- Claude Code configuration generator
- Virtual environment setup
- Dependency management with UV

#### Testing Infrastructure
- Installation test suite (`test-install.sh`)
- MCP server functionality tests (`test-mcp-server.sh`)
- HTTP server endpoint tests (`test-http.sh`)
- GitHub Actions workflow for CI/CD
- Automated testing on Python 3.10, 3.11, 3.12
- Syntax validation and import checks
- Security scanning for sensitive data

#### Documentation
- Comprehensive README with setup instructions
- Quick start guide (QUICKSTART.md)
- Real-world usage examples (EXAMPLES.md)
- Contribution guidelines (CONTRIBUTING.md)
- Publishing guide (PUBLISH.md)
- Project summary (PROJECT_SUMMARY.md)
- Files manifest (FILES_MANIFEST.md)
- Quick reference card (QUICK_REFERENCE.md)
- MIT License

#### Dashboard
- Streamlit-based web dashboard for infrastructure visualization
- Computer inventory with filtering
- Distribution and tag analytics
- Annotation management
- Interactive visualizations with Plotly

#### Deployment
- HTTP server deployment script (`deploy-http.sh`)
- Systemd service configuration examples
- Remote deployment support with SSE transport
- Environment variable configuration

### Security
- No hardcoded credentials (environment variable support)
- Generic placeholder examples in code
- .gitignore protecting sensitive files
- Read-only API access pattern
- HTTPS communication

### Technical Stack
- Python 3.10+ support
- MCP Framework 1.24.0
- Landscape API Python client 0.9.0
- Starlette + Uvicorn for HTTP server
- UV package manager integration
- GitHub Actions for CI/CD

---

## Future Plans

### v1.1.0 (Planned)
- [ ] Docker support for easy deployment
- [ ] More query filters and search options
- [ ] Bulk operations support
- [ ] Custom script integration
- [ ] Webhook support for notifications
- [ ] Enhanced error handling and logging
- [ ] Performance optimizations

### v1.2.0 (Planned)
- [ ] Support for Landscape Cloud
- [ ] Multi-tenant support
- [ ] Role-based access control
- [ ] REST API wrapper
- [ ] Prometheus metrics export
- [ ] Grafana dashboard templates

### Long-term Ideas
- [ ] Support for other MCP clients (not just Claude Code)
- [ ] Plugin system for custom tools
- [ ] Integration with other system management tools
- [ ] Mobile app support
- [ ] Real-time notifications
- [ ] Machine learning for anomaly detection

---

## Version History

| Version | Release Date | Highlights |
|---------|-------------|------------|
| 1.0.0 | 2026-01-27 | 🎉 Initial public release |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute to this project.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/landscape-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/landscape-mcp/discussions)

---

**Note**: This project follows [Semantic Versioning](https://semver.org/):
- MAJOR version for incompatible API changes
- MINOR version for new functionality in a backward compatible manner
- PATCH version for backward compatible bug fixes
