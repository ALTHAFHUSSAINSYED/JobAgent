# JobPilot AI
## Autonomous Multi-Agent Recruitment Platform

Version: 1.0

---

# Vision

JobPilot AI is an autonomous multi-agent recruitment platform designed to eliminate repetitive job application tasks while maximizing interview opportunities.

The system intelligently discovers jobs, analyzes job descriptions, measures compatibility against the user's professional profile, tailors resumes and cover letters, completes applications across multiple ATS platforms, tracks every submission, learns from previous outcomes, and continuously improves future applications.

The platform combines deterministic automation with selective AI reasoning to minimize operational cost while maintaining high-quality applications.

---

# Mission

Reduce manual job application effort by more than 95% while increasing interview conversion through intelligent resume tailoring and automated application workflows.

---

# Primary Objectives

• Automatically discover relevant DevOps, Cloud, Platform Engineering, SRE, and Infrastructure jobs.

• Analyze every Job Description.

• Calculate an intelligent Job Match Score.

• Identify missing skills.

• Tailor resumes automatically.

• Generate customized cover letters.

• Complete applications automatically.

• Handle multiple ATS platforms.

• Maintain complete application history.

• Learn from previous applications.

• Operate for less than $2/month in AI inference costs.

---

# Target Users

- **Version 1:** Single User
- **Future Versions:** Multi-user SaaS Platform

---

# Core Principles

## AI Only Where Reasoning is Required

Traditional code performs:
- parsing
- browser automation
- retries
- validation
- logging
- scheduling

LLMs perform:
- semantic understanding
- resume tailoring
- cover letter generation
- ATS question answering
- job matching

---

## Human Intervention Only When Required

Everything else should be autonomous, with human intervention reserved for:
- CAPTCHA
- OTP
- MFA
- Unknown ATS questions
- Unexpected browser state

---

## Cost First

The platform should avoid unnecessary LLM calls. The default workflow should rely on deterministic software whenever possible.

---

## Modular Architecture

Every capability belongs to exactly one agent. Agents communicate through well-defined interfaces. No agent directly modifies another agent's internal logic.

---

## Security First

Credentials are encrypted. Secrets never enter Git. Resume data remains private. Sensitive data is never sent to an LLM unless absolutely required.

---

## Explainability

Every decision should be traceable. Examples:
- Why was a job skipped?
- Why was Resume B selected?
- Why was the match score 91%?
- Why was an application stopped?

Every decision must have an explanation.

---

## Adaptive Browser Automation

Instead of hardcoding selectors for each job portal, browser automation operates as an **Adaptive Browser Agent** that:
- Inspects the DOM dynamically.
- Prefers accessibility labels and semantic roles.
- Falls back to visible text and heuristics.
- Maintains a registry of portal-specific overrides only when necessary.

This design makes it easier to support LinkedIn, Workday, Greenhouse, Lever, Naukri, and future portals without rewriting the automation engine.

---

# Success Metrics

| Metric | Target |
| --- | --- |
| Applications submitted/day | 50+ |
| Average application time | <90 seconds |
| Manual effort | <5% |
| Resume tailoring | 100% |
| Cover letter generation | 100% |
| Application tracking | 100% |
| Monthly AI Cost | <$2 |
| Platform uptime | 99% |

---

# Why We're Writing This First

Every future coding agent will read this before generating code. It establishes:
- Project purpose
- Design philosophy
- AI boundaries
- Success metrics
- Non-negotiable constraints

This prevents the project from drifting as it grows.
