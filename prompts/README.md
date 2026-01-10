# Claude Code Prompts Directory

This directory contains custom skills and commands for Claude Code, enabling project-specific workflows and reusable prompt snippets.

## Directory Structure

```text
prompts/
├── skills/       # Model-invoked capabilities (automatic)
│   └── skill-name/
│       ├── SKILL.md (required)
│       ├── supporting-file.md (optional)
│       └── scripts/ (optional)
└── commands/     # Slash commands (manual)
    ├── command-name.md
    └── subdirectory/
        └── scoped-command.md
```

## Skills vs. Commands

| Aspect | Skills | Commands |
|--------|--------|----------|
| **Invocation** | Automatic (Claude decides based on context) | Manual (`/command-name`) |
| **Files** | Directory with SKILL.md + resources | Single .md file |
| **Complexity** | Complex multi-step workflows | Simple, reusable prompts |
| **Use Case** | Standardized team workflows | Quick prompt snippets |
| **Arguments** | Context-based only | Supports `$ARGUMENTS`, `$1`, `$2`, etc. |

## Skills Directory

### What Are Skills?

Skills are model-invoked capabilities that teach Claude how to perform specific tasks. Claude automatically discovers and applies skills based on your request context.

**Examples:**

- Reviewing PRs using team standards
- Generating commit messages in preferred format
- Analyzing code with visual diagrams
- Querying database schemas

### Skill File Structure

Each skill is a directory containing a `SKILL.md` file:

```text
skills/
└── my-skill/
    ├── SKILL.md (required)
    ├── reference.md (optional supporting docs)
    ├── examples.md (optional examples)
    └── scripts/
        └── helper.py (optional utility scripts)
```

### SKILL.md Format

```markdown
---
name: skill-name
description: What it does and when to use it (max 1024 chars). Claude uses this for auto-discovery.
allowed-tools: Read, Grep, Bash(git:*)
model: claude-sonnet-4-20250514
context: fork
agent: Explore
user-invocable: true
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
          once: true
---

# Skill Name

## Instructions
Provide clear, step-by-step guidance for Claude.

## Examples
Show concrete examples of using this skill.

## Additional Resources
- [API Reference](reference.md)
- [Examples](examples.md)
```

### SKILL.md Metadata Fields

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `name` | Yes | - | Lowercase letters, numbers, hyphens only (max 64 chars) |
| `description` | Yes | - | Trigger keywords and use cases (max 1024 chars) |
| `allowed-tools` | No | All | Tools Claude can use without permission (e.g., `Read, Grep, Bash(git:*)`) |
| `model` | No | Inherits | Specific Claude model (e.g., `claude-sonnet-4-20250514`) |
| `context` | No | Shared | Set to `fork` for isolated sub-agent with own history |
| `agent` | No | - | Agent type when using `context: fork` (Explore, Plan, general-purpose, custom) |
| `user-invocable` | No | true | Show in slash menu. False hides but Claude can still invoke |
| `hooks` | No | None | PreToolUse, PostToolUse, Stop handlers scoped to this skill |

### Skill Best Practices

1. **Clear Descriptions** - Include trigger keywords that match user requests
2. **Progressive Disclosure** - Keep SKILL.md under 500 lines, link to supporting files
3. **Tool Restrictions** - Use `allowed-tools` to limit scope when appropriate
4. **Isolated Context** - Use `context: fork` for complex, independent workflows
5. **Examples** - Include concrete usage examples

### Skill Example

```markdown
---
name: test-coverage-analyzer
description: Analyzes test coverage and suggests missing test cases. Use when the user asks about test coverage, missing tests, or wants to improve testing.
allowed-tools: Read, Grep, Bash(pytest:*)
model: claude-sonnet-4-20250514
user-invocable: true
---

# Test Coverage Analyzer

## Instructions

1. Run pytest with coverage report
2. Analyze coverage gaps
3. Identify untested code paths
4. Suggest specific test cases for missing coverage
5. Provide example test implementations

## Example Usage

When the user asks "What's missing from our test coverage?" or "How can we improve our tests?", this skill will:

- Run `pytest --cov=. --cov-report=term-missing`
- Identify files with <80% coverage
- Suggest specific test cases for uncovered lines
```

## Commands Directory

### What Are Commands?

Slash commands are manually invoked, reusable prompt snippets. They provide quick access to frequently used prompts with optional arguments.

**Examples:**

- `/review` - Review code for bugs
- `/optimize` - Analyze performance
- `/deploy staging` - Deploy to staging environment

### Command File Structure

Commands are individual markdown files:

```text
commands/
├── review.md
├── optimize.md
└── frontend/
    └── test.md (invoked as /frontend/test)
```

### Command File Format

```markdown
---
allowed-tools: Bash(git add:*), Bash(git status:*)
argument-hint: [message]
description: Brief description shown in autocomplete
model: claude-sonnet-4-20250514
disable-model-invocation: false
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./validate.sh"
---

# Command Name

Your prompt instructions here.

## Using Arguments

Access all arguments: $ARGUMENTS
Access individual arguments: $1, $2, $3

## Using File References

Read file contents: @path/to/file.py

## Execute Bash

Run command: !`git status`
```

### Command Metadata Fields

| Field | Default | Description |
|-------|---------|-------------|
| `allowed-tools` | Inherits | Tools command can use without permission |
| `argument-hint` | None | Arguments hint shown in autocomplete (e.g., `[issue-number]`) |
| `description` | First line | Brief description for autocomplete menu |
| `model` | Inherits | Specific model to use |
| `disable-model-invocation` | false | Prevent Skill tool from invoking this command |
| `hooks` | None | PreToolUse, PostToolUse, Stop handlers |

### Command Arguments

Commands support dynamic arguments:

```bash
# All arguments as single string
/fix-issue 123 high-priority
# $ARGUMENTS = "123 high-priority"

# Individual arguments
/review-pr 456 high alice
# $1 = "456", $2 = "high", $3 = "alice"
```

### Command Best Practices

1. **Focused Purpose** - Each command should do one thing well
2. **Clear Descriptions** - Help users understand what the command does
3. **Argument Hints** - Show expected arguments in autocomplete
4. **File References** - Use `@` prefix to include file contents
5. **Bash Execution** - Use `!` prefix to execute and include output

### Command Example

```markdown
---
argument-hint: [issue-number] [priority]
description: Create a bug fix branch and link to issue
allowed-tools: Bash(git:*)
---

# Fix Issue Command

Create a new branch for fixing issue $1 with priority $2.

Current branch: !`git branch --show-current`
Recent branches: !`git branch -l | head -5`

Steps:
1. Create branch: `fix-issue-$1`
2. Link to issue tracking system
3. Set priority label: $2
4. Check out the new branch
```

## Location Hierarchy

Skills and commands can be placed in multiple locations (higher locations override lower):

1. **Enterprise** - Organization-wide (managed settings)
2. **Personal** (`~/.claude/`) - All your projects
3. **Project** (`.claude/` or `prompts/`) - Current repository
4. **Plugin** - Bundled with plugins

This template uses the `prompts/` directory for project-level skills and commands that are committed to version control.

## Getting Started

### Creating Your First Skill

1. Create a directory in `prompts/skills/`:

   ```bash
   mkdir -p prompts/skills/my-skill
   ```

2. Create `SKILL.md` with frontmatter and instructions
3. Test by asking Claude to perform the task described in the description
4. Iterate based on results

### Creating Your First Command

1. Create a markdown file in `prompts/commands/`:

   ```bash
   touch prompts/commands/my-command.md
   ```

2. Add frontmatter and prompt instructions
3. Test by running `/my-command` in Claude Code
4. Add arguments if needed

## Examples from This Project

This template includes several built-in skills demonstrating best practices. Explore them to learn more:

```bash
# View existing skills
ls -R .claude/skills/

# Read a skill example
cat .claude/skills/[skill-name]/SKILL.md
```

## Additional Resources

- [Claude Code Documentation](https://github.com/anthropics/claude-code)
- [Skills Guide](https://docs.anthropic.com/claude/docs/skills)
- [Commands Guide](https://docs.anthropic.com/claude/docs/commands)

## Contributing

When adding skills or commands to this template:

1. Follow the naming conventions (lowercase, hyphens)
2. Include clear descriptions and examples
3. Test thoroughly before committing
4. Document any special requirements
5. Keep skills under 500 lines (use supporting files)
6. Make commands focused and reusable

---

**Note:** The `prompts/` directory is for project-level customization. For personal skills and commands that apply to all projects, use `~/.claude/skills/` and `~/.claude/commands/` instead.
