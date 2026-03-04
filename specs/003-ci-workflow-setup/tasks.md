# Tasks: CI Workflow Integration Guide for Anodyse Users

**Input**: Specification, plan, research, data-model, and contracts from `/specs/003-ci-workflow-setup/`  
**Prerequisites**: spec.md ✅, plan.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅  
**Output Target**: Integration guides and example workflows for end users

**Organization**: Tasks grouped by user story (US1-US3) enabling independent implementation and testing.

---

## Phase 0: Project Setup & Infrastructure

**Purpose**: Foundation and shared resources for all user stories

- [ ] T001 Create documentation directory structure in `docs/ci-integration/`
- [ ] T002 Create example workflows directory `docs/examples/workflows/`
- [ ] T003 Create templates directory `docs/examples/templates/` (for custom template examples)
- [ ] T004 Set up GitHub repository for dogfooding: Create `.github/workflows/` directory
- [ ] T005 Set up GitLab pipeline placeholder (if testing on GitLab instance)
- [ ] T006 Create contribution guide for CI integration examples in `docs/CI_EXAMPLES_CONTRIBUTING.md`

---

## Phase 1: Foundational Documentation (Blocking Prerequisites)

**Purpose**: Documentation that all user stories depend on

- [ ] T010 Create main CI integration guide: `docs/CI_INTEGRATION.md` covering overview, platform selection, and cross-platform concepts
- [ ] T011 [P] Create GitHub Actions introduction section in `docs/CI_INTEGRATION.md#github-actions` with platform overview
- [ ] T012 [P] Create GitLab CI introduction section in `docs/CI_INTEGRATION.md#gitlab-ci` with platform overview
- [ ] T013 [P] Create generic CI patterns introduction in `docs/CI_INTEGRATION.md#generic-ci` with common patterns
- [ ] T014 Create publishing guide: `docs/PUBLISHING.md` covering GitHub Pages, GitLab Pages, Read the Docs, and static hosting
- [ ] T015 Create troubleshooting guide: `docs/TROUBLESHOOTING.md` with common errors and solutions
- [ ] T016 Create environment variable reference: `docs/ENVIRONMENT_VARIABLES.md` documenting all ANODYSE_* variables
- [ ] T017 Finalize and validate quickstart guide: `specs/003-ci-workflow-setup/quickstart.md`

---

## Phase 2: User Story 1 - GitHub Actions Integration Guide (Priority: P1)

**Story Goal**: Provide end users with complete GitHub Actions integration for automated documentation generation

**Independent Test**: Copy-paste GitHub Actions workflow generates docs on push, PR, and schedule; artifacts available and GitHub Pages optional

**Acceptance Criteria**:
1. User has GitHub repository with Ansible code
2. User copies example workflow file to `.github/workflows/`
3. User updates environment variables for their paths
4. Documentation auto-generates on push, PR, and scheduled triggers
5. Generated docs available as artifacts
6. (Optional) Docs published to GitHub Pages without additional setup

### US1 Tasks: GitHub Actions Setup & Documentation

- [ ] T101 [P] [US1] Create GitHub Actions reference contract: `docs/github-actions-reference.md` with schema and customization examples
- [ ] T102 [P] [US1] Create GitHub Actions basic workflow example: `docs/examples/workflows/github-actions-basic.yml`
  - Inputs: default paths (./playbooks, ./docs)
  - Triggers: push to main, PR to main, manual
  - Output: artifact upload
- [ ] T103 [P] [US1] Create GitHub Actions advanced workflow with GitHub Pages: `docs/examples/workflows/github-actions-with-github-pages.yml`
  - Includes basic workflow functionality
  - Adds GitHub Pages deployment on push to main
  - Demonstrates conditional deployment
- [ ] T104 [P] [US1] Create GitHub Actions all-triggers workflow: `docs/examples/workflows/github-actions-all-triggers.yml`
  - Push, PR, schedule, manual triggers
  - Shows how to enable/disable each trigger
- [ ] T105 [US1] Create GitHub Actions section in `docs/CI_INTEGRATION.md`:
  - Installation steps (3 steps)
  - Configuration walkthrough (env vars, paths, triggers)
  - Step-by-step copy-paste guide
  - Common customizations (branches, artifacts, templates)
  - Troubleshooting (7+ common issues specific to GitHub Actions)
- [ ] T106 [P] [US1] Create GitHub Actions template customization example: `docs/examples/github-actions-custom-templates.yml`
  - Show how to reference custom template directory
  - Show how to clone external templates
- [ ] T107 [US1] Test GitHub Actions workflow locally with act or in GitHub repository
  - Verify workflow runs on push
  - Verify artifacts generated correctly
  - Verify workflow runs on PR (no publish)
  - Verify scheduled run creates artifacts
- [ ] T108 [US1] Create GitHub Actions FAQ section in troubleshooting: `docs/TROUBLESHOOTING.md#github-actions`
  - Workflow not triggering
  - Artifacts not found
  - GitHub Pages deployment failing
  - Permission errors

### US1 Tasks: Integration & Documentation

- [ ] T109 [US1] Update main documentation index to link to GitHub Actions guide
- [ ] T110 [US1] Add GitHub Actions setup to quickstart guide validation checklist
- [ ] T111 [US1] Create GitHub Actions video walkthrough transcript (optional): `docs/GITHUB_ACTIONS_WALKTHROUGH.md`

---

## Phase 3: User Story 2 - GitLab CI/CD Integration Guide (Priority: P2)

**Story Goal**: Provide GitLab users with equivalent CI/CD integration for automated documentation generation

**Independent Test**: Copy-paste GitLab configuration generates docs on push, MR, and schedule; artifacts available and GitLab Pages optional

**Acceptance Criteria**:
1. User has GitLab project with Ansible code and runner available
2. User copies example `.gitlab-ci.yml` or adds to existing config
3. User updates variables for their paths
4. Documentation auto-generates on push, MR, and scheduled triggers
5. Generated docs available in job artifacts
6. (Optional) Docs published to GitLab Pages without additional setup

### US2 Tasks: GitLab CI/CD Setup & Documentation

- [ ] T201 [P] [US2] Create GitLab CI reference contract: `docs/gitlab-ci-reference.md` with schema, runner options, and customization examples
- [ ] T202 [P] [US2] Create GitLab CI basic configuration example: `docs/examples/gitlab-ci-basic.yml`
  - Uses Docker runner (python:3.11-slim)
  - Inputs: default paths via variables
  - Triggers: push, MR, manual
  - Output: artifacts with 30-day retention
- [ ] T203 [P] [US2] Create GitLab CI advanced configuration with GitLab Pages: `docs/examples/gitlab-ci-with-gitlab-pages.yml`
  - Includes basic CI job
  - Adds pages: job for publishing docs
  - Shows artifact path → Pages host mapping
- [ ] T204 [P] [US2] Create GitLab CI all-triggers configuration: `docs/examples/gitlab-ci-all-triggers.yml`
  - Push, MR, schedule, manual triggers via rules
  - Shows how to enable/disable each trigger
- [ ] T205 [P] [US2] Create GitLab CI shell runner alternative: `docs/examples/gitlab-ci-shell-runner.yml`
  - For self-hosted runners without Docker
  - Shows venv setup for self-hosted environments
- [ ] T206 [US2] Create GitLab CI section in `docs/CI_INTEGRATION.md`:
  - Runner setup (Docker vs. shell)
  - Configuration walkthrough (variables, stages, rules)
  - Step-by-step copy-paste guide
  - Common customizations (branches, versions, templates, retention)
  - Troubleshooting (7+ common issues specific to GitLab CI)
- [ ] T207 [P] [US2] Create GitLab CI template customization example: `docs/examples/gitlab-ci-custom-templates.yml`
  - Show how to reference repository templates
  - Show how to clone external templates via before_script
- [ ] T208 [US2] Test GitLab CI configuration on GitLab project or instance
  - Verify pipeline triggers on push
  - Verify artifacts stored correctly
  - Verify MR pipeline runs (no publish)
  - Verify scheduled pipeline
- [ ] T209 [US2] Create GitLab CI FAQ section in troubleshooting: `docs/TROUBLESHOOTING.md#gitlab-cicd`
  - Pipeline not triggering
  - Docker runner not available
  - Artifacts not stored
  - GitLab Pages deployment failing
  - Variable scoping issues

### US2 Tasks: Integration & Documentation

- [ ] T210 [US2] Update main documentation index to link to GitLab CI guide
- [ ] T211 [US2] Add GitLab CI setup to quickstart guide validation checklist
- [ ] T212 [US2] Create feature parity matrix: `docs/PLATFORM_COMPARISON.md` comparing GitHub Actions vs. GitLab CI capabilities and usage

---

## Phase 4: User Story 3 - Generic CI/CD Integration Guide (Priority: P3)

**Story Goal**: Enable organizations with custom/enterprise CI systems to adapt Anodyse integration to their platform

**Independent Test**: Documentation clearly explains CLI patterns and integration concepts; validated by implementing in at least one additional CI system (Jenkins or Woodpecker example)

**Acceptance Criteria**:
1. End user reads generic CI documentation
2. User understands core anodyse CLI patterns and integration concepts
3. User can adapt GitHub/GitLab examples to their CI system
4. User successfully implements anodyse in their custom CI system
5. Documentation includes examples for Jenkins, Woodpecker, and CircleCI at minimum

### US3 Tasks: Generic CI/CD Documentation & Examples

- [ ] T301 [P] [US3] Create generic CI guide section in `docs/CI_INTEGRATION.md#generic-ci`:
  - CLI pattern overview
  - Environment variable conventions
  - Exit code semantics
  - Artifact storage abstraction
  - Template mounting patterns
  - Error handling strategies

- [ ] T302 [P] [US3] Create Jenkins integration example: `docs/examples/Jenkins/Jenkinsfile` (Declarative Pipeline)
  - Show pipeline structure with stages
  - Setup Python venv
  - Invoke anodyse
  - Archive artifacts
  - Error handling

- [ ] T303 [P] [US3] Create Woodpecker CI example: `docs/examples/woodpecker/.woodpecker.yml`
  - Show pipeline structure
  - Docker image setup
  - Anodyse invocation
  - Artifact handling
  - Multi-trigger support

- [ ] T304 [P] [US3] Create CircleCI example: `docs/examples/circleci/config.yml`
  - Show job structure
  - Docker image setup
  - Anodyse invocation
  - Artifact storage
  - Workflows and triggers

- [ ] T305 [P] [US3] Create Travis CI example: `docs/examples/travis/.travis.yml`
  - Show build structure
  - Python setup
  - Anodyse invocation
  - Deploy configuration

- [ ] T306 [P] [US3] Create generic shell script pattern: `docs/examples/scripts/generate-docs.sh`
  - Portable across all CI systems
  - Environment variable handling
  - Error checking
  - Artifact staging

- [ ] T307 [US3] Create generic CI integration guide: `docs/GENERIC_CI_INTEGRATION.md`
  - When to use generic pattern vs. platform-specific
  - CLI patterns and best practices
  - Troubleshooting for custom CI systems
  - Extending integration to other platforms

- [ ] T308 [US3] Create CI platform comparison matrix: `docs/CI_PLATFORM_SUPPORT.md`
  - Supported platforms (P1: GitHub, GitLab; P3: Others)
  - Feature comparison (Docker support, secrets management, artifact handling)
  - Migration guide (how to adapt from one platform to another)

- [ ] T309 [US3] Test generic patterns with Jenkins Declarative Pipeline
  - Verify Jenkinsfile runs successfully
  - Document any environment-specific gotchas

- [ ] T310 [US3] Test generic patterns with Woodpecker CI
  - Verify .woodpecker.yml runs successfully
  - Document runner configuration requirements

- [ ] T311 [US3] Create generic CI troubleshooting section: `docs/TROUBLESHOOTING.md#generic-ci`
  - Environment setup issues
  - Python/pip problems
  - Artifact staging failures
  - Template mounting issues

### US3 Tasks: Community & Extensibility

- [ ] T312 [US3] Create platform request template: `docs/PLATFORM_REQUEST_TEMPLATE.md`
  - For users to request new CI platform examples
  - Template for submitting contributions

- [ ] T313 [US3] Create CI integration contribution guide: `docs/CONTRIBUTING_CI_EXAMPLES.md`
  - How to add new platform examples
  - Testing requirements
  - Documentation standards
  - Pull request process

---

## Phase 5: Anodyse Repository Dogfooding

**Purpose**: Demonstrate feature by implementing in anodyse repository using sample playbooks

- [ ] T401 [P] Create GitHub Actions workflow for anodyse repository: `.github/workflows/docs-on-push.yml`
  - Runs on push to main
  - Processes samples/
  - Publishes to GitHub Pages at /docs/samples/
  - Uses repository example templates

- [ ] T402 [P] Create GitHub Actions workflow for PR validation: `.github/workflows/docs-on-pr.yml`
  - Runs on PR to main
  - Validates docs can be generated
  - Reports status in PR

- [ ] T403 [P] Create GitHub Actions workflow for scheduled regeneration: `.github/workflows/docs-schedule.yml`
  - Runs weekly Monday 2 AM
  - Regenerates all sample docs
  - Updates repository

- [ ] T404 Create sample documentation README: `samples/README-DOCS.md`
  - Explains what sample docs are
  - Links to generated output
  - Shows CI workflow examples

- [ ] T405 Update main README: `README.md`
  - Add link to CI integration guide
  - Add badge/link to sample automated docs
  - Reference dogfood examples

- [ ] T406 Create anodyse repository CI/CD status page: `docs/ANODYSE_CI_DOGFOOD.md`
  - Shows how anodyse uses this feature
  - Links to CI workflows
  - Links to generated sample docs
  - Status of automation

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Overall quality, validation, and user experience

### Documentation Quality

- [ ] T501 Review all guides for consistency in:
  - Terminology (workflow vs. pipeline, job vs. stage)
  - Code formatting (YAML indentation, shell script style)
  - Cross-platform examples parity
  - File paths and assumptions

- [ ] T502 Create documentation index: `docs/CI_INTEGRATION_INDEX.md`
  - Navigation guide to all CI docs
  - Quick links by platform
  - FAQ index
  - Troubleshooting quick reference

- [ ] T503 [P] Create glossary: `docs/CI_GLOSSARY.md`
  - Define CI/CD, workflow, pipeline, job, stage, trigger, artifact, secret
  - Platform-specific terminology
  - Anodyse-specific terms

- [ ] T504 [P] Create checklists for setup verification: `docs/SETUP_CHECKLISTS.md`
  - GitHub Actions setup checklist (7 items)
  - GitLab CI setup checklist (8 items)
  - Generic CI setup checklist (6 items)

- [ ] T505 Create configuration reference: `docs/CONFIGURATION_REFERENCE.md`
  - All environment variables documented
  - Default values
  - Supported options per platform

### Testing & Validation

- [ ] T601 Validate all example workflows (GitHub, GitLab) can be copied and run without modification
  - Test with sample playbooks
  - Confirm artifacts generated
  - Verify no errors in logs

- [ ] T602 Validate all shell scripts run on multiple OS (Linux, macOS, Windows WSL)
  - Verify portability
  - Document any platform-specific steps

- [ ] T603 [P] Validate all code blocks in documentation are current and accurate
  - YAML syntax validation
  - Shell script syntax check
  - File paths exist

- [ ] T604 [P] Validate all cross-references and links in documentation
  - Internal links (docs → docs)
  - External links (GitHub, GitLab, etc.)
  - Line anchors (#sections)

- [ ] T605 Perform user acceptance test (UAT): Have non-Anodyse developer follow each guide
  - GitHub Actions guide (30 minutes)
  - GitLab CI guide (30 minutes)
  - Generic pattern guide (45 minutes)
  - Document clarity issues and update docs

- [ ] T606 Test error scenarios and validate error messages
  - Missing input directory
  - Invalid YAML in playbooks
  - Timeout scenarios
  - Permission denied errors

### Release & Documentation

- [ ] T701 Create CHANGELOG entry: `CHANGELOG.md` entry for CI integration feature
  - New documentation
  - Example workflows
  - Supported platforms

- [ ] T702 Create feature announcement: `docs/CI_INTEGRATION_RELEASE_NOTES.md`
  - What's new
  - Quick start links
  - Known limitations
  - Feedback request

- [ ] T703 Create migration guide for existing users: `docs/ADDING_CI_TO_EXISTING_PROJECTS.md`
  - How to add CI to already-existing projects
  - Integration with existing CI workflows
  - Updating paths and configuration

- [ ] T704 [P] Create example repository templates (to share as starter packs): `docs/STARTER_TEMPLATES.md`
  - Link to GitHub template repo
  - Link to GitLab template repo
  - How to use templates

- [ ] T705 Update project documentation home to reference CI integration
  - Link from getting-started
  - Link from advanced usage
  - Feature highlights on homepage

---

## Dependencies & Sequencing

### Strict Sequencing (Blocking)

```
Phase 0 (Setup)
    ↓
Phase 1 (Foundational Docs) — BLOCKS all user stories
    ├→ Phase 2 (US1: GitHub Actions)
    ├→ Phase 3 (US2: GitLab CI)
    └→ Phase 4 (US3: Generic CI)
         └→ Phase 5 (Dogfood) — Can start after US1 complete
             └→ Phase 6 (Polish) — Final validation & release
```

### Parallelizable Work

**Within Phase 2 (US1)**: T101-T104, T106, T109-T110 can run in parallel  
**Within Phase 3 (US2)**: T201-T205, T207, T210-T212 can run in parallel  
**Within Phase 4 (US3)**: T302-T306, T308, T311-T313 can run in parallel  
**Within Phase 5 (Dogfood)**: T401-T403 can run in parallel  
**Within Phase 6 (Polish)**: T503-T504, T603-T604 can run in parallel

---

## Independent Test Scenarios

### US1 (GitHub Actions): Minimal MVP Test
```
Given: Developer has GitHub repo with playbooks in ./playbooks
When: Developer copies docs/examples/workflows/github-actions-basic.yml to .github/workflows/
And: Updates ANODYSE_INPUT_DIR to ./playbooks, ANODYSE_OUTPUT_DIR to ./docs
And: Pushes a commit to main branch
Then: Workflow triggers and completes successfully
And: Documentation generated in ./docs/
And: Artifacts available for download
Acceptance: ✓ 20-minute setup time achieved
```

### US2 (GitLab CI): Minimal MVP Test
```
Given: Developer has GitLab project with playbooks in ./playbooks
When: Developer adds docs/examples/gitlab-ci-basic.yml to .gitlab-ci.yml
And: Updates ANODYSE_INPUT_DIR to ./playbooks
And: Pushes a commit
Then: Pipeline triggers and completes successfully
And: Documentation generated in job artifacts
And: Artifacts stored with 30-day retention
Acceptance: ✓ 20-minute setup time achieved
```

### US3 (Generic CI): Minimal MVP Test
```
Given: Developer reads docs/CI_INTEGRATION.md#generic-ci and docs/examples/jenkins/
When: Developer implements Anodyse invocation in their Jenkins/Woodpecker/CircleCI job
And: Configures environment variables per documentation
And: Triggers build
Then: Build succeeds and documentation is generated
And: Artifacts stored in CI artifact staging area
Acceptance: ✓ Developer successfully replicated GitHub/GitLab patterns
```

---

## MVP Scope (Recommended Minimum)

**Phase 0**: Setup (1 day)  
**Phase 1**: Foundational docs (2 days)  
**Phase 2**: GitHub Actions (3 days) ← **Ship MVP after this**  
**+ Dogfood**: Implement in anodyse repo (1 day)

**MVP Delivery**: Copy-paste GitHub Actions workflows + Setup guide  
**Timeline**: ~7 days for MVP, 14-21 days for full feature (all 3 platforms + polish)

---

## Task Metrics

| Phase | Tasks | Estimated Hours | Parallel Potential |
|-------|-------|-----------------|-------------------|
| Phase 0 | 6 | 4-6 | High (all independent) |
| Phase 1 | 8 | 12-16 | Medium (section overlap) |
| Phase 2 | 11 | 16-20 | High (7 parallelizable) |
| Phase 3 | 12 | 16-20 | High (6 parallelizable) |
| Phase 4 | 13 | 20-24 | High (8 parallelizable) |
| Phase 5 | 6 | 8-10 | High (3 parallelizable) |
| Phase 6 | 8 | 12-16 | Medium (mixed) |
| **TOTAL** | **64** | **88-112 hours** | **~6-8 days (full team)** |

---

## Quality Checklist

Before marking tasks complete:

- [ ] All code examples tested and working
- [ ] All file paths verified and accurate
- [ ] All documentation links validated
- [ ] Cross-platform compatibility verified
- [ ] Error messages and troubleshooting clear
- [ ] Screenshots/diagrams added where helpful
- [ ] No hardcoded credentials or tokens in examples
- [ ] Consistent terminology across all guides
- [ ] User testing completed (UAT)
- [ ] README and homepage updated with feature link

---

**Status**: Tasks Complete ✅  
**Total Tasks**: 64  
**Ready for Implementation**: Phase 0 can start immediately  
**MVP Milestone**: Complete Phase 0 + Phase 1 + Phase 2 (~7 days)  
**Full Feature**: All 6 phases (~15-21 days with parallel execution)
