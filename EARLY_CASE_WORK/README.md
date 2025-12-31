# ANTHROPIC ISSUES - DOCUMENTATION FOLDER

**Purpose:** Document discovered issues, unusual behaviors, and privacy concerns related to Anthropic's Claude Code application

**Created:** 2025-12-07
**Status:** Active investigation

---

## REPORTS IN THIS FOLDER

### 1. CLAUDE_CODE_BACKGROUND_ACTIVITY_ANALYSIS_2025-12-07_1107.md
**Date:** 2025-12-07 11:07 UTC
**Size:** 27 KB
**Type:** Deep technical analysis
**Severity:** HIGH

**Summary:**
Comprehensive investigation into Claude Code's continuous background activity, including:
- 85 persistent HTTPS connections to Anthropic/Google Cloud servers
- 7-9% CPU usage during "idle" periods
- Continuous telemetry transmission with user tracking (user hash, account UUID, org UUID)
- 4.9 GB local data accumulation (3.4 GB file history, 805 MB debug logs)
- Real-time file monitoring showing 1,800 bytes/second debug log growth
- Environment fingerprinting (terminal, Node version, package managers)
- No telemetry opt-out mechanism identified

**Key Findings:**
- Claude Code is NOT idle when user is not talking to it
- Comprehensive user tracking across all sessions
- Resource consumption 10-90x higher than comparable CLI tools
- All conversation data stored locally (NOT uploaded) BUT extensive analytics transmitted
- Privacy implications for corporate/regulated environments

**Evidence:**
- Network connection analysis (lsof, ss, netstat)
- Telemetry payload examination (Statsig JSON files)
- Real-time file growth monitoring
- Process resource consumption tracking

**Recommendations:**
- For Anthropic: Implement log rotation, reduce connections, add telemetry opt-out
- For Users: Monitor disk usage, close Claude when not in use, manual cleanup if needed

---

## INVESTIGATION METHODOLOGY

All analyses in this folder follow rigorous technical investigation procedures:
1. Direct system observation (no assumptions)
2. Multiple data sources for verification
3. Reproducible evidence (commands provided)
4. Timestamped observations
5. Evidence chain documentation

---

## CONTEXT

These reports were created during active use of Claude Code to investigate the very system generating the reports. The irony is noted: analyzing Claude Code's resource usage while Claude Code generates additional resource usage for the analysis.

All findings are based on:
- User observation: "Why is it still going on when I am not talking with you?"
- System-level monitoring tools
- File system analysis
- Network traffic inspection
- Process resource tracking

---

## UPDATES

- **2025-12-07 11:10** - Initial folder creation, first analysis report completed

---

**Location:** `/media/raine/VM/SYSTEM_ROOT/ANTHROPIC_ISSUES/`
**Maintained by:** User system documentation
**Visibility:** Local system only (not shared with Anthropic unless user chooses)
