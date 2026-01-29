# Usage Examples

Real-world examples of using Landscape MCP with Claude Code.

## Getting Started

Once you've installed and configured Landscape MCP, you can start querying your infrastructure using natural language in Claude Code.

## Basic Queries

### List All Computers

**You ask:**
> "Show me all computers in Landscape"

**Claude uses:** `landscape_query_computers(limit=25)`

**Response:**
```json
[
  {
    "id": 123,
    "hostname": "server-prod-01",
    "distribution": "Ubuntu 24.04 LTS",
    "last_ping_time": "2026-01-27T10:30:00Z",
    "tags": ["production", "web-server"]
  },
  {
    "id": 124,
    "hostname": "dev-laptop-02",
    "distribution": "Ubuntu 22.04 LTS",
    "last_ping_time": "2026-01-27T10:25:00Z",
    "tags": ["development"]
  }
  // ... more computers
]
```

### Find Computers by Tag

**You ask:**
> "Show me all production servers"

**Claude uses:** `landscape_query_computers(query="tag:production")`

**Result:** Lists all computers tagged with "production"

### Check Computers Needing Reboot

**You ask:**
> "Which machines need a reboot?"

**Claude uses:** `landscape_query_computers(query="needs:reboot:true")`

**Result:** Lists all computers that require a system reboot

## Package Queries

### Search for a Package

**You ask:**
> "Is nginx installed anywhere?"

**Claude uses:** `landscape_query_packages(search="nginx")`

**Response:**
```json
[
  {
    "name": "nginx",
    "version": "1.24.0-2ubuntu1",
    "computer_id": 123,
    "hostname": "server-prod-01",
    "summary": "High performance web server"
  },
  {
    "name": "nginx",
    "version": "1.18.0-6ubuntu1",
    "computer_id": 125,
    "hostname": "server-prod-03",
    "summary": "High performance web server"
  }
]
```

### Check Package on Specific Computer

**You ask:**
> "Is Docker installed on server-prod-01?"

**Claude uses:** `landscape_fast_package_lookup(hostname="server-prod-01", package="docker")`

**Response:**
```json
{
  "hostname": "server-prod-01",
  "package": "docker.io",
  "version": "24.0.5-0ubuntu1",
  "summary": "Linux container runtime"
}
```

**Or if not installed:**
```json
{
  "hostname": "server-prod-01",
  "package": "docker",
  "status": "not_installed"
}
```

## Activity Monitoring

### Check Recent Activities

**You ask:**
> "Show me recent activities for dev-laptop-02"

**Claude uses:** `landscape_query_activities(hostname="dev-laptop-02", limit=5)`

**Response:**
```json
[
  {
    "id": 1001,
    "type": "package-upgrade",
    "status": "succeeded",
    "summary": "Upgraded 15 packages",
    "timestamp": "2026-01-27T09:00:00Z"
  },
  {
    "id": 1000,
    "type": "reboot",
    "status": "succeeded",
    "summary": "System reboot completed",
    "timestamp": "2026-01-26T18:00:00Z"
  }
  // ... more activities
]
```

### Filter Activities by Status

**You ask:**
> "Show me failed activities from the last week"

**Claude uses:** `landscape_query_activities(query="status:failed created-after:2026-01-20", limit=10)`

## Alert Management

### Check Active Alerts

**You ask:**
> "What alerts do we have?"

**Claude uses:** `landscape_query_alerts()`

**Response:**
```json
[
  {
    "computer_id": 126,
    "hostname": "server-prod-04",
    "alert_type": "disk-space",
    "severity": "warning",
    "message": "Disk usage above 85% on /dev/sda1"
  },
  {
    "computer_id": 127,
    "hostname": "backup-server-01",
    "alert_type": "offline",
    "severity": "critical",
    "message": "Computer not responding"
  }
]
```

## Offline Computer Detection

### Find Offline Computers

**You ask:**
> "Which computers haven't checked in for the last 2 hours?"

**Claude uses:** `landscape_query_offline(since_minutes=120)`

**Response:**
```json
[
  {
    "id": 127,
    "hostname": "backup-server-01",
    "last_ping_time": "2026-01-27T08:00:00Z",
    "offline_duration_minutes": 150
  },
  {
    "id": 128,
    "hostname": "old-test-server",
    "last_ping_time": "2026-01-26T20:00:00Z",
    "offline_duration_minutes": 870
  }
]
```

## Complex Queries

### Multi-Criteria Search

**You ask:**
> "Show me all production web servers running Ubuntu 24.04"

**Claude uses:** `landscape_query_computers(query="tag:production tag:web-server distribution:24.04")`

### Package Comparison

**You ask:**
> "Compare Python versions across all development machines"

**Claude analyzes:**
1. Uses `landscape_query_computers(query="tag:development")`
2. For each computer, uses `landscape_fast_package_lookup(hostname=..., package="python3")`
3. Summarizes results in a table

**Sample Output:**
```
Python Versions on Development Machines:
┌─────────────────┬─────────┐
│ Hostname        │ Version │
├─────────────────┼─────────┤
│ dev-laptop-01   │ 3.12.1  │
│ dev-laptop-02   │ 3.11.7  │
│ dev-server-01   │ 3.12.1  │
│ dev-server-02   │ 3.10.12 │
└─────────────────┴─────────┘

⚠️ Note: dev-laptop-02 and dev-server-02 are running older versions
```

### Security Audit

**You ask:**
> "Are there any computers with critical security updates pending?"

**Claude analyzes:**
1. Uses `landscape_query_computers()` to get all systems
2. Filters by security update status
3. Provides summary with recommendations

## Advanced Use Cases

### Infrastructure Report

**You ask:**
> "Generate a summary report of my infrastructure"

**Claude performs:**
```
1. Total computers: landscape_query_computers(limit=1000)
2. Offline machines: landscape_query_offline(since_minutes=60)
3. Computers needing reboot: landscape_query_computers(query="needs:reboot:true")
4. Active alerts: landscape_query_alerts()
5. Recent activities: landscape_query_activities(limit=10)
```

**Sample Report:**
```
📊 Infrastructure Report (as of 2026-01-27 10:45 UTC)

Total Computers: 47
├─ Online: 45 (95.7%)
└─ Offline: 2 (4.3%)

System Status:
├─ Computers needing reboot: 8
├─ Active alerts: 3
└─ Recent failed activities: 1

Distribution Breakdown:
├─ Ubuntu 24.04 LTS: 32 computers
├─ Ubuntu 22.04 LTS: 13 computers
└─ Ubuntu 20.04 LTS: 2 computers

⚠️ Action Items:
1. Investigate 2 offline computers
2. Schedule reboots for 8 computers
3. Review 3 active alerts (1 critical)
```

### Compliance Check

**You ask:**
> "Which production servers are not running the latest Ubuntu LTS?"

**Claude performs:**
```
1. Get production servers: landscape_query_computers(query="tag:production")
2. Filter by distribution
3. List outdated systems
```

### Package Rollout Verification

**You ask:**
> "Has the nginx update been deployed to all web servers?"

**Claude performs:**
```
1. Get web servers: landscape_query_computers(query="tag:web-server")
2. For each server: landscape_fast_package_lookup(hostname=..., package="nginx")
3. Compare versions
4. Report status
```

**Sample Output:**
```
Nginx Deployment Status:

Target version: 1.24.0-2ubuntu1

✅ Up to date (3/5):
  • server-prod-01: 1.24.0-2ubuntu1
  • server-prod-02: 1.24.0-2ubuntu1
  • server-prod-03: 1.24.0-2ubuntu1

⚠️ Needs update (2/5):
  • server-prod-04: 1.18.0-6ubuntu1
  • server-prod-05: 1.18.0-6ubuntu1

Recommendation: Update 2 remaining servers
```

## Tips for Effective Queries

### Be Specific
❌ "Show me servers"
✅ "Show me all production web servers running Ubuntu 24.04"

### Use Natural Language
Claude understands context and can chain multiple queries:
- "Find all computers with Docker installed"
- "Then check which ones need a reboot"

### Ask for Analysis
Don't just request data - ask for insights:
- "What's the status of my infrastructure?"
- "Are there any security concerns?"
- "Which systems need attention?"

### Combine Queries
Claude can perform complex multi-step analysis:
- "Compare package versions across environments"
- "Generate a compliance report"
- "Identify systems that need updates"

## Query Syntax Reference

When Claude constructs queries, it uses these patterns:

| Pattern | Example | Description |
|---------|---------|-------------|
| `tag:NAME` | `tag:production` | Filter by tag |
| `hostname:NAME` | `hostname:server-01` | Specific computer |
| `distribution:VERSION` | `distribution:24.04` | OS version |
| `needs:reboot:BOOL` | `needs:reboot:true` | Reboot required |
| Multiple filters | `tag:prod tag:web` | AND logic |

## More Examples

See [README.md](README.md) for more documentation and the full list of available tools.

---

**Questions?** Open an issue on [GitHub](https://github.com/yourusername/landscape-mcp/issues)
