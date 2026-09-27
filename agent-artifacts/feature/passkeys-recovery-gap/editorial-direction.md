# Editorial direction
These are the exact standing directions for this article. Later sections specialize earlier ones; the orchestrator's commission adds article-specific decisions without rewriting them.

Checkout revision: `e53ea8cf251a4e1b1d0249e1d0594dd60864b89b`

## 1. House editorial standard

Source: `spec/editorial.md`

# Editorial standard

Every article meets this standard, whatever its template and whatever the press.

The first section is about writing, and it applies to everything. The second is
about what this paper does, and an owner may move any of it in
`press/editorial.md` except correctness. Register, formality, and how hard to
press a judgment are an owner's to set in `press/editorial.md` and in the
article's voice guide. Nothing here sets them.

`spec/slop.md` lists the prose failures, and they apply at every register. An
owner may allow one of them in a template or a press, and has to say which one
and where.

Nothing here covers trivia. There is no paper-wide position on the Oxford comma.
Be consistent within a piece.

## The principles of great writing

**It is clear.** Clear writing is easy to understand, and that has little to do
with how hard the words are. Use the exact word. An approximate one leaves a
reader guessing which of several things you meant, and a precise one settles it.
The subject can be difficult without the sentence being difficult. Use one word
for each idea and keep using it. Reach for a synonym and whoever reads it looks
for a second idea.

**It teaches.** Someone who finishes the piece can reason about the subject and
not only recall it. Order it so each part can be used where it appears. Define a
technical term where it first appears and assume the rest. Carry an abstract
claim down to an instance before moving on. Order the piece so each section uses
what you set up earlier.

**It stands on its own.** Someone arriving from a link has read nothing else.
Introduce every term and event inside the article.

**It does original work.** Do something with the sources that the sources did
not do. Say in one sentence what that was. If you cannot write that sentence,
the article is not finished.

## The paper's principles

Correctness is the one nothing loosens. An owner who wants a different bar on
the others says so in `press/editorial.md`.

**It is correct.** Cite what could be doubted and the claims without which the
piece does not work. Common ground needs no citation. Open the source and find
the passage before citing it, and record the section, page or paragraph, so a
reader lands on the words and not on a homepage. Cite the document that made a
claim ahead of any article about it, and where a figure is disputed cite the
document that owns it. If you cannot source a claim, cut it or state the
uncertainty plainly. Never fabricate, pad or decorate a citation.

**It says what the reporting supports.** Say it without hedging. Withholding a
conclusion you can show is its own distortion. Where the reporting does not
reach one, say that, and separate what is established from what is judged. Show
the reasoning from the evidence to the conclusion. Never write that someone
hinted, implied or signalled, which attributes your guess to them.

**It is fair to a view it disagrees with.** State a view in the words of someone
who holds it before taking it apart. Beating a weak version of the opposition
tests nothing.

**It is written for more than one person.** Use the profile in
`press/editorial.md` to decide what to cover and what background to assume, then
write each piece for the audience around that profile. Where the profile is a
new parent, write articles any parent could be handed. Narrow a series to one
person only where `press/editorial.md` or the series prompt says to.

## Numbers

Give the figure and not the magnitude. Give the range a source gives and no more
precision than that. Where nobody could scale a figure alone, put it beside one
they already hold. Say plainly what nobody knows.

## Punctuation

Use the plainest mark that works. Where two marks would both work, use the
plainer one, and where you are unsure use the period.

- **Period.** Two thoughts are two sentences. In most drafts, a period belongs
  where the em-dash, the semicolon or the colon is.
- **Comma.** Joins inside one thought, and sets off a short aside. Two
  independent clauses joined by a comma alone are two sentences.
- **Colon.** Introduces a list, a definition, or the payoff. The clause in front
  of it stands on its own.
- **Semicolon.** Rare. Two independent clauses close enough that a period would
  be too much between them. Do not chain them and do not patch a comma splice
  with one.
- **Em-dash.** A real interruption or a sharp aside. When you delete one, a
  period is usually what belongs there. `spec/banned-terms.yaml` sets the count.
- **Parentheses.** A true aside. Take them out and the sentence still says what
  it said. If you need what is inside them, fold it back in.

An owner may extend this section and may not loosen it.

## Form

Each template's identity specifies its own form: paragraph length, how the dek
reads, how the piece closes. End on the conclusion you built. Skip the generic
moral.

Read the published library for what a series has covered and what not to repeat.
Do not read it for the form. An older piece was written to the format of its
time, and if you copy that structure forward you bring back a section somebody
retired.

### Literal strings

Use inline `<code>` only where somebody must preserve a string's exact spelling:
something they could type, paste, execute or match character for character.
Ordinary terms, product names and model names do not take it, and neither does a
literal you have already established. Where several tokens need comparison, give
them a table or a code listing.

## Charts

Use a chart where a trend or a comparison is the point. Charts are PNGs rendered
from the committed `chart-N.py` script beside the article (`spec/charts.md`).
Label the axes, note a non-linear scale, and cite the data source in the
caption.

## One exception

If following a rule in this file would give you a sentence you would not say
aloud, break the rule. Correctness, teaching and sourcing stay.

## 2. Slop standard

Source: `spec/slop.md`

# Slop

Slop is writing that reads as machine-written. Whoever recognizes it stops
trusting the reporting, which costs the paper more than a dull sentence does.
The editor cuts it on every article, against this file.

Cutting slop does not mean making the prose dry. A joke, a fragment or a short
quotable line is not slop. Do not cut them to stay safe.

## The test

Replace every subject-specific noun in the sentence with a placeholder, then
read what is left.

If the sentence was reporting something, what is left makes no sense, because
the nouns carried it. If it still makes sense, the writer filled in a familiar
pattern and the subject was interchangeable. Cut the second kind.

"The tension here is real, and it is structural" reduces to "the X here is real,
and it is Y", which anyone could write about anything. "The board met twice in
March and adjourned without a vote" reduces to nothing at all.

Run the test on any sentence that sounds like the best line in its paragraph. A
joke that depends on the nouns passes, which is why applying the test does not
flatten a piece.

## Where it sits

Slop is most common at the edges: the first and last sentence of a paragraph, of
a section, and of the article. A writer with nothing left to add writes a
sentence there anyway. Test every edge even when the middles read clean, and
test the article's last sentence most carefully, since it is the position with
the least left to say.

An opening sentence has no earlier sentence to introduce its nouns. The
dangling-referent rule: a definite noun phrase whose referent appears only in
the briefing reads as complete to everyone who wrote the brief, and as a
dangling reference to whoever arrived from a link.

Delete. Do not repair. Rewriting gives you a slop sentence that sounds better,
because the fault is that the writer had nothing to say there. Write a
replacement only when something real was waiting to be said.

## Figures of speech

A figure of speech is allowed when it makes something understood, and never when
it makes something sound important. Rare either way. An agent reaches for these
to add weight. That is the case to cut.

- **Abstractions acting.** "Writing goes unclear", "the argument rests on", "the
  trend demands". Nothing there can do anything. Say who acted, or use the verb
  that states what the thing is. A document is the exception: a filing says what
  is printed in it.
- **Metaphor.** "The pond of prose", "a headwind for the sector". Keep one where
  the comparison explains something a plain sentence cannot. Cut one that
  decorates.
- **Antithesis.** "X is not Y, it is Z", "not just X but Y", "X rather than Y".
  Check every draft for it. It stays only where the misconception it corrects is
  real and stated in the piece.
- **Built to be quoted.** "That's the whole point", "here's the kicker", "the
  catch is". Write one of these and you are grading your own argument. The next
  sentence should continue it.
- **The inflated copula.** "Serves as", "stands as", "represents". Also the
  trailing clause that supplies an opinion in the grammar of a finding:
  "highlighting", "underscoring", "cementing". Write "is", or write the finding.
- **Tricolon.** Three items where the material has one or five. You picked three
  for the rhythm.
- **Anaphora.** Consecutive sentences opening the same way. Repeat once to carry
  an argument. Three times and you are writing to a cadence.
- **The rhetorical question.** "So what does this mean for the industry?" Ask
  one only where the answer that follows is the piece's own work.

Analogy is permitted without qualification. An analogy exists to make something
understood, and whoever reads it either follows it or does not.

## What else it looks like

These failures recur. They are not a complete list, and a sentence matching none
of them still goes if it fails the test above.

- **Empty conclusions.** A sentence that sounds like a finding and states
  nothing the article established: an idea for a subject, a linking verb, and an
  assessment. "That limit is itself part of the design" and "the difficulty here
  should not be understated" state nothing anyone could check.
- **Performed carefulness.** The writer advertising their judgment where a
  qualification belongs. "The honest position is" and "what the evidence has
  established" rate the writer's own care. "The confidence on both sides runs
  ahead of the evidence" rates the people arguing and says nothing about the
  argument. A real qualification states something checkable: what went
  unmeasured, who disagrees, what would settle it. Keep those and cut the
  display.
- **Fluff.** Filler openings ("In today's fast-paced world"), empty connectives,
  throat-clearing ("As you might know"), and openers that lecture: Note,
  Consider, Imagine.
- **Puffery.** Ordinary facts described as significant, pivotal, transformative,
  a testament, a turning point, or part of a broader movement. State what
  happened and give the figures that show how big it was.
- **Reaching for the generic.** The median phrasing where a specific one exists:
  the drug's name, not "a treatment". 40 nanometers, not "tiny". Say what you
  mean and commit where the evidence lets you.
- **Vague attribution.** "Experts argue", "observers note", "many believe". Say
  who, or cut the claim.
- **Self-reference.** The piece never narrates itself or its newsroom ("this
  dossier", "what follows") and never gestures at a hypothetical reader. Citing
  or linking another article the paper published is reporting, not
  self-reference.
- **Formula.** A closer, section opener, dek or heading built to the same
  pattern as the last article's. A house catchphrase is the same failure. One
  article cannot show this, so the editor compares against the recent record.

Punctuation tells belong to the punctuation section of `spec/editorial.md`, and
the counted lexical tells to `spec/banned-terms.yaml`, which a press extends in
`press/banned-terms.yaml` and the proof counts against the merged list. Both
apply here too. When a count runs over, rewrite the sentence. Substituting a
synonym keeps the same vagueness, and repunctuating an em-dash keeps the fluff.
Delete first, then rewrite what remains.

An owner may allow one of these failures in a template or a press.
`spec/editorial.md` sets the terms. The example lesson template has that
allowance for its two bookend cards, so the editor leaves them addressing the
reader and judges them like any other sentence. A sentence written in an allowed
form still has to say something.

## Who this binds

Every role, and every file a role writes. The editor cuts slop out of a draft,
and whoever writes the next article reads the commission, the brief, the
evidence record, the voice guide and the editorial review, and picks up the
register they are written in. Hold your own artifact to this standard before you
hand it on.

## 3. Headline standard

Source: `spec/headlines.md`

# Headlines, deks, and section headings

This is the standard for the three lines a reader meets first. The prose rules
of `spec/editorial.md` and `spec/slop.md` apply here word for word.

Hold all three to one test: write a line you can defend from what the piece
establishes. Every tell below is a way of avoiding that.

## The headline

Subject, verb, and the surprise in the first words. Put the concrete news ahead
of every qualifier, because a scanning reader may not get past it.

- **State the finding, and say who did it.** "Steve Ballmer was an underrated
  CEO" (Dan Luu) and "Ghostty Is Now Non-Profit" (Mitchell Hashimoto) are claims
  each writer defends. Prefer a specific record to a scope: "A decade of major
  cache incidents at Twitter" (Luu again) tells you exactly what is in it.
- **Use a fresh verb, in the present tense for events.** The classic headline
  pair: "Students applaud later start times" reports the event from the side
  that felt it. "Officials approve schedule change" reports the same event as
  paperwork.
- **Put a number in only where the number is the surprise.** "Building a World
  Map with only 500 bytes" (Simon Willison).
- **Ask a question only where the piece answers it.** "Why is DNS still hard to
  learn?" (Julia Evans) is honest because the post contains the answer.
  Betteridge's law covers the other kind: a headline ending in a question mark,
  so that nobody has to stand behind a claim.
- **The colon subtitle is a machine tell.** "X: How Y Changed Z" and "Company:
  The Adjective Noun and the Adjective Noun" are templates that fit any topic.
  Keep a colon only where you need both halves, as in "git branches: intuition &
  reality" (Evans). Where the right half is decoration, cut the colon and write
  the claim.
- **A triad of paired adjectives ("Faster Models, Firmer Rules, Tighter Supply")
  only sounds comprehensive.** Pick the one development that matters most and
  say what happened to it. Put the other two in the dek or the body.
- **Anchor wit in the story's own nouns, with a plain dek beside it.** The
  Economist headlined a meat-producer merger "A steak in the market" and could
  afford to, because the dek under it stated the argument plainly. Write the dek
  anyway.

All of that at once. A writer who found two chip CEOs reading the same market
data and reaching opposite conclusions could headline it "The Chip Curtain:
Slowdown or Surrender?" and hedge twice, once with the borrowed metaphor and
once with the question. You found something better, so say it: "Two CEOs read
the same chip data and reach opposite conclusions."

## The dek

Put in the dek what the headline left out, and never restate the headline.
Commit the headline to the surprise, then give the dek the who, the what, and
the one detail that makes the piece unmistakable for any other. "The very modern
corporate tale of what happens when a top executive at a $6 billion public
company can't stop tweeting" works because of the dollar figure and the verb.
"The fascinating tale of a San Francisco-based executive" identifies nothing.
One lean sentence, a stance and not a topic, and no detail that pulls attention
from the thesis.

The negative-parallelism reflex is banned in body prose (`spec/slop.md`) and the
dek gets no exemption. Three dek molds are built from it: the semicolon reversal
("X did A; Y refuses B"), the suspended question ("...and the real question is
whether"), and the comma triad, three clauses joined by commas and closed with
"and" ("The trial cut the rate from 14 in 100 to 2, the general-population
evidence is thinner, and the benefit depends on sustained feeding"). Cut them on
sight. Even a good mold looks stamped once it recurs, so check the recent
library's deks before settling on one.

## Section headings

Each heading is a step of the argument, in the piece's own nouns. Somebody
skimming only the headings should be able to reconstruct the argument and its
order. A heading that would fit any article on any subject is scaffolding, and
the scaffolding slots ("Background", "Implications", "The Road Ahead", "Key
Takeaways") are the machine tell. Keep the `data-nb-section` label short,
concrete, and the same as its heading. A fixed template heading ("Sources") is
furniture and exempt. Everything you write is held to this standard.

Headings repeat the same way deks do. Join two clauses with a comma and "and" in
several of them ("The scale, and what it is compounding against") and the piece
looks stamped however sharp each line is. Build them differently from each
other, and check the recent library's headings as you checked its deks.

## 4. Press editorial direction

Source: `press/editorial.md`

# Voice

The reader is a professional who reads widely and does not need a field
explained from the beginning. Write every piece for the people around that
reader, never for one person.

The register is a serious daily newspaper. Report first. State a judgment once
the reporting has earned it, and say where the record stops and the paper's
own reading begins.

Assume the headline has been seen, and spend the words on what it left out.

## 5. Template identity

Source: `templates/article/identity.md`

# article

An article does original analysis.

Outline the article's reasoning before naming its sections. Remove any section
whose deletion leaves that reasoning unchanged. Do not close on a reading list
or a pointer away.

Name the flex sections for the argument this piece makes, not a standard
outline. `templates/FURNITURE.md` states when to reach for a piece.

## 6. Series direction

Source: `press/series/feature/prompt.md`

# Feature

One piece a day on technology, science, and the businesses built on them, in
whatever form the material deserves. Some days the subject is the week's most
consequential development, reported past the headline. Other days it is a
question nobody is asking this week that is worth understanding anyway. Do not
let the news set every day's subject.

Use `paper` when the subject is one research paper and the piece reports and
weighs it. Use `article` otherwise.

Choose the subject by what will still be useful in a month.
