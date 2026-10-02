# Habitica Codebase Summary — PM Orientation for the Comeback Screen

**Repo:** https://github.com/HabitRPG/habitica (read at tag `5.50.6`, commit `bce89c6`)
**Read for:** PM scoping a Comeback screen (best-streak stat + 60-second comeback lesson + one-tap streak freeze)
**Caveat:** this is Habitica's open-source web monorepo. The iOS and Android apps live in **separate repos** (`habitica-ios`, `habitica-android`) and are not visible here. Also note the repo's own policy banner: public PRs are paused and AI-generated code is not accepted — treat this as a reference codebase to learn from, not one to ship into.

---

## 1. PM-level tour

### What it does, in one sentence
Habitica turns your real-life habits, daily routines, and to-dos into an RPG: completing tasks earns XP, gold, and pets, and missing your due Dailies costs you HP and breaks your streaks.

### How the codebase is organized

| Path | What it is | Why a PM cares |
|---|---|---|
| `website/common/script/` | **Shared game rules**, used by both server and web client: `cron.js` (date/day-boundary math), `ops/` (scoreTask, buy, rebirth…), `content/` (spells, achievements, quests, login incentives), `libs/` | This is the rulebook. Almost any change to streak or scoring behavior lands here, and it is shared code — a change affects server and client at once. |
| `website/server/` | Node/Express API. `models/` (Mongoose schemas), `controllers/api-v3` + `api-v4` (HTTP routes), `libs/` (cron orchestration, push notifications, spells, preening), `middlewares/` | Where new data fields and endpoints get defined. Two live API versions, both public. |
| `website/client/src/` | Vue 2 SPA. `components/` (by domain: `tasks/`, `achievements/`, `snackbars/`, `header/`), `pages/`, `store/` (Vuex), `router/`, `mixins/` | Where a Comeback *screen* would be built. Note: UI is organized as **modals over a single main page**, not as routed screens. |
| `website/common/locales/` | **46 languages** of JSON copy | Every string you spec is a localization ask. |
| `migrations/` | One-off scripts to backfill user data | Any new field on 2M+ existing users needs one of these, or a safe default. |
| `test/` | `test/common/` (game rules), `test/api/unit/`, `test/api/v3|v4/integration/` | `test/api/unit/libs/cron.test.js` alone is ~2,000 lines. That is a signal, not trivia — see blast radius. |
| `habitica-images/`, `website/raw_sprites/`, `gulp/` | Art assets and build pipeline | Sprite-based art; new illustrations are a real pipeline step. |

### The 3 files to know

1. **`website/server/libs/cron.js`** — the day-boundary engine. This is the moment the app decides "you missed yesterday," docks HP, resets buffs, awards Perfect Day, and increments login incentives. **The Comeback screen's trigger lives at this moment.** Critically: cron is *not* a scheduled background job — it runs on demand when the user's client calls `POST /api/v4/cron` (see `cronWrapper`, and `needsCron` computed in `website/server/libs/user/index.js:29-31`). The user has to show up for the break to be processed.

2. **`website/common/script/ops/scoreTask.js`** — task scoring and **the actual line where a streak dies**: `if (!user.stats.buffs.streaks || task.challenge.id || task.group.id) task.streak = 0;` (`:310`, in the `cron` branch). Also holds the streak gold bonus (`:141-150`) and the 21-day streak achievement (`:338-342`).

3. **`website/client/src/components/notifications.vue`** (~850 lines) — the client-side orchestrator for everything shown after a day rolls over: it decides when to run cron, shows the "Record Yesterday's Activity" modal, and maps server notification types to modals and snackbars. **A Comeback screen has to get in line here**, and this file is already the app's most crowded decision point.

### Key data models and what they tell you

**`website/server/models/task.js` — `DailySchema` (`:378-412`)**
```
streak: Number (default 0)      // current streak only — there is no best/longest streak stored
history: Array                  // {date, value, isDue, completed} — preened over time
isDue, nextDue                  // precomputed scheduling
yesterDaily: Boolean            // opt a task into the "did you do this yesterday?" flow
frequency / everyX / repeat / daysOfMonth / weeksOfMonth
```
**Product read:** streaks are **per-task, not per-user**. Habitica has no single "your streak" number. That is a structural decision the Comeback screen has to take a position on. Also: `history` is aggressively preened for performance (`libs/preening.js`), so you cannot assume you can reconstruct a user's streak history after the fact.

**`website/server/models/user/schema.js`**
```
stats.buffs.streaks: Boolean    // ← a streak freeze ALREADY EXISTS (see below)
stats.buffs.stealth: Number     // Rogue "Stealth": evades N due Dailies entirely
preferences.sleep: Boolean      // the Inn: pauses all damage
preferences.dayStart: 0-23      // user-chosen day boundary (Custom Day Start)
preferences.suppressModals: {levelUp, hatchPet, raisePet, streak}
preferences.pushNotifications: {14 named toggles} + unsubscribeFromAll
achievements.streak: Number     // count of 21-day streaks earned, NOT a streak length
flags.*                         // ~40 booleans: tours, tutorials, recapture email phases
lastCron: Date, flags.cronCount: Number
_ABtests: Mixed                 // an A/B bucket bag exists, but is barely used
```
**Product read:** recovery and forgiveness mechanics are already a designed part of this product, and they are **monetized through the class/skill system** rather than given away. `flags` also tells you this team's pattern for gating one-time experiences: add a boolean, check it client-side.

**`website/server/models/userNotification.js`** — a closed `enum` of ~40 live notification types (`CRON`, `STREAK_ACHIEVEMENT`, `LOGIN_INCENTIVE`, …) that persist on the user and are marked read via `POST /api/v4/notifications/read`. **Product read:** any new server-driven prompt needs a new enum value. This is a cheap, well-worn extension point.

---

## 2. Mapping the Comeback screen to the codebase

### Where it would live

| Piece | Location |
|---|---|
| The screen itself | `website/client/src/components/tasks/comebackModal.vue` — modeled directly on the existing **`yesterdailyModal.vue`**, which is the closest thing that already ships: a post-cron, full-attention, blocking modal about missed Dailies |
| Registration + trigger | `website/client/src/components/notifications.vue` — new branch alongside `runYesterDailies()` / `afterYesterdailies()` (`:594-660`) |
| Break detection | `website/server/libs/cron.js` (the dailies loop, `:215-308`) + `website/common/script/ops/scoreTask.js:310` where `task.streak = 0` happens |
| New notification type | `website/server/models/userNotification.js` — e.g. `STREAK_BROKEN` |
| New user/task fields | `website/server/models/task.js` (`DailySchema`) and/or `website/server/models/user/schema.js` |
| Freeze action endpoint | `website/server/controllers/api-v4/user/` (v4 is the newer surface; v3 stays for third-party API clients) |
| Client state | `website/client/src/store/actions/tasks.js`, `user.js` |
| Copy | `website/common/locales/en/*.json`, then 45 other locales |
| Lesson content | **No home.** There is no lesson/content-delivery system anywhere in this codebase. `content/` is game data (spells, eggs, quests), not learning material. |

### What it touches or depends on

**Streaks**
- `task.streak` is per-Daily, incremented in `scoreTask` on check-off, zeroed in the cron branch.
- **A streak freeze already exists three ways, and you should not ship a fourth without a decision:**
  1. **Chilling Frost** — Mage skill, level 14, sets `user.stats.buffs.streaks = true`, which makes `scoreTask` skip the reset (`content/spells.js:106-115`). It is single-use per day (throws `spellAlreadyCast`) and is **wiped by cron** (`libs/cron.js:341,350`), so it protects exactly one night.
  2. **Stealth** — Rogue skill, `buffs.stealth` decrements per due Daily and evades the miss entirely (`libs/cron.js:245-249`).
  3. **The Inn** — `preferences.sleep = true` suppresses all damage.
  - Note the carve-out: Chilling Frost does **not** protect challenge or group tasks (`scoreTask.js:310`). Your one-tap freeze inherits that question.

**Tasks / cron**
- Cron is lazy and client-triggered, guarded by `_cronSignature` against double-runs, and wrapped in a Mongo transaction.
- It honors `preferences.dayStart` and timezone drift (`daysUserHasMissed`, `models/user/methods.js:374`). "Broke a streak" is therefore not a server-clock event — it is a per-user, timezone-dependent event that fires whenever they next open the app.
- The existing yesterdaily modal already **interposes before damage is applied** — the client asks "did you do these yesterday?", scores retroactively, *then* calls cron. Your Comeback screen sits downstream of that and must not fight it.

**Notifications**
- In-app: `user.notifications[]` + the modal/snackbar dispatch in `notifications.vue`.
- Push: `website/server/libs/pushNotifications.js` (APNs + Firebase), `pushDevices[]` on the user, and **14 named opt-out toggles** under `preferences.pushNotifications`. There is currently **no push category for streaks or re-engagement** — re-engagement is done over email (`flags.recaptureEmailsPhase`, `weeklyRecapEmailsPhase`).

### Blast radius

Ranked by what actually hurts:

1. **HP and character damage.** Streak reset and HP loss are the same code path (`scoreTask` cron branch). A freeze bug that skips too much also skips damage, or worse, applies it twice. In this product, HP loss causes **death and level loss** — an irreversible, support-ticket-generating outcome.
2. **Cron itself.** Everything day-boundary lives in one function: login incentives, Perfect Day, buffs, MP regen, quest boss damage, gold-to-gems cap, subscription perks, todo decay. A crash mid-cron in the modal flow means the user's day never rolls over, and because cron is client-triggered they can end up stuck. The ~2,000-line `cron.test.js` is the team's scar tissue here.
3. **Two-sided timezone math.** `common/script/cron.js` `shouldDo()` runs on both server and client. If your "did they break a streak?" check is computed client-side (like the yesterdaily check at `notifications.vue:611-640`) and diverges from the server, users see a Comeback screen for a streak they didn't break — or miss one they did.
4. **Modal collision.** The post-cron moment is already contested: yesterdaily, level-up, streak achievement, login incentive, onboarding-complete, drop caps. `notifications.vue` already has hand-rolled dedupe hacks (`lastShownStreakCount`, the 3-minute `lastCron` check at `:826`). Adding a blocking screen here without deciding precedence produces a modal pile-up on exactly the day a user is most fragile.
5. **The public API.** v3 and v4 are documented, rate-limited, and used by third-party tools. New fields on tasks and users appear in `GET /user` responses; the `noSet` lists in `models/task.js:160` and `libs/user/index.js` control what clients may write.
6. **Mobile.** iOS and Android are separate codebases against the same API. Anything you add server-side either ships to three clients or degrades silently on two of them.
7. **Challenge and group tasks.** Streaks on these behave differently and are excluded from freeze. Get this wrong and you break shared-accountability features.

---

## 3. What this changes about your spec

### Data that does not exist yet

| Need | Status | Implication |
|---|---|---|
| **Best / longest streak** | **Does not exist.** Only `task.streak` (current) and `achievements.streak` (count of 21-day milestones). `grep` for `bestStreak`/`longestStreak` returns nothing. | You cannot show "your best streak was 34 days" to existing users without either a new `bestStreak` field going forward (accurate only after launch) or a migration over `task.history`, which has been preened. **Decide now:** ship a stat that's only correct for new streaks, or use `achievements.streak` as a proxy, or cut the stat. |
| **A per-user streak** | Does not exist. Streaks are per-Daily. | "You broke your streak" is ambiguous. Longest active Daily? Count of streaks lost last night? This is a product definition, not an implementation detail. |
| **A durable streak-freeze entitlement** | Partially exists. `buffs.streaks` is a one-night boolean wiped by cron, earned via a level-14 Mage skill with an MP cost. No balance, no inventory, no earn/purchase loop for a freeze **item**. | A "one-tap freeze" needs new state: how many do I have, how do I get more, does it cost anything, can I use it retroactively. |
| **Retroactive freeze** | Does not exist at all. `buffs.streaks` must be set **before** cron runs. | A Comeback screen shown *after* the break, offering to undo it, is a genuinely new capability — restoring `task.streak` from a value the system already overwrote to 0. Either persist the pre-break value or set the freeze before cron. |
| **Lesson content** | No content system, no lesson model, no progress tracking. | The "60-second comeback lesson" has no foundation here. Either it's static localized copy (cheap, 46 locales) or it's a new content subsystem (large, separate effort). |
| **Streak push category** | Not in `preferences.pushNotifications`. | New toggle + respecting `unsubscribeFromAll`. |
| **Impression / suppression flag** | Pattern exists (`flags.*`, `preferences.suppressModals.*`) but no field for this. | Cheap to add; say which pattern you want. |
| **Event analytics** | Thin. `libs/localAnalytics.js` only tracks registration and subscription events. `_ABtests` exists but is nearly unused. | **You cannot currently measure whether this feature works.** Instrumentation is in-scope work, not a follow-up. |

### Existing constraints to call out in the ticket

- **Cron is client-triggered, not scheduled.** Break detection only happens when the user opens the app. A break that occurred five days ago surfaces today. Your empty-state and copy have to survive "you broke your streak" arriving a week late.
- **`preferences.dayStart` (0-23) plus timezone drift** define the day boundary, per user. There is no global midnight.
- **Multi-day absences collapse to one day.** `multiDaysCountAsOneDay = true` in `libs/cron.js:185` — a 9-day absence is scored as one missed day. Deliberate mercy already in the product; your feature should be consistent with it.
- **The yesterdaily flow already owns this moment** and lets users retroactively check off yesterday's Dailies *before* damage. Some "broken streaks" get repaired by the user before your screen would ever fire. Sequence matters.
- **Forgiveness is currently earned, not given** — class skills, MP costs, level gates. A free one-tap freeze is a change in the product's economy and its core tension, not just a new screen.
- **46 locales**, and copy ships through `website/common/locales/`.
- **Two live API versions + two separate mobile repos.**
- **`buffs.streaks` is reset unconditionally by cron**, including on Perfect Days — any longer-lived freeze needs new state, not this field.
- **Sprite-based art pipeline** (`gulp sprites:compile`) — new illustration is a build step.

### The one question to answer before kickoff

**"When a user taps 'freeze my streak' on the Comeback screen, are we preventing a future break or reversing one that already happened — and for which streak?"**

Everything hinges on this:
- *Preventing* = set `buffs.streaks` before cron runs. Small, reuses the existing mechanic, but means the screen must appear **before** the break is processed, which changes the trigger from "streak broken" to "streak at risk" — a different feature.
- *Reversing* = restore `task.streak` after cron already zeroed it. Requires new persisted state (the pre-break value), a new endpoint, a new audit story, and a decision on how far back a user can reach.
- *And which streak* — Habitica has no single user streak. One Daily? All Dailies broken last night? The longest one? Engineering cannot estimate without this.

Answer that and the rest of the spec (best-streak stat definition, lesson placement, modal precedence, instrumentation) follows. Go in without it and the kickoff becomes the design meeting.

---

## Quick reference

| Question | File |
|---|---|
| Where does a streak die? | `website/common/script/ops/scoreTask.js:310` |
| Where does the day roll over? | `website/server/libs/cron.js` (`cron`, `cronWrapper`) |
| How is "a day" defined per user? | `website/common/script/cron.js` (`startOfDay`, `shouldDo`), `models/user/methods.js:374` |
| What is the existing streak freeze? | `website/common/script/content/spells.js:106-115` (Chilling Frost) |
| Closest existing analogue to a Comeback screen | `website/client/src/components/tasks/yesterdailyModal.vue` |
| Who decides which modal shows after cron? | `website/client/src/components/notifications.vue:594-660` |
| Streak data shape | `website/server/models/task.js:378-412` (`DailySchema`) |
| Recovery/forgiveness state | `website/server/models/user/schema.js:691-702` (`stats.buffs`) |
| Notification types | `website/server/models/userNotification.js:7-90` |
| Push plumbing + opt-outs | `website/server/libs/pushNotifications.js`, `schema.js:613-628` |
