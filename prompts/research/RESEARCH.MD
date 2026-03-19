## Key Product Clarifications

The following behaviors are core to TutEditor and should shape both product design and system architecture.

### 1. User-declared task context comes first

Before or during a session, the user should explicitly outline what they are trying to do.

Examples:
- “I am solving a coding exercise on binary search.”
- “I am implementing logistic regression from scratch.”
- “I am debugging a PyTorch training loop.”
- “I am building a small ML pipeline with scikit-learn.”
- “I am trying to understand recursion by implementing merge sort.”

This declared context is critical because TutEditor should not interpret code in a vacuum. It should use the user’s stated goal to interpret:
- current code
- recent edits
- likely intent
- whether the user is progressing correctly
- what the next logical step should be

This means TutEditor is not only “editor-aware”; it is also **goal-aware**.

#### Product implication
The app should include a visible **Task Context panel** at the start of a session or pinned beside the editor.

Possible fields:
- what are you trying to build / solve?
- what language are you using?
- is this a coding exercise, project feature, debugging task, or ML implementation?
- what kind of help do you want by default? (hint-first, conceptual, structural, etc.)

#### System implication
Every tutoring request should include:
- user-declared task context
- current code snapshot
- recent edits
- optional runtime / lint / test feedback
- user’s side conversation history relevant to this task

Without this, the tutor may misread a partially written implementation as “wrong” when it is simply unfinished.

---

### 2. Parallel side conversations are a core feature

The user should be able to have parallel conversations with TutEditor beside the coding workspace.

These are not just generic chats. They are task-adjacent tutoring threads.

Examples:
- “Explain what I’m trying to do here.”
- “What does this error mean?”
- “What is the theory behind batch normalization?”
- “Compare two ways I could structure this solution.”
- “Why is my current approach likely to fail?”
- “What should I test next?”

These side conversations should coexist with the editor and should help the user think without disrupting the main coding flow.

#### Why this matters
In real learning, users do not only need inline hints. They also need:
- conceptual clarification
- debugging interpretation
- decomposition help
- comparison of approaches
- reflective explanation

So TutEditor should support both:
- **editor-grounded hinting**
- **parallel tutoring conversations**

#### Product implication
UI should likely have:
- a main editor area
- a tutoring sidebar
- multiple conversation threads or tabs
- the ability to keep one thread for debugging, another for theory, another for planning

These threads should remain linked to the same declared task context unless the user changes it.

#### System implication
Conversation threads should be scoped to a session and optionally tagged by type:
- hinting
- debugging
- theory
- planning
- review

The system should know that the threads are related, but it should not blindly merge all context every time. Only relevant thread context should be included in each tutoring call.

---

### 3. Tutoring should be user-triggered, not constantly running

TutEditor should not continuously monitor and respond every few seconds.

Instead, the user should explicitly trigger tutoring when needed.

Primary trigger example:
- **Hint / I’m getting stuck**

When the user clicks that button, TutEditor should:
1. read the current task context
2. inspect the current editor state
3. inspect recent edits
4. inspect any runtime / lint / test errors if available
5. generate a small nudge:
   - what the user has already done
   - what seems to be the next logical step
   - what assumption may need checking

This preserves focus and avoids noisy over-intervention.

#### Why this matters
If TutEditor reacts constantly, it becomes:
- distracting
- expensive
- overly eager
- more like surveillance than support

The system should feel like a skilled tutor who speaks when asked, not a backseat driver.

#### Product implication
Main call-to-action buttons may include:
- Hint / I’m getting stuck
- Explain this error
- Review my approach
- What should I do next?
- Give me a stronger hint
- Reveal more

The first and most important is the stuck-triggered hint button.

#### System implication
Model inference should be event-driven, not continuous.
A tutoring request should fire only on:
- explicit user click
- optional run/test event if the user asks for analysis
- optional explicit thread message submission

Do not build the first version around automatic inference on every keystroke.

---

## Refined Core Product Loop

The essential TutEditor loop should now be defined as:

1. user declares what they are trying to do
2. user writes code in the editor
3. user optionally chats in parallel side threads
4. user clicks **Hint / I’m getting stuck**
5. system reads:
   - declared task context
   - current code
   - recent work
   - relevant errors
6. TutEditor responds with:
   - what the user has already done
   - what the likely next step is
   - a small pedagogical nudge, not a full solution

This loop is more important than advanced autonomy, proactive interruption, or agentic orchestration in the MVP.

---

## Updated MVP Requirements

The MVP should include the following specific capabilities:

### Required
- task context input before or during the session
- browser-based code editor
- sidebar with tutoring conversations
- support for parallel side conversations
- explicit **Hint / I’m getting stuck** trigger
- tutoring response grounded in:
  - task context
  - current editor snapshot
  - recent work
- response style focused on nudging, not solving

### Not required for MVP
- continuous background monitoring
- automatic intervention every few seconds
- autonomous task completion
- full project-wide agent reasoning
- proactive interruption without user request

---

## Additional Conceptual Data Model

### TaskContext
- id
- session_id
- title
- description
- task_type
- language
- desired_help_style
- created_at
- updated_at

Example `task_type` values:
- coding_exercise
- debugging
- ml_implementation
- model_training
- data_pipeline
- algorithm_practice
- refactor
- concept_learning

### ConversationThread
- id
- session_id
- title
- thread_type
- linked_task_context_id
- created_at

Example `thread_type` values:
- general
- hinting
- debugging
- theory
- planning
- reflection

### HintRequest
- id
- session_id
- task_context_id
- snapshot_id
- triggering_message
- request_type
- created_at

Example `request_type` values:
- stuck
- next_step
- explain_error
- review_approach
- stronger_hint

---

## Updated UX Thesis

TutEditor is not a constantly talking AI.
It is a **goal-aware tutoring workspace** where:

- the user states what they are trying to do
- the user writes code
- the user can think out loud in side conversations
- the tutor intervenes when explicitly invited
- the intervention is small, grounded, and pedagogically useful

That interaction model is a major part of the product’s identity.