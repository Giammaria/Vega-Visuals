# Hierarchical Gantt v2.0 (Vega v6) - README

This repo/spec contains a **hierarchical (tree) Gantt chart** built in **Vega v6**, designed to work well both:

- **Inside Power BI / Deneb** (as a custom Vega visual), and
- **Outside Power BI** (embedded on a web page with vega-embed).

The chart supports **expand/collapse**, **animated sorting (sibling-level)**, **vertical scrolling**, optional **dependency lines**, optional **bar labels**, and a handful of UX controls (toggles + slider).

## What you get (feature list)

### Hierarchy + interaction

- **Parent/child hierarchy** using id + parentId (tree structure).
- **Expand/collapse** per node (click row) with **persistent expansion state** stored in expandedNodeIds so expanding doesn’t “reset” just because the dataflow recomputed (including during sorts).
- **Expand All / Collapse All** top control buttons.

### Sorting

- **Column-header sorting** with a 3-state cycle:**ascending → descending → default/original (clears sort)**. This is driven by sortHistory → sortField + sortOrder.
- Sorting is **sibling-level** and preserves hierarchy order via a **computed “sort path”** (so children remain under parents, and preorder traversal stays valid).
- Sorting is designed to be **dynamic**: it can sort by any field present in the dataset because it accesses datum\[sortField\] and normalizes to sortKey.

### Scrolling + navigation modes

- **Vertical scrolling** when content exceeds viewport (with a vertical scrollbar whose enabled state is computed).
- **Pan & Zoom Mode toggle** (also toggled via the Space key), which changes wheel/drag semantics.

### Optional overlays

- **Dependency lines** toggle (showDependencies) and parsing of dependencyId into an array.
- **Bar labels** toggle (showBarLabels).

### Key configuration knobs

- configRow (row height, indent width, default fill).
- configInitialDepth (initial auto-expanded depth, and what “Collapse All” returns to).
- configAnimationDuration (including sort animation duration).
- configIsPowerBIVisual + sizing behavior (width/height derived differently in Power BI vs standalone).

## Quickstart

### A) Power BI + Deneb (recommended for report authors)

1.  Add a **Deneb** visual to the canvas.

2.  In the **Fields** well, provide the dataset fields the spec expects (see schema below).
3.  Choose **Vega** (not Vega-Lite).
4.  Paste the spec JSON.
5.  Make sure your date fields are typed as dates (Power BI Date/DateTime). The spec converts with toDate(datum.startDate) / toDate(datum.endDate).
6.  If you are using Deneb in Power BI, you’ll usually want the signal, **configIsPowerBIVisual**, to reflect that environment so width/height come from containerSize()-style logic rather than fixed numbers.

> **Tip:** Deneb users will most commonly customize **columns** and **tooltips** by editing the last two datasets: column-data and gantt-item-tooltip-data (details below).

### B) Standalone web page (Vega Embed)

If you want to share this outside Power BI, the typical pattern is: host a JSON spec + data, then embed.

Example (minimal) HTML (URLs shown in code so you can replace as needed):

```
<div id="vis"></div>
<script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
<script>
  vegaEmbed('#vis', 'PATH_TO_SPEC.json', { actions: true });
</script>
```

For standalone usage, fixed sizing is controlled by configDesiredWidth and configDesiredGanttHeight (unless you change the sizing logic).

## Data requirements

### Required fields (core)

Your main dataset is named **dataset** and is parsed with:

> <small>\* indicates field is required</small>

- \* id _(number)_ — unique node id
- \* parentId _(number | null)_ — parent node id (only 1 null parentId should exist for the root).
- \* name _(string)_ — display name for the task row
- \* startDate _(date)_
- \* endDate _(date)_
- ‎ ‎ decimalPercentComplete _(number)_ — e.g. 0.35 for 35%
- ‎ ‎ dependencyId _(string)_ — optional comma-separated ids
- ‎ ‎ color _(string)_ — optional, falls back to configRow.defaultFill

These field names are case-sensitive.

### Dependencies (optional)

If you provide dependencyId, it can contain a comma-separated list (spaces are stripped) which is converted into an array dependencies.

Example values:

- "dependencyId": "12"
- "dependencyId": "12,15,19"
- "dependencyId": null or "null" (treated as no dependencies)

## The two main “authoring” surfaces

Most report authors won’t need to touch the transforms or marks. They’ll edit the **values** array of these two datasets at the end of the data array:

### 1) Add / remove / configure **columns** (column-data)

This dataset defines **what columns exist**, how wide they’re allowed to be, alignment, formatting, etc.

Each column entry looks like:

- name: internal column name
- field: the dataset field to display/sort by (must exist on the row datum)
- type: "text" | "date" | "percentage" (used to format values)
- format: formatting string (date format for timeFormat, or numeric format for format)
- label: header label shown to users
- align: "left" | "center" | "right"
- allowableWidth: width budget for the column
- alwaysShow: whether it shows even when “Show Detail Columns” is off
- boldValue: whether values render bold

Example addition:

```
{
  "name": "owner",
  "field": "owner",
  "type": "text",
  "format": null,
  "label": "Owner",
  "align": "left",
  "allowableWidth": 120,
  "alwaysShow": false,
  "boldValue": false
}
```

✅ **Sorting note:** because sorting reads datum\['sortField'\] and normalizes into sortKey, adding a column that points to any real field automatically becomes sortable via the column header click logic.

### 2) Add / remove / configure **tooltips** (gantt-item-tooltip-data)

This dataset defines which fields appear when hovering a Gantt row/bar, and how they’re labeled and formatted.

Entries include:

- field: dataset field to show
- label: tooltip label
- type: "text" | "date"
- format: date format or numeric format

Example addition:

```
{ "field": "owner", "label": "Owner", "type": "text", "format": null }
```

Under the hood, tooltip generation:

- filters to the currently hovered node (mouseoverNodeDatum)
- looks up the matching row in dataset
- computes value from mouseoverNodeDatum\[\<field\>\] or the dataset value
- formats with timeFormat() for dates (or format() for numeric/text formatting)
- pivots into an object for the tooltip renderer

## Configuration guide (what authors commonly tweak)

### Layout + sizing

- configDesiredWidth (standalone width target)
- configDesiredGanttHeight (standalone height target)
- configIsPowerBIVisual + the computed width/height logic (Power BI vs non-PBI behavior).

### Row rendering

- configRow.rowHeight (density)
- configRow.levelIndentWidth (tree indent)
- configInitialDepth (initially expanded depth)
- configIncludeRoot (whether to show the synthetic/root)

### Animation timing

- configAnimationDuration.sort controls sort animation length (and other durations live here too).

## How sorting works (mental model)

When a user clicks a column header:

1.  sortHistory updates, storing the clicked field name and cycling state.
2.  sortField and sortOrder derive from that history.
3.  In dataset-formatted:

    - \sortRaw = datum\['sortField'\]
    - sortKey converts values into a comparable type:

      - dates → numeric timestamp
      - numbers → number
      - everything else → lowercase string

    - siblingRank is computed **within each parentId** (sibling-only sort) via a window transform.

4.  In dataset-formatted-sorted:

    - sortPath is built from ancestor \siblingRankPad values
    - final sort index is assigned by sorting sortPath (preorder traversal that respects the sibling ordering).

This is what keeps **children under their parent** while still letting you “sort by Progress” (or any other column) at the sibling level.

## Performance tips for large hierarchies (author-friendly)

Even with lazy row rendering, large trees can get expensive. A few practical knobs you can turn without becoming a Vega expert:

- **Increase rowHeight** (configRow.rowHeight) if you don’t need a dense view (fewer visible marks in viewport).
- Keep your default view shallow: set configInitialDepth to 1 (or 2) so it doesn’t render thousands of nodes initially.
- If you don’t need them:

  - disable dependencies (configShowDependencies.enabled = false)
  - disable bar labels (configShowBarLabels.enabled = false)
  - remove unnecessary detail columns (via the values array in the column-dataset)

## Troubleshooting

### “My dates look shifted / wrong day”

If your input dates are already real date objects or timestamps, the spec’s approach of converting using:

- toDate(datum.startDate)
- toDate(datum.endDate)

is the right direction (it avoids formatting-to-string-then-parsing, which can introduce timezone shifts).

### “Sorting doesn’t work on my new column”

Check:

- Your new field exists on the row datum.
- Values are consistently typed (all numbers, all dates, or all strings). Sorting normalizes via sortKey and treats invalid values as nulls.

### “Expanded nodes collapse when I sort”

Expansion state is intended to persist via expandedNodeIds (string ids). If you customize hierarchy transforms, be careful not to accidentally re-key ids or change id types.

## Where to edit things (fast reference)

- **Change sizing / row height / animation durations:** top-level signals (configDesiredWidth, configDesiredGanttHeight, configRow, configAnimationDuration, etc.).
- **Change what columns appear:** data\[\] → **column-data** → values[].
- **Change tooltip contents:** data\[\] → **gantt-item-tooltip-data** → values[].

## Dev Info

- Author: Madison Giammaria
- GitHub: [Vega-Visuals](https://github.com/Giammaria/Vega-Visuals)
- LinkedIn: [Profile](https://www.linkedin.com/in/madison-giammaria-58463b33/)
