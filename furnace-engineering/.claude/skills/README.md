# Engineering skills used on this project

These Claude Code skills shaped how the design package was built. They load automatically when Claude Code is
started inside `furnace-engineering/`.

| Skill | Upstream (licence) | Used for |
|---|---|---|
| engineering-calc-report | BaratiLab/mechanical-engineering-skills (MIT) | Structure of `out/calc/SHV-FUR-6700-CR.html`: summary with margins first, inputs with sources, numbered assumptions, blank sign-off |
| thermal-fluids-calc | BaratiLab (MIT) | Duct, trench and pipe pressure drops (C-05, C-06, C-09) |
| design-review-package | BaratiLab (MIT) | Decision register, open items and the check summary |
| drawing-gdt-review | BaratiLab (MIT) | Title block, projection symbol and notes on the GA sheets |
| material-selection | BaratiLab (MIT) | Lining build-up comparison (all-fibre against microporous) |
| machine-element-sizing | BaratiLab (MIT) | Kettle support rib check (C-12) |
| cad-planner | gAmUssA/cadquery-skills (MIT) | One builder module per system; folders map to assemblies |
| assembly-constraints, cadquery-export | gAmUssA/cadquery-skills (MIT) | Named assembly tree, STEP and GLB export |

Only the method text (`SKILL.md` and `references/`) is vendored here. The upstream helper scripts some skills call
(`scripts/*.py`) are not included. Install them from upstream if you want them:
`npx skills add BaratiLab/mechanical-engineering-skills` and https://github.com/gAmUssA/cadquery-skills.

flowful-ai/cad-skill was also reviewed. It is PolyForm Noncommercial, so it is not used in this commercial project.
