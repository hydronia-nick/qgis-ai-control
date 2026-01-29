# QGIS AI Bridge - TODO List

**Last Updated:** 2026-01-29
**Current Phase:** Phase A.2 - Record OilFlow2D Workflows
**Current Command Count:** 28/~65 target

---

## ✅ COMPLETED: Phase A.1 - Workflow Recording System (2026-01-29)

All 5 workflow recording commands implemented and tested:

- [x] **workflow.record_start** - Begin capturing Qt events ✅
  - Captures: clicks, keyboard, dialogs, dropdown selections, focus
  - Filters noise (only significant events)
  - Auto-logs widget properties (objectName, class, text, window title, parent)
  - Stores with timestamps and elapsed time

- [x] **workflow.record_stop** - Stop recording and generate workflow doc ✅
  - Stops event capture
  - Generates structured markdown in `mcp-server/workflows/<name>.md`
  - Generates raw JSON for debugging
  - Returns summary (step count, duration, file paths)

- [x] **workflow.add_note** - Add manual annotations during recording ✅
  - User calls this to add context
  - Inserts note at current timestamp
  - Explains WHY a step matters

- [x] **workflow.list** - List all saved workflows ✅
  - Scans `mcp-server/workflows/` directory
  - Returns workflow names, purposes, recorded dates

- [x] **workflow.get** - Retrieve specific workflow ✅
  - Reads workflow markdown file
  - Returns formatted workflow for AI to follow
  - Includes all steps, params, timing

**Test Results:**
- Recorded test_workflow with 12 events over 11 seconds
- Generated markdown + JSON successfully
- All commands tested via curl and working

---

## 🎯 Current Priority: Phase A.2 - Record OilFlow2D Workflows

### Phase A.2: Record OilFlow2D Workflows (5 workflows)

- [ ] 🎥 **Record: oilflow2d_new_project.md**
  - Create new OilFlow2D project
  - Capture: menu action name, dialog objectNames, form fields
  - Document: CRS selection, output directory, project name

- [ ] 🎥 **Record: oilflow2d_add_boundary.md**
  - Add boundary shapefile to project
  - Capture: file dialog, layer loading, styling

- [ ] 🎥 **Record: oilflow2d_configure_simulation.md**
  - Configure simulation parameters
  - Capture: parameter dialogs, settings, validation

- [ ] 🎥 **Record: oilflow2d_run_simulation.md**
  - Execute simulation
  - Capture: start button, progress indicators, completion detection

- [ ] 🎥 **Record: oilflow2d_export_results.md**
  - Export simulation results
  - Capture: export dialog, file formats, output paths

### Phase A.3: Implement Missing Commands (As Discovered)

**Note:** These will be discovered during workflow recording. Implement only what's actually needed.

**Expected commands based on workflows:**
- [ ] **layer.add** - Load vector/raster layers (likely needed)
- [ ] **project.save** - Save project file (likely needed)
- [ ] **project.new** - Create blank project (if not using OilFlow2D's new project)
- [ ] **plugin.list** - Check if OilFlow2D is enabled (useful for troubleshooting)
- [ ] **plugin.enable** - Enable plugin if disabled (nice to have)

### Phase A.4: Test Full Automation

- [ ] **Test: AI follows oilflow2d_new_project.md autonomously**
  - Start with QGIS running
  - AI reads workflow and executes each step
  - No manual intervention
  - Document any failures or gaps

- [ ] **Test: Full OilFlow2D workflow end-to-end**
  - New project → Add boundary → Configure → Run → Export
  - Chain all 5 workflows together
  - Verify complete autonomous operation

- [ ] **Document gaps and iterate**
  - What commands are still missing?
  - What wait times need adjustment?
  - What error handling is needed?

---

## 🔧 Phase B: Complete OilFlow2D Critical Commands

**Start after Phase A.4 is validated**

- [ ] Implement commands discovered in Phase A.3
- [ ] Test each command via workflow execution
- [ ] Update workflow docs if commands change behavior
- [ ] Verify all 5 OilFlow2D workflows work reliably

---

## 📋 Phase C: Generalize to Standard GIS Operations

**Start after OilFlow2D proof of concept is complete**

### Layer Management (5-6 remaining)
- [x] layer.list ✅ DONE
- [ ] layer.add (may be done in Phase B)
- [ ] layer.remove
- [ ] layer.set_active
- [ ] layer.set_visible
- [ ] layer.reorder
- [ ] layer.get_info

### Project Operations (6-7 commands)
- [ ] project.new (may be done in Phase B)
- [ ] project.open
- [ ] project.save (may be done in Phase B)
- [ ] project.save_as
- [ ] project.get_info
- [ ] project.set_crs
- [ ] project.close

### Canvas Control (5-6 commands)
- [ ] canvas.zoom_full
- [ ] canvas.zoom_to_layer
- [ ] canvas.zoom_to_extent
- [ ] canvas.pan
- [ ] canvas.refresh
- [ ] canvas.get_extent

---

## 🚀 Phase D: Data Processing

**Start after Phase C complete**

### Processing Algorithms (3-4 commands)
- [ ] processing.list_algorithms
- [ ] processing.get_params
- [ ] processing.run
- [ ] processing.get_result

### Feature/Attribute Operations (3-4 commands)
- [ ] features.select_by_expression
- [ ] features.get_selected
- [ ] features.get_attributes
- [ ] attributes.update_field

---

## 📊 Phase E: Output/Export

**Start after Phase D complete**

- [ ] export.to_shapefile
- [ ] export.to_geojson
- [ ] export.to_csv

---

## 🐛 Known Issues to Address

- [ ] **qgis.restart_api can crash QGIS**
  - Workaround: Use qgis.kill_process + qgis.launch
  - Consider: Fixing the restart logic or removing command

- [ ] **Need test projects with sample data**
  - Create sample shapefiles for testing
  - Document test data locations
  - Include in repository or document where to get them

- [ ] **Dialog visibility unconfirmed**
  - Some dialogs may not appear after trigger()
  - Need better verification methods
  - May need widget.wait_for improvements

---

## 📚 Documentation TODOs

- [ ] Update qgis_mcp_skills.md after each command added
- [ ] Keep IMPLEMENTATION_GUIDE.md current with progress
- [ ] Update workflow README.md as workflows are recorded
- [ ] Create user guide for workflow recording
- [ ] Document common troubleshooting patterns

---

## 🎯 Success Metrics

### Phase A Complete When:
- ✅ All 5 workflow.* commands implemented and tested
- ✅ All 5 OilFlow2D workflows recorded and documented
- ✅ AI can follow at least 1 OilFlow2D workflow autonomously
- ✅ End-to-end OilFlow2D automation validated

### Phase B Complete When:
- ✅ All commands discovered in workflows implemented
- ✅ All 5 OilFlow2D workflows work reliably
- ✅ No manual intervention needed for standard OilFlow2D operations

### Phase C-E Complete When:
- ✅ 50+ commands total
- ✅ Complete GIS workflow automation
- ✅ General QGIS operations fully supported

---

## 💡 Ideas for Future Phases

- [ ] Styling commands (symbology, labels, colors)
- [ ] Layout/print composer commands
- [ ] Plugin management (list, enable, disable, install)
- [ ] Server operations (for QGIS Server)
- [ ] 3D view control
- [ ] Temporal controller (time series)
- [ ] Expression builder/validator
- [ ] Field calculator operations

---

**Next Action:** Implement workflow.record_start command
