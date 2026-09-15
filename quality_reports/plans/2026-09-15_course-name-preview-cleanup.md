# Course Name and Link Preview Cleanup

## Objective

Remove obsolete DGIST HSS118 course naming from current public pages and link-preview metadata, and prevent the old name from being regenerated.

## Plan

1. Audit the website, Paper2PR sources and rendered output, page metadata, search indexes, preview assets, and current course records for obsolete names.
2. Identify the origin of the reported preview text and distinguish source problems from third-party cached previews.
3. Correct current titles, descriptions, metadata, and generation templates in isolated publishable changes while preserving unrelated work.
4. Build the affected sites, verify rendered metadata and current naming, run relevant existing checks, and add a focused regression check if metadata generation needs a code change.
5. Publish verified fixes, inspect production HTML with browser and social-crawler user agents, and refresh the reported preview cache where the available tools allow it.

## Naming

- Term theme: Physical AI for Everyone.
- Official course name: Seminar for Comprehensive Competency Cultivation (SCCC).
- Course identifier: DGIST HSS118, Fall 2026.

## Acceptance Criteria

- Current public-facing course content and metadata use the accepted names.
- Social preview titles and descriptions are explicit and consistent with the visible page.
- Rebuilt output and production responses contain no obsolete course name in displayed text or preview metadata.
- Existing links, slides, recordings, and unrelated local work continue to function.
- Any remaining third-party cached preview is identified precisely, with a practical refresh route.

Historical reports remain historical records. Existing internal path slugs are not renamed merely because they contain the former name; their role in public output is audited separately.
