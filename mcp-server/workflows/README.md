# QGIS AI Bridge - Workflow Library

**Purpose:** Token-efficient workflow documentation for common QGIS and OilFlow2D operations.

**Token Budget:** ~250-300 tokens per workflow (vs 2000+ tokens for discovery each conversation)

## Available Workflows

### OilFlow2D Workflows
- ⬜ `oilflow2d_new_project.md` - Create new OilFlow2D project
- ⬜ `oilflow2d_add_boundary.md` - Add boundary shapefile to project
- ⬜ `oilflow2d_configure_simulation.md` - Configure simulation parameters
- ⬜ `oilflow2d_run_simulation.md` - Execute simulation run
- ⬜ `oilflow2d_export_results.md` - Export simulation results

### General QGIS Workflows
- ⬜ `qgis_load_shapefile.md` - Load vector shapefile into project
- ⬜ `qgis_load_raster.md` - Load raster data into project
- ⬜ `qgis_set_project_crs.md` - Set project coordinate system

## How to Use

### For AI Agents
1. Check available workflows: `qgis_control({"command": "workflow.list"})`
2. Get workflow: `qgis_control({"command": "workflow.get", "params": {"workflow_name": "oilflow2d_new_project"}})`
3. Follow step-by-step instructions
4. Each step has exact command, params, and expected results

### For Recording New Workflows
1. Plan the workflow (what task to accomplish)
2. Start recording: `qgis_control({"command": "workflow.record_start", "params": {"workflow_name": "my_workflow"}})`
3. Execute the workflow in QGIS
4. Add notes: `qgis_control({"command": "workflow.add_note", "params": {"note": "This sets the CRS"}})`
5. Stop recording: `qgis_control({"command": "workflow.record_stop"})`
6. Review and edit the generated markdown file
7. Test by having AI follow the workflow
8. Commit to git

## Workflow Document Format

Each workflow follows this structure:

```markdown
# Workflow: <Name>

**Purpose:** Brief description
**Prerequisites:** What must be true before starting
**Estimated time:** How long it takes
**Recorded:** Date

## Steps

### 1. Step Name
- **Command:** qgis.command_name
- **Params:** {"param": "value"}
- **Wait:** 0.5s
- **Expected:** What should happen
- **Note:** Why this matters (optional)

### 2. Next Step
...

## Troubleshooting
- Common issues and solutions

## Variables
- <user_provided> = Values that change each time
```

## Standards

**DO:**
- ✅ Record complete end-to-end workflows
- ✅ Include wait times (prevents race conditions)
- ✅ Add verification steps (widget.wait_for)
- ✅ Document prerequisites and expected outcomes
- ✅ Use variables for user-provided values
- ✅ Include troubleshooting section

**DON'T:**
- ❌ Record exploratory clicking (clean before saving)
- ❌ Skip wait times
- ❌ Hardcode paths or user-specific values
- ❌ Assume widgets are visible without wait_for
- ❌ Skip error handling

## Token Efficiency

**Command Reference (qgis_mcp_skills.md):**
- ~200 tokens
- Lists all available commands

**Workflow Library (this directory):**
- ~250 tokens per workflow
- 5 OilFlow2D workflows = ~1250 tokens

**Total:** ~1500 tokens for complete OilFlow2D automation knowledge

**vs Discovery Each Time:** 10,000+ tokens wasted per conversation

## Status

**Phase A: Build Recording System**
- ⬜ workflow.record_start
- ⬜ workflow.record_stop
- ⬜ workflow.add_note
- ⬜ workflow.list
- ⬜ workflow.get

**Phase B: Record OilFlow2D Workflows**
- 0/5 workflows recorded

**Last Updated:** 2026-01-29
