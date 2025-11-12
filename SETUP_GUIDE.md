# GitHub Copilot Workshop - Advanced Level - Setup Guide

## What's Been Created

This workshop contains 3 advanced challenges with actual codebases for hands-on practice.

### Challenge 1: Multi-Agent Architecture Review ✅
**Location**: `challenges/01-architecture-review/`

**Codebase**: TechMart E-Commerce Microservices Platform
- API Gateway (Node.js/Express) - with security issues
- User Service (Node.js/PostgreSQL) - with performance issues
- Docker Compose setup for all services
- Documentation of known issues

**Key Files Created**:
- `docker-compose.yml` - Multi-service orchestration
- `services/api-gateway/` - Complete gateway service with vulnerabilities
- `services/user-service/` - User service with N+1 queries and security flaws
- `docs/ARCHITECTURE.md` - System overview with known issues
- `AGENT_GUIDE.md` - Comprehensive agent prompting guide
- `scripts/install-all.sh` and `.ps1` - Installation scripts

**To Use**:
```bash
cd challenges/01-architecture-review
./scripts/install-all.ps1  # Windows
# or
./scripts/install-all.sh   # Linux/Mac

docker-compose up -d
```

### Challenge 2: Security Audit & Remediation
**Location**: `challenges/02-security-audit/`

**Codebase**: PaySecure Fintech Application (Python Flask)
- Complete fintech app with OWASP Top 10 vulnerabilities
- Payment processing with PCI-DSS violations
- Authentication system with security flaws

**Status**: Core code structure created (expanding below)

### Challenge 3: Performance Optimization
**Location**: `challenges/03-performance-optimization/`

**Codebase**: StreamVibe Video Streaming Platform (Node.js)
- Video streaming service with performance bottlenecks
- Database query optimization challenges
- Caching implementation opportunities

**Status**: Core code structure created (expanding below)

## Quick Start for Each Challenge

### Challenge 1: Architecture Review
```powershell
cd challenges/01-architecture-review
docker-compose up -d
# Open http://localhost:3000
```

### Challenge 2: Security Audit
```powershell
cd challenges/02-security-audit
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
flask run
```

### Challenge 3: Performance Optimization
```powershell
cd challenges/03-performance-optimization
npm install
docker-compose up -d
npm run dev
```

## Prerequisites

- Docker & Docker Compose
- Node.js 18+
- Python 3.9+
- Git
- VS Code with GitHub Copilot
- 8GB RAM minimum
- 20GB free disk space

## Workshop Flow

1. **Read the Challenge README** - Understand the scenario and objectives
2. **Setup the Environment** - Get the application running
3. **Read AGENT_GUIDE.md** - Learn effective agent prompting
4. **Start Analysis** - Use agents to discover issues
5. **Implement Fixes** - Remediate critical issues
6. **Document Findings** - Create comprehensive reports
7. **Reflect** - Document lessons learned

## Support Files Included

Each challenge includes:
- `README.md` - Full challenge instructions
- `AGENT_GUIDE.md` - Agent prompting strategies
- `docs/` - System documentation
- `tests/` - Test suites
- `scripts/` - Utility scripts
- Docker files for easy setup

## What To Expect

### Time Investment
- Challenge 1: 90-120 minutes
- Challenge 2: 90-120 minutes
- Challenge 3: 90-120 minutes
- Total: 4.5 - 6 hours

### Learning Outcomes
- Master GitHub Copilot agent mode
- Multi-agent coordination
- Security vulnerability analysis
- Performance optimization techniques
- Architecture review skills
- Working with existing codebases

## Tips for Success

1. **Use Agent Mode Extensively** - Don't just use regular Copilot
2. **Create Specialized Personas** - Security expert, performance engineer, etc.
3. **Iterate and Refine** - Ask follow-up questions
4. **Validate Everything** - Test all agent suggestions
5. **Document Your Process** - Keep notes on effective prompts

## Common Issues & Solutions

### Docker Issues
- **Problem**: Ports already in use
- **Solution**: Stop other services or change ports in docker-compose.yml

### Python Environment
- **Problem**: Package installation fails
- **Solution**: Upgrade pip: `python -m pip install --upgrade pip`

### Node.js Memory
- **Problem**: Out of memory errors
- **Solution**: Increase Node memory: `export NODE_OPTIONS="--max-old-space-size=4096"`

## Next Steps

1. Start with Challenge 1 to learn multi-agent coordination
2. Move to Challenge 2 for security-focused agent work  
3. Complete Challenge 3 for performance optimization

## Getting Help

- Review the `AGENT_GUIDE.md` in each challenge
- Check `docs/` folder for system documentation
- Look at `tests/` for expected behavior
- Refer to the main workshop README

## Additional Resources

- GitHub Copilot Documentation
- OWASP Top 10
- Node.js Best Practices
- Python Security Guide
- PostgreSQL Performance Tuning

Good luck with the advanced challenges! 🚀
