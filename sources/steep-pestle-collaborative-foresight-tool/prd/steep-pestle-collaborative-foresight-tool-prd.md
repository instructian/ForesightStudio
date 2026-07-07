# PRD: Collaborative STEEP/PESTLE Signal, Trend, and Scenario Studio

Date: 2026-05-03
Status: Draft for review
Primary audience: students, instructors, curriculum owners, product/design/engineering teams

## 1. Executive Summary

This product is a collaborative strategic foresight workspace for students learning STEEP and PESTLE analysis. Students collect weak signals, interpret them as part of larger trends, combine them into annotated collections, and use those collections to develop future scenarios, speculative design opportunities, personas, problem statements, and user journeys.

The current logging sheet is a useful starting point because it captures PESTLE category, keywords, signal title, description, context, implications, relevance, trend analysis, certainty, future wheel, date, student name, and source. However, it has several limitations that the product should solve:

- Participation is captured through a free-text `Name` field rather than authenticated student identity.
- Dates are frequently missing and do not distinguish source publication date, signal observation date, and submission date.
- Multiple sources spill into unlabeled columns after `Source`, making source quality, citation, and deduplication hard.
- The category model supports five STEEP categories in the sheet, but not Legal, which is needed for PESTLE.
- Relevance, certainty, and trend analysis are free-form enough that students may answer inconsistently.
- There is no structured way to link signals to one another, combine them into trends, create shared collections, or assess contribution quality.
- There is no instructor analytics layer, collaboration layer, or scenario-generation workflow.

The proposed tool turns the spreadsheet into a structured learning environment with guided help text for every field, reusable taxonomies, evidence/source management, collaboration, instructor dashboards, optional LLM-assisted interpretation, and a scenario studio that requires students to ground each future scenario in at least five signals.

## 2. Product Vision

The tool should help students move from "I found an interesting article" to "I can defend a future-facing interpretation of change, connect it to other evidence, and use it to frame meaningful speculative design work."

It should make high-quality foresight practice easier without hiding the method. Students should see what they are collecting, why each data point matters, how signals become trends, and how trends become scenarios. Instructors should be able to observe participation, assess analytical quality, and optionally configure an LLM to support clustering, interpretation, critique, and scenario drafting while keeping student authorship visible.

## 3. Source Materials Reviewed

### 3.1 Attached PESTLE Skill

The attached ZIP contains a single `SKILL.md` defining a `pestle-analysis` skill. It frames PESTLE as a strategic macro-environment analysis across:

- Political
- Economic
- Social
- Technological
- Legal
- Environmental

The skill emphasizes identifying relevant factors, assessing impact and likelihood, prioritizing by impact x probability, developing strategic responses, identifying metrics or leading indicators, building contingency plans, and documenting assumptions and unknowns.

The product should embed those concepts directly into the data model and student workflows rather than reducing PESTLE to a category dropdown.

### 3.2 Attached Workbook Baseline

Workbook: `FA23-MM680-SCANNING.xlsx`

Observed structure:

- One worksheet with 41 filled signal rows.
- Main headers: Category, Keywords, Signal Title, Signal Description, Context, Implications, Relevance, Trend Analysis, Certainty, Future Wheel, Date, Name, Source.
- Header comments provide basic field guidance for several columns.
- Data validation exists for category, certainty, and student name.
- The category list includes Social, Technological, Economical, Environmental, Political. It does not include Legal, and "Economical" should become "Economic."
- Student participation can be inferred from `Name`, but the field is manually entered and inconsistent.
- `Date` is missing on roughly 78 percent of filled rows.
- `Trend Analysis`, `Relevance`, and `Implications` have notable gaps.
- Multiple sources are sometimes placed in unlabeled columns N through W.

These findings inform the data improvements and instructor dashboard requirements below.

## 4. Goals

1. Help students collect higher-quality signals with clear guidance, structured evidence, and consistent metadata.
2. Help students connect signals into trends, clusters, collections, and future scenarios.
3. Make collaboration visible through shared workspaces, comments, annotations, collection ownership, and version history.
4. Give instructors a backend view of student participation, contribution quality, missing work, and class-level thematic patterns.
5. Support STEEP and PESTLE modes, including configurable course taxonomies.
6. Provide optional LLM assistance that instructors can enable, configure, and audit for local or hosted model providers.
7. Support scenario creation based on selected signals, scenario archetypes, time horizons, problem statements, personas, and user journeys.
8. Preserve provenance so every trend, collection, and scenario can be traced back to the signals and sources used to create it.

## 5. Non-Goals

- The product is not a general LMS replacement.
- The product is not a citation manager, although it should manage citations well enough for foresight assignments.
- The product is not an autonomous scenario generator. It may assist, but students must choose, edit, justify, and submit their interpretations.
- The product is not a grading engine. It should support assessment and rubrics, but final grading belongs to instructors.
- The product should not require an LLM to be useful.

## 6. Primary Users

### 6.1 Student

Students collect signals, search and browse the class database, create or join collections, annotate relationships, create trends, and develop scenarios for speculative design work.

Key needs:

- Understand what counts as a signal.
- Submit work quickly without losing methodological rigor.
- Receive help text and examples while completing fields.
- Find related signals submitted by classmates.
- Combine evidence into meaningful patterns.
- Explain why a signal matters.
- Create scenario vignettes grounded in evidence.
- Show their contribution to collaborative work.

### 6.2 Instructor

Instructors configure courses, assignments, taxonomies, required fields, rubrics, collaboration settings, and optional AI settings. They monitor participation and review student outputs.

Key needs:

- See who submitted what, when, and at what level of completeness.
- Identify students who are not participating.
- Review quality of sources, descriptions, and analysis.
- Configure course-specific PESTLE/STEEP categories and help text.
- Moderate, merge, or correct noisy student data.
- Export data for assessment or class discussion.
- Enable or disable LLM assistance safely.

### 6.3 Teaching Assistant or Reviewer

Teaching assistants help review submissions, tag records, resolve duplicates, and give feedback.

Key needs:

- Filter by course section, student, assignment, status, category, and quality flag.
- Leave comments and request revisions.
- Bulk review or approve signals.

### 6.4 Program Admin

Program admins manage institution-level settings, privacy, authentication, and model-provider policies.

Key needs:

- Configure SSO/LMS integrations.
- Control whether hosted LLMs are allowed.
- Manage data retention and export rules.

## 7. Success Metrics

### 7.1 Student Learning Metrics

- Median number of complete signals submitted per student per assignment.
- Percent of signals with valid source metadata and source-quality assessment.
- Percent of signals linked to at least one trend or collection.
- Percent of scenarios grounded in at least five approved signals.
- Improvement in rubric scores for signal quality, trend synthesis, and scenario plausibility.

### 7.2 Instructor Workflow Metrics

- Time required to assess participation for a class section.
- Percent of submissions that can be reviewed without manual cleanup.
- Number of duplicate or low-quality records identified before final submission.
- Instructor adoption of dashboards, exports, and rubric workflows.

### 7.3 Collaboration Metrics

- Number of shared collections created.
- Number of comments, annotations, and relationship links created.
- Distribution of contributions within each collection.
- Percent of group projects where all assigned students make at least one substantive contribution.

### 7.4 AI Assistance Metrics

- Percent of LLM suggestions accepted, edited, or rejected.
- Student edits after AI suggestions.
- Instructor-reported usefulness of AI clustering, critique, and scenario prompts.
- Incidents of unsupported claims introduced by AI.

## 8. Core Concepts

### 8.1 Signal

A signal is a concrete observation of change. It is usually small, specific, and sourceable: an article, policy proposal, research finding, behavior shift, product launch, court ruling, environmental event, social practice, or emerging technology.

### 8.2 Trend

A trend is a pattern inferred from multiple signals. Trends should not be created from a single source unless marked as preliminary. A trend should explain direction, momentum, uncertainty, affected stakeholders, and possible implications.

### 8.3 Collection

A collection is a curated set of signals and trends assembled for a purpose. Collections may support class discussion, group projects, research themes, scenario development, or speculative design briefs. Collections include contextual notes and can be shared.

### 8.4 Scenario

A scenario is a plausible future environment constructed from signals, trends, scenario archetypes, and time horizons. Each scenario must be traceable to at least five signals and should include:

- Future environment description
- Scenario vignette
- Problem statements
- Opportunity statements
- Personas
- User journeys
- Design prompts
- Assumptions and uncertainties

### 8.5 Scenario Archetype

A scenario archetype is a pattern for imagining how change unfolds. The tool should support configurable archetypes, with defaults such as:

- Continuation: current patterns intensify or stabilize.
- Constraint: scarcity, regulation, cost, or risk limits behavior.
- Breakthrough: a technological, social, or policy shift accelerates change.
- Fragmentation: groups, regions, markets, or institutions diverge.
- Regeneration: communities rebuild around sustainability, care, repair, or resilience.
- Crisis and adaptation: a shock forces rapid reorganization.

### 8.6 Time Horizon

Time horizon is the future distance used for analysis. Defaults should be configurable by course:

- Near term: 1 to 3 years
- Mid term: 3 to 7 years
- Long term: 7 to 15 years
- Transformational: 15 or more years

## 9. Product Scope

### 9.1 MVP Scope

The MVP should include:

- Course and assignment setup.
- Student authenticated submission of signals.
- Structured signal form with help text for each datum.
- STEEP/PESTLE category mode.
- Search, sort, filter, and saved views.
- Signal detail pages with source, comments, relationships, and revision history.
- Trend creation from multiple signals.
- Shared collections with contextual notes.
- Instructor participation dashboard.
- Basic export to CSV/XLSX.
- Scenario builder requiring at least five signals.
- LLM integration setting that can be disabled, configured, and audited, but can ship as a controlled beta.

### 9.2 Post-MVP Scope

Post-MVP should include:

- Visual connection maps.
- Timeline and horizon scanning views.
- Advanced network analysis of tags, signals, students, and themes.
- LMS gradebook integration.
- Source credibility automation.
- Citation formatting.
- Rubric scoring workflows.
- Portfolio export.
- Model evaluation dashboards.
- Multi-course institutional libraries.

## 10. Data Improvements Over the Existing Sheet

### 10.1 Replace Free-Text Student Name with Authenticated Identity

Current issue: The sheet uses a `Name` dropdown, which can be incomplete or inconsistent.

Requirement:

- Student identity should come from login or course roster.
- A display name may appear on submissions.
- The system should store `submitted_by_user_id`, `submitted_at`, and `last_edited_by_user_id`.
- Instructors should be able to see contribution counts by student, assignment, group, and date range.

### 10.2 Split Source Into a Source Object

Current issue: Multiple sources are stored across unlabeled columns.

Requirement:

- A signal can have one or more sources.
- Each source should have structured fields: title, URL/file, source type, publisher, author, publication date, access date, credibility rating, relevance note, and citation.
- Students should identify the primary source.
- The tool should detect duplicate URLs.

### 10.3 Add Dates with Clear Meaning

Current issue: `Date` is mostly missing and ambiguous.

Requirement:

- `submitted_at` is automatic.
- `source_published_on` is captured per source when available.
- `signal_observed_on` captures when the event, behavior, policy, or phenomenon occurred.
- `time_horizon_relevance` captures whether the signal is near-term, mid-term, long-term, or transformational.

### 10.4 Improve Category Model

Current issue: The sheet uses STEEP-like categories but not Legal, and "Economical" should be "Economic."

Requirement:

- Course can run in STEEP mode or PESTLE mode.
- Default PESTLE categories: Political, Economic, Social, Technological, Legal, Environmental.
- Signals can have one primary category and optional secondary categories.
- Instructors can add course-specific subcategories.

### 10.5 Add Analytical Scoring

Current issue: Relevance and certainty are free-form.

Requirement:

- Replace or augment free text with structured scales:
  - Relevance: Low, Medium, High, Critical
  - Impact: Low, Medium, High, Transformative
  - Likelihood: Low, Medium, High, Unknown
  - Uncertainty: Low, Medium, High
  - Novelty: Familiar, Emerging, Weak Signal, Wildcard
  - Time horizon: Near, Mid, Long, Transformational
  - Evidence strength: Weak, Moderate, Strong
- Students should still explain their reasoning in short text fields.

### 10.6 Add Relationship and Synthesis Fields

Requirement:

- Signals can be linked as supports, contradicts, amplifies, weakens, precedes, consequence of, or adjacent to another signal.
- Students can mark whether a signal is an opportunity, threat, constraint, uncertainty, driver, or leading indicator.
- Trends can show the signals used to infer them.

### 10.7 Add Foresight Method Fields

Requirement:

- Capture assumptions and unknowns.
- Capture leading indicators to monitor.
- Capture possible strategic responses.
- Capture stakeholder groups affected.
- Capture ethical, equity, access, and sustainability considerations.

## 11. Data Dictionary and Help Text

Every student-facing field should include inline help, examples, validation rules, and instructor-editable course language. Help text should be available as hover text, side-panel guidance, and field-level examples.

### 11.1 Signal Fields

| Field | Required | Type | Help Text for Students | Validation / Notes |
|---|---:|---|---|---|
| Signal Title | Yes | Short text | Give the signal a concise name that someone can recognize in a list. Use a specific title, not a broad topic. Example: "AI weather models outperform traditional 10-day forecasts." | 8 to 120 characters. |
| Signal Summary | Yes | Long text | Describe what happened, what changed, or what was observed. Stay concrete before interpreting. | 50 to 1,200 characters. |
| Primary Category | Yes | Dropdown | Choose the STEEP/PESTLE category that best explains the main kind of change. | Course-controlled options. |
| Secondary Categories | No | Multi-select | Add other categories touched by the signal. Many good signals cross categories. | Max 3 recommended. |
| Keywords / Tags | Yes | Tag input | Add searchable words that describe the topic, affected domain, technology, population, policy, or risk. | Normalize duplicates and spelling. |
| Source(s) | Yes | Source object | Add the article, report, paper, dataset, interview, observation, or artifact where you found the signal. | At least one primary source. |
| Source Type | Yes | Dropdown | Identify what kind of evidence this is: news article, academic paper, government report, company announcement, dataset, field observation, social media, patent, legal case, policy proposal, or other. | Required per source. |
| Source Publication Date | Recommended | Date | When was the source published or last updated? Use the source date, not today's date. | Warn if missing. |
| Signal Observed Date | Recommended | Date or date range | When did the event or behavior happen? If the source is about a long-running issue, use a range or mark "ongoing." | Supports ongoing/unknown. |
| Geographic Scope | Yes | Dropdown + text | Where is this signal relevant? Examples: local, city, state, national, regional, global, online community, supply chain. | Enables map/filter views. |
| Affected Stakeholders | Yes | Multi-select + text | Who may be affected? Consider users, workers, communities, institutions, governments, businesses, ecosystems, and non-human systems. | Encourage specificity. |
| Context | Yes | Long text | Explain the background needed to understand why this signal matters. What conditions made it possible? | 80 to 1,500 characters. |
| Implications | Yes | Long text | Explain possible consequences if this signal grows, spreads, or combines with other changes. Include both opportunities and risks when relevant. | 80 to 1,500 characters. |
| Relevance Rating | Yes | Scale | How relevant is this signal to the course theme or project brief? | Low, Medium, High, Critical. |
| Relevance Rationale | Yes | Short text | Explain why you chose that relevance rating. | Required when relevance is High or Critical. |
| Impact Rating | Yes | Scale | If this signal becomes more widespread, how large could its effect be? | Low, Medium, High, Transformative. |
| Likelihood | Yes | Scale | How likely is it that this signal will continue, scale, or influence the future? | Low, Medium, High, Unknown. |
| Uncertainty | Yes | Scale | How uncertain is your interpretation? High uncertainty is acceptable if explained. | Low, Medium, High. |
| Evidence Strength | Yes | Scale | How strong is the evidence behind this signal? Consider source quality, specificity, corroboration, and recency. | Weak, Moderate, Strong. |
| Novelty | Yes | Dropdown | Is this a familiar trend, an emerging signal, a weak signal, or a wildcard? | Instructor can define terms. |
| Time Horizon Relevance | Yes | Multi-select | When might this matter most: 1-3 years, 3-7 years, 7-15 years, 15+ years? | Used in scenario builder. |
| Related Trend Hypothesis | Recommended | Short text | What larger trend might this signal be part of? This can be tentative. | Can later convert into a trend. |
| Leading Indicators | Recommended | Long text | What should we monitor to know whether this signal is strengthening or fading? | Supports PESTLE skill guidance. |
| Strategic Response | Optional | Long text | What might designers, organizations, communities, or policymakers do in response? | Opportunity, mitigation, adaptation, compliance. |
| Assumptions | Recommended | Long text | What are you assuming that may need to be checked? | Helps students separate evidence from interpretation. |
| Unknowns / Research Questions | Recommended | Long text | What do you still need to learn? | Can become research tasks. |
| Ethics / Equity Considerations | Recommended | Long text | Who benefits, who is burdened, who is excluded, and what harms could appear? | Useful for speculative design. |
| Submitted By | Automatic | User reference | Your account will be attached automatically. | Not manually editable by students. |
| Submitted At | Automatic | Timestamp | The system records when you submitted. | Used in participation dashboard. |
| Status | Automatic/manual | Workflow state | Draft, submitted, needs revision, approved, archived, duplicate. | Instructor/reviewer controlled after submission. |

### 11.2 Source Fields

| Field | Required | Help Text |
|---|---:|---|
| Source Title | Yes | Use the title of the article, report, paper, dataset, or artifact. |
| URL or File | Yes | Paste the source link or upload a file. If the source is offline, describe where it came from. |
| Publisher / Organization | Recommended | Name the organization responsible for publishing the source. |
| Author | Optional | Add the author when available. |
| Publication Date | Recommended | Use the date shown by the source. |
| Access Date | Automatic | The system records when the source was added. |
| Source Type | Yes | Choose the evidence type so reviewers can interpret credibility. |
| Credibility Rating | Yes | Rate whether the source seems weak, moderate, or strong. Explain if weak. |
| Source Note | Recommended | Say why this source supports the signal. Do not paste the full article. |
| Citation | Automatic/editable | The system generates a citation students may edit. |

### 11.3 Trend Fields

| Field | Required | Help Text |
|---|---:|---|
| Trend Name | Yes | Name the broader pattern inferred from multiple signals. |
| Trend Claim | Yes | State the trend as an argument about change, not just a topic. |
| Supporting Signals | Yes | Select at least two signals for a preliminary trend and at least five for a strong trend. |
| Contradicting Signals | Optional | Add signals that complicate or challenge the trend. |
| Direction of Change | Yes | Is the trend increasing, decreasing, fragmenting, stabilizing, accelerating, or uncertain? |
| Momentum | Yes | Estimate whether the trend is weak, moderate, strong, or volatile. |
| Impact | Yes | Estimate potential effect if the trend continues. |
| Likelihood | Yes | Estimate likelihood and explain uncertainty. |
| Affected Stakeholders | Yes | Identify who is most affected. |
| Leading Indicators | Recommended | List measurable signs to monitor. |
| Implications | Yes | Explain what this trend could mean for design, policy, business, culture, or everyday life. |
| Notes | Optional | Add interpretation, disagreement, or questions. |

### 11.4 Collection Fields

| Field | Required | Help Text |
|---|---:|---|
| Collection Title | Yes | Name the curated set of signals and trends. |
| Purpose | Yes | Explain why this collection exists: class discussion, scenario, project theme, research question, design brief, etc. |
| Included Items | Yes | Add signals and/or trends. |
| Contextual Notes | Yes | Explain the connection between items. What pattern, tension, or question does this collection reveal? |
| Collection Tags | Optional | Add tags for search and reuse. |
| Visibility | Yes | Private, group, class, instructor-only, or public export. |
| Collaborators | Optional | Add students or groups who can edit. |
| Contribution Summary | Automatic | The system shows who added, edited, commented, or removed items. |
| Discussion | Optional | Threaded comments for interpretation and critique. |

### 11.5 Scenario Fields

| Field | Required | Help Text |
|---|---:|---|
| Scenario Title | Yes | Give the future environment a memorable title. |
| Time Horizon | Yes | Choose when this scenario takes place. |
| Scenario Archetype | Yes | Choose the pattern of future change: continuation, constraint, breakthrough, fragmentation, regeneration, crisis/adaptation, or instructor-defined. |
| Source Signals | Yes | Select at least five signals. Strong scenarios should use signals across more than one category. |
| Source Trends | Recommended | Add trends that help explain the future environment. |
| Future Environment Description | Yes | Describe the social, technological, economic, environmental, political, and legal conditions of this future. Ground the description in the selected signals. |
| Vignette | Yes | Write a short scene showing everyday life in this scenario. Use concrete details and avoid generic futurism. |
| Problem Statements | Yes | Define the problems that emerge in this future. Use "How might we..." or equivalent formats when useful. |
| Opportunity Statements | Recommended | Identify openings for speculative design projects, services, policies, artifacts, or experiences. |
| Personas | Yes | Create at least two personas affected by this future. Include needs, constraints, motivations, access, and risks. |
| User Journeys | Yes | For each persona, describe a journey through a relevant task or experience in the future environment. |
| Tensions and Tradeoffs | Recommended | What conflicts shape this scenario? Who gains and who loses? |
| Assumptions | Yes | List assumptions that make the scenario plausible. |
| Open Questions | Yes | List research questions or uncertainties that remain. |
| Design Brief | Recommended | Summarize the speculative design challenge created by the scenario. |

## 12. Functional Requirements

### 12.1 Course and Assignment Setup

Instructors must be able to:

- Create a course workspace.
- Import or sync a roster.
- Create assignments with due dates, group settings, required number of signals, required fields, and rubric criteria.
- Choose STEEP or PESTLE mode.
- Add course-specific categories, tags, archetypes, time horizons, and example signals.
- Configure whether student submissions are visible immediately, after approval, or after due date.
- Configure whether students may edit after submission.
- Configure whether students may see other students' names.

Acceptance criteria:

- An instructor can create an assignment requiring each student to submit five signals, join one collection, and create one scenario.
- The assignment can require at least one signal from specific categories.
- The assignment can require at least one source per signal and one rationale for each rating.

### 12.2 Student Signal Submission

Students must be able to:

- Create draft signals.
- Save incomplete drafts.
- View inline help for every field.
- Submit signals with authenticated identity.
- Add multiple sources without using extra columns.
- Add tags, categories, ratings, implications, assumptions, and research questions.
- See completion indicators before submitting.
- Receive validation warnings for missing source dates, weak evidence, vague titles, or missing rationale.

Acceptance criteria:

- A student cannot submit a final signal without title, summary, primary category, source, context, implications, relevance rating, impact rating, likelihood, uncertainty, evidence strength, and authenticated identity.
- A student can submit a signal with multiple sources, each with its own metadata.
- The system stores revision history for edits.

### 12.3 Browse, Search, Sort, and Filter

Users must be able to view and work with the signal database through multiple modes:

- Table view for spreadsheet-like scanning.
- Card view for quick reading.
- Detail view for one signal.
- Category board by STEEP/PESTLE category.
- Timeline view by source date, observed date, or submission date.
- Tag explorer.
- Student contribution view, instructor-only by default.
- Relationship map, post-MVP if not in MVP.

Search and filters should include:

- Full-text search across title, summary, context, implications, tags, source title, and notes.
- Category and subcategory.
- Tags and keywords.
- Student or group.
- Date range.
- Time horizon.
- Source type.
- Evidence strength.
- Relevance, impact, likelihood, uncertainty, and novelty.
- Status.
- Used or unused in trends, collections, or scenarios.

Acceptance criteria:

- A user can find all high-impact technological signals tagged "healthcare" with strong evidence.
- A student can sort signals by relevance, date, impact, or number of connections.
- An instructor can filter to submitted but incomplete or needs-revision signals.

### 12.4 Linking and Relationship Mapping

Students must be able to connect signals to one another.

Relationship types:

- Supports
- Contradicts
- Amplifies
- Weakens
- Precedes
- Consequence of
- Similar to
- Causes uncertainty for
- Suggests opportunity for
- Suggests threat for

Acceptance criteria:

- A student can link two signals and explain the relationship.
- Relationship links appear on each signal detail page.
- Collections and scenarios preserve relationship context.

### 12.5 Trend Creation

Students must be able to create trends from signals.

Requirements:

- Students can select signals and convert them into a trend draft.
- The system prompts students to write a trend claim.
- The trend must distinguish evidence from interpretation.
- The system shows gaps, such as trends based on only one category or weak evidence.
- Trends can be class-visible, group-visible, or private.

Acceptance criteria:

- A trend created from fewer than two signals is labeled "hypothesis" or "preliminary."
- A trend created from five or more approved signals can be labeled "well supported" if the student adds a rationale.
- Students can add contradicting evidence.

### 12.6 Collections Workspace

Collections are the main collaboration workspace.

Requirements:

- Students can create collections from signals and trends.
- Collections can be private, group-shared, class-shared, or instructor-only.
- Collections include a notes area for contextual synthesis.
- Collections support threaded comments.
- Collections track who added each item and who wrote each note.
- Collections can be duplicated or forked.
- Collections can be exported as a PDF, Markdown, CSV, or presentation outline.
- Collections can be used as input to scenarios.

Ways to work with collection data:

- Sort items by category, time horizon, date, impact, uncertainty, source strength, or contributor.
- Group items by category, tag, stakeholder, geography, or time horizon.
- Create clusters manually.
- Compare two collections.
- Highlight tensions and contradictions.
- Mark key signals.
- Create relationship notes between selected items.
- Convert a collection into a scenario brief.

Acceptance criteria:

- A student can create a shared collection, add ten signals, group them by time horizon, and write a contextual note explaining the pattern.
- Another student can comment on that interpretation and suggest a contradicting signal.
- The instructor can see the contribution history.

### 12.7 Scenario Studio

The Scenario Studio must help students create evidence-grounded scenarios for speculative design.

Requirements:

- Students can start a scenario from a collection, trend, or selected signals.
- Each scenario must include at least five signals.
- The system should encourage category diversity but not require it by default.
- Students choose time horizon and scenario archetype.
- Students are prompted to describe the future environment.
- Students write a vignette showing lived experience in that future.
- Students create problem statements and opportunity statements.
- Students create personas and user journeys for those personas.
- The scenario must include assumptions, uncertainties, and source traceability.

Scenario workflow:

1. Select source collection or at least five signals.
2. Choose time horizon.
3. Choose scenario archetype.
4. Review selected signals in a scenario evidence board.
5. Identify main drivers, uncertainties, tensions, stakeholders, and consequences.
6. Draft future environment description.
7. Draft vignette.
8. Draft problem statements and opportunity statements.
9. Create personas.
10. Create user journeys.
11. Review traceability and submit.

Acceptance criteria:

- The system blocks final submission if fewer than five signals are attached.
- Each scenario shows a source traceability panel.
- Each problem statement can be linked to one or more signals, trends, or journey pain points.
- Each persona has at least one user journey.

### 12.8 Scenario Vignette Prompting

The tool should guide students to write concrete vignettes.

Student prompt:

"Write a scene from this future. Show a person, group, or institution encountering a meaningful problem or opportunity. Include concrete details about the environment, tools, constraints, norms, and choices. Ground the scene in the selected signals and time horizon."

Vignette requirements:

- 300 to 1,000 words by default, configurable.
- Must reference at least three of the selected signals explicitly or implicitly.
- Must include at least one stakeholder affected by the scenario.
- Must avoid unsupported magic leaps unless marked as speculative assumptions.

### 12.9 Problem Statements

Problem statements should help students move from scenario to design opportunity.

Supported formats:

- "How might we help [persona/stakeholder] achieve [need] despite [future constraint]?"
- "[Stakeholder] needs a way to [goal] because [future condition] makes [current approach] fail."
- "In a future where [scenario condition], [persona] struggles to [task], creating an opportunity for [design direction]."

Acceptance criteria:

- Each scenario requires at least two problem statements.
- Problem statements can be tagged by stakeholder, category, and design opportunity.

### 12.10 Personas

Personas must be scenario-specific, not generic marketing profiles.

Required persona fields:

- Name
- Role or relationship to the future environment
- Context and living/working conditions
- Goals
- Needs
- Constraints
- Access to technology/resources
- Risks or vulnerabilities
- Attitudes and motivations
- Signals/trends shaping their situation

Acceptance criteria:

- Each scenario requires at least two personas.
- Persona fields must refer to scenario conditions.

### 12.11 User Journeys

User journeys should show how a persona experiences a task or problem in the scenario.

Required journey fields:

- Persona
- Scenario context
- Goal
- Trigger
- Steps
- Touchpoints
- Pain points
- Workarounds
- Emotional state
- Opportunities for design intervention
- Signals/trends connected to each major step

Acceptance criteria:

- Each persona must have at least one journey.
- Journey steps can be displayed as a timeline or table.

### 12.12 Instructor Backend

Instructors need a backend view for participation and quality.

Dashboard requirements:

- Total submissions by student.
- Complete vs incomplete submissions.
- Draft vs submitted vs approved vs needs-revision counts.
- Submissions by date.
- Category coverage by student and class.
- Tag cloud or theme summary.
- Source completeness and evidence strength.
- Signals used in trends, collections, and scenarios.
- Comments and collaboration activity.
- Group contribution distribution.
- Late or missing work.
- Revision requests.
- Exportable participation report.

Quality review indicators:

- Missing required fields.
- Weak source credibility.
- No source publication date.
- Vague title.
- Duplicate URL or similar signal.
- High-impact signal without rationale.
- Scenario using fewer than five signals.
- Scenario with narrow category diversity.

Acceptance criteria:

- Instructor can filter the dashboard by assignment, section, group, date range, category, and student.
- Instructor can open a student profile showing submissions, comments, collections, scenarios, and contribution history.
- Instructor can export participation and signal data.

### 12.13 Rubrics and Feedback

The tool should support instructor-defined rubrics.

Default rubric categories:

- Signal specificity
- Source quality
- Contextual understanding
- Implication quality
- PESTLE/STEEP categorization
- Trend synthesis
- Collaboration
- Scenario plausibility
- Scenario creativity
- Evidence traceability
- Ethical/equity reflection

Feedback requirements:

- Instructors can comment on specific fields.
- Instructors can request revisions.
- Students can resubmit when allowed.
- Rubric scores can be exported.

### 12.14 Import and Export

Import:

- CSV/XLSX import from existing signal logs.
- Column mapping UI.
- Duplicate detection.
- Student name mapping to roster when possible.
- Source columns N+ should be mapped into multiple source objects.

Export:

- CSV/XLSX for signals, trends, collections, scenarios, sources, and participation.
- Markdown/PDF export for collections and scenarios.
- Instructor gradebook export.
- JSON export for advanced analysis.

Acceptance criteria:

- The attached workbook structure can be imported with mapping rules.
- Multiple unlabeled source columns can be converted into separate source records.

## 13. Optional LLM Integration

### 13.1 Product Principle

The LLM should assist interpretation, organization, critique, and drafting. It should not replace student thinking or instructor judgment. All AI outputs must be visibly marked, editable, and auditable.

### 13.2 Instructor Control

Instructors must be able to:

- Enable or disable LLM features per course or assignment.
- Choose allowed use cases.
- Configure model provider.
- Choose local or hosted endpoint.
- Provide API key or local endpoint securely.
- Set model, temperature, context limits, and privacy mode.
- Decide whether student prompts and outputs are logged.
- Decide whether AI suggestions can be used in final submissions.
- Provide course-specific system instructions.

Provider modes:

- Disabled.
- Local model endpoint, such as OpenAI-compatible local server, Ollama, LM Studio, or institution-hosted endpoint.
- Hosted model provider through instructor or institution credentials.
- Bring-your-own-provider configuration using a generic OpenAI-compatible API.

### 13.3 AI Use Cases

Allowed AI assist features should be modular:

- Signal cleanup: suggest clearer title, tags, category, or summary.
- Field critique: identify missing evidence, vague implications, or unsupported claims.
- Source extraction: suggest source title, publisher, and publication date from URL metadata when available.
- Similar-signal detection: suggest duplicates or related signals.
- Clustering: propose possible clusters across signals.
- Trend drafting: suggest trend claims from selected signals.
- Contradiction finding: identify selected signals that may challenge a trend.
- Leading indicator suggestions.
- Scenario scaffolding: suggest future environment outline from selected signals.
- Vignette critique: ask whether the vignette is grounded in signals.
- Persona and user journey prompts.
- Instructor analytics summaries.

### 13.4 Human-AI Boundary

The system must preserve human decision-making:

- AI suggestions are drafts, not final answers.
- Students must accept, edit, or reject suggestions.
- The system should log whether AI assisted a field.
- Instructors can view AI-assistance metadata if enabled.
- The system should encourage students to explain why they accepted or changed important AI suggestions.

### 13.5 AI Safety, Privacy, and Audit

Requirements:

- Never send student data to hosted models unless instructor/institution settings allow it.
- Clearly label when content may leave the institution environment.
- Redact or exclude student identity from model prompts when possible.
- Store prompt, model, timestamp, and output metadata when audit logging is enabled.
- Provide a "no AI" course mode.
- Provide a "local only" course mode.
- Provide disclaimers that AI may invent connections or overstate certainty.
- Require source traceability for AI-generated trend or scenario text.

### 13.6 AI Evaluation

The product should measure:

- Whether AI suggestions preserve source claims.
- Whether AI clusters are useful to students.
- Whether AI introduces unsupported facts.
- Whether student final work differs meaningfully from AI drafts.
- Whether instructors find summaries faithful enough.

The system should support instructor feedback on AI suggestions:

- Useful
- Partly useful
- Not useful
- Unsupported
- Biased or problematic
- Needs better evidence

## 14. UX Requirements

### 14.1 Student Home

Student home should show:

- Current assignments.
- Signal submission progress.
- Draft signals.
- Recent class signals.
- Collections they own or collaborate on.
- Scenarios in progress.
- Instructor feedback.

### 14.2 Signal Entry Experience

Signal entry should feel guided but not slow.

UX requirements:

- Progressive disclosure: show essential fields first, advanced fields below.
- Inline help next to every field.
- Examples visible on demand.
- Completion meter.
- Save draft.
- Submit button with validation summary.
- Source add/edit panel.
- Duplicate warning.
- "Find related signals" after save.

### 14.3 Data Workspace

The workspace should support multiple ways of seeing the same data:

- Table
- Cards
- Timeline
- Category board
- Tag explorer
- Collection canvas
- Relationship map
- Scenario evidence board

Users should be able to switch views without losing filters.

### 14.4 Collaboration

Requirements:

- Comments on signals, trends, collections, and scenarios.
- Mentions.
- Suggested edits.
- Contribution history.
- Presence indicators for group work, if feasible.
- Fork or duplicate collection to explore alternate interpretations.
- Share link within course workspace.

### 14.5 Instructor Dashboard UX

Instructor dashboard should prioritize fast scanning:

- Participation summary at top.
- At-risk students or groups.
- Missing required submissions.
- Signals needing review.
- Category coverage chart.
- Trend and scenario submission status.
- Export buttons.
- Drill-down tables.

## 15. Permissions and Roles

Roles:

- Student
- Group owner
- Teaching assistant
- Instructor
- Course admin
- Institution admin

Permission examples:

- Students can edit their drafts.
- Students can edit submitted work only if assignment allows it.
- Students can comment on class-visible work if enabled.
- Instructors can view all course work.
- Teaching assistants can review and comment if granted.
- Institution admins can configure provider policies but should not automatically see student content unless policy allows it.

Visibility options:

- Private draft
- Submitted to instructor
- Group visible
- Class visible
- Public export, instructor-controlled

## 16. System Architecture Requirements

### 16.1 Conceptual Services

- Authentication and roster service.
- Course and assignment service.
- Signal repository.
- Source repository.
- Trend service.
- Collection service.
- Scenario service.
- Comment and annotation service.
- Participation analytics service.
- Export/import service.
- LLM provider gateway.
- Audit log service.

### 16.2 Data Entities

Core entities:

- User
- Course
- Section
- Assignment
- Group
- Signal
- Source
- Tag
- Category
- SignalRelationship
- Trend
- Collection
- CollectionItem
- Comment
- Scenario
- Persona
- UserJourney
- Rubric
- Review
- ParticipationEvent
- LLMConfiguration
- LLMAuditEvent

### 16.3 Traceability

The system must support traceability:

- Source to signal.
- Signal to trend.
- Signal/trend to collection.
- Signal/trend/collection to scenario.
- Scenario to problem statement, persona, and journey.
- User action to participation record.
- AI suggestion to accepted/edited/rejected field.

## 17. Participation Analytics

Participation should include quantity, timing, and contribution type.

Tracked events:

- Signal draft created.
- Signal submitted.
- Signal edited.
- Source added.
- Comment posted.
- Relationship created.
- Trend created.
- Collection created.
- Collection item added or removed.
- Collection note edited.
- Scenario created.
- Persona created.
- Journey created.
- Peer feedback given.
- Revision completed.

Instructor-visible measures:

- Number of signals submitted.
- Number of complete signals.
- Number of approved signals.
- Number of sources added.
- Number of comments and replies.
- Number of collection contributions.
- Number of scenario contributions.
- Average completeness score.
- On-time rate.
- Contribution balance in group projects.

Participation analytics should avoid overvaluing noisy activity. The dashboard should separate "activity count" from "substantive contribution," using rubric or review status where possible.

## 18. Validation Rules

Signal validation:

- Title cannot be blank.
- Summary cannot be blank.
- Primary category is required.
- At least one source is required.
- Context and implications are required for final submission.
- Relevance, impact, likelihood, uncertainty, and evidence strength are required.
- Student identity is automatic.
- Duplicate URL warning appears before submission.

Trend validation:

- Trend claim is required.
- At least two supporting signals are required.
- If only two signals are used, mark as preliminary.
- Impact and likelihood are required.

Collection validation:

- Title and purpose are required.
- At least one item is required.
- Contextual note is required before sharing with class.

Scenario validation:

- At least five signals are required.
- Time horizon is required.
- Scenario archetype is required.
- Future environment description is required.
- Vignette is required.
- At least two problem statements are required.
- At least two personas are required.
- Each persona requires at least one journey.

## 19. Accessibility and Inclusion Requirements

- Keyboard accessible interface.
- Screen-reader compatible form labels and help text.
- High-contrast mode.
- Captions or transcripts for any media help content.
- Clear plain-language field explanations.
- Support for multilingual source titles and notes if courses need it.
- Avoid color-only status indicators.
- Allow students to export their own work.

## 20. Privacy, Compliance, and Data Governance

Requirements:

- Student submissions are education records and should be handled with appropriate institutional privacy controls.
- Course-level visibility must be explicit.
- Student identity should not be sent to hosted LLM providers unless allowed by policy.
- Instructors should be able to anonymize class signal libraries for export.
- Audit logs should track instructor access, AI usage, and major content changes.
- Data retention settings should be configurable by institution or course.
- Export should allow removal of student names when needed.

## 21. Reporting and Exports

Student exports:

- My signals.
- My collections.
- My scenarios.
- Portfolio PDF or Markdown.

Instructor exports:

- All signals.
- All sources.
- Participation report.
- Rubric scores.
- Collections.
- Scenarios.
- Course library archive.

Export formats:

- CSV
- XLSX
- JSON
- Markdown
- PDF

## 22. Suggested MVP Milestones

### Milestone 1: Structured Signal Log

- Course workspace.
- Student login/roster.
- Signal form with help text.
- Multiple structured sources.
- Table/card browsing.
- Instructor participation dashboard.
- CSV/XLSX import/export.

### Milestone 2: Collaboration and Synthesis

- Comments.
- Signal relationships.
- Trend creation.
- Shared collections.
- Collection notes.
- Contribution history.

### Milestone 3: Scenario Studio

- Scenario creation from collections/signals.
- Archetype and time horizon selection.
- Future environment, vignette, problem statement, persona, and journey workflows.
- Traceability panel.

### Milestone 4: Optional LLM Assistance

- Instructor-configured provider gateway.
- AI-assisted signal cleanup, clustering, trend drafting, scenario scaffolding, and critique.
- Audit log and AI metadata.
- Local-only mode.

### Milestone 5: Advanced Analysis

- Relationship maps.
- Timeline visualization.
- Advanced instructor analytics.
- Rubrics and gradebook export.
- Cross-course libraries.

## 23. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Students submit broad topics instead of concrete signals. | Field help, examples, validation prompts, and instructor review. |
| Students over-rely on AI-generated interpretations. | AI metadata, required student rationale, instructor controls, and no-AI mode. |
| Source quality varies widely. | Source type, credibility rating, duplicate detection, and source-quality rubric. |
| Collaboration becomes unequal. | Contribution tracking by action type, group dashboard, and instructor alerts. |
| Scenario writing becomes generic. | Require at least five signals, archetype, time horizon, traceability, personas, and journeys. |
| Data entry becomes too burdensome. | Progressive disclosure, draft save, templates, examples, and import support. |
| Categories become rigid. | Primary plus secondary categories and instructor-editable taxonomies. |
| Privacy concerns around student names and hosted AI. | Authenticated identity, visibility controls, anonymized exports, local-only AI mode, and audit logs. |

## 24. Open Product Questions

1. Should students see classmates' names by default, or should names be hidden until work is shared in a group or class discussion?
2. Should instructors approve signals before they become visible in the shared class library?
3. Should scenario archetypes be fixed by the product or editable by each instructor?
4. Should the tool integrate with an LMS in MVP, or begin with CSV roster import/export?
5. Should AI usage be visible to students only, instructors only, or both?
6. Should public exports ever be allowed, or should all sharing remain inside the course workspace?
7. Should rubric scores be built into the MVP, or should the MVP focus on participation analytics first?

## 25. Recommended Decisions

Recommended MVP decisions:

- Start with authenticated identity and CSV roster import before full LMS integration.
- Use PESTLE as the default taxonomy, with STEEP as a course setting.
- Require at least one source for every signal and support multiple sources from day one.
- Require at least five signals for final scenario submission.
- Make LLM support optional and instructor-controlled, with local-only and disabled modes.
- Build exports early so instructors can trust the tool even before advanced analytics exist.
- Add relationship maps after core data quality and collaboration workflows are stable.

## 26. Example Student Workflow

1. Student opens the current assignment and sees they need five signals and one scenario.
2. Student adds a signal about AI-assisted weather forecasting.
3. The form asks for title, summary, PESTLE category, source, context, implications, ratings, tags, and uncertainty.
4. Student sees help text explaining the difference between "source publication date" and "signal observed date."
5. Student submits the signal.
6. The system suggests related signals about climate risk, infrastructure, and emergency response.
7. Student adds the signal to a shared collection called "Climate Adaptation and Predictive Systems."
8. A teammate adds a contextual note connecting weather AI, water scarcity, migration, and urban planning.
9. The group creates a trend from seven signals.
10. The group starts a scenario for a 7-15 year time horizon using a "constraint" archetype.
11. The system requires at least five signals before the scenario can be submitted.
12. Students write a future environment, vignette, problem statements, personas, and user journeys.
13. Instructor reviews the scenario traceability panel and contribution dashboard.

## 27. Example Instructor Workflow

1. Instructor creates a course workspace and imports a roster.
2. Instructor creates a signal-scanning assignment requiring five signals per student.
3. Instructor chooses PESTLE mode and adds course-specific tags.
4. Instructor enables class-visible signals after submission.
5. Instructor disables hosted AI but allows a local model endpoint for trend critique.
6. During the assignment, instructor checks participation dashboard.
7. Instructor filters for students with fewer than three submitted signals.
8. Instructor reviews signals with weak source credibility or missing implications.
9. Instructor creates a class discussion collection from the strongest signals.
10. Instructor exports participation and scenario reports at the end of the module.

## 28. Acceptance Criteria Summary

The product is ready for pilot when:

- Students can submit structured, source-backed signals with help text for every field.
- Instructors can see participation by student without relying on free-text names.
- Signals support multiple structured sources.
- Users can search, sort, filter, and view signals in more than one workspace mode.
- Students can create trends from signals.
- Students can create shared collections with contextual notes and contribution history.
- Students can create scenarios from at least five signals.
- Scenarios include future environment, vignette, problem statements, personas, and user journeys.
- Instructors can export signal and participation data.
- LLM features can be disabled, configured for local or hosted providers, and audited.

