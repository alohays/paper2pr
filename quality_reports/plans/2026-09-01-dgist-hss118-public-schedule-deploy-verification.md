# DGIST HSS118 Public Schedule Deployment Verification Plan

## Objective

Confirm that only the necessary student-facing schedule and material labels changed for the November 20 hardware session, integrate the verified W02 roadmap into the publishable Paper2PR history, and validate both deployed websites end to end.

## Steps

1. Compare the live course page, the Paper2PR series source, generated semester maps, and the W02 roadmap against the accepted working schedule.
2. Remove or shorten any public wording that goes beyond schedule and material guidance while preserving the robot-learning-first sequence and the late hardware special-module framing.
3. Reconcile `w02-authoring` with current `main` without staging unrelated TTA or historical-plan work.
4. Run the series suite, W02 render and quality gate, note/language checks, the public-site strict build, and focused visual or HTML checks.
5. Commit and push the intended changes, wait for GitHub Actions, and verify the production URLs rather than assuming deployment completed.

## Acceptance Criteria

- September 18 is a DGIST leadership talk, November 13 remains a leadership talk, and November 20 is the hardware lecture everywhere students can see the schedule.
- The public page keeps the official lecture title and a concise `Special module` label.
- The W02 roadmap presents robot learning first and hardware/control/mechanics as the late physical-stack synthesis.
- Paper2PR and the teaching site build successfully, their deployment workflows pass, and unrelated working-tree changes remain untouched.
