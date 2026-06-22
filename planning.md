# TakeMeter — Project Planning

## Community

**Chosen community:** YouTube comments on BLACKPINK — "DDU-DU DDU-DU" M/V  
**Video URL:** https://www.youtube.com/watch?v=IHNzOHi8sJs  
**Video ID:** `IHNzOHi8sJs`

**Why this community:** <!-- 2–3 sentences. What makes discourse here varied and text-heavy? Why is discourse quality a real distinction people in this community care about? -->
Music videos have always provided a space with a diverse and polarized discourse. Some people provide opinions, some spam, some people blindly criticize, and some blindly praise. Through labeling these texts, we can filter out spam messsages and get a data-driven understanding of how the public received a certain music video. 

To choose a representative and highly popular community, I chose the Youtube comments under Blackpink's music video "Ddu-du-ddu-du".

---

## Label Taxonomy

### Label 1: `Fan_war`
Any comments that involve criticism towards the artist with no real proof or while praising another.

e.g. "BLACKPINK SHOULD DISBAND TWICE IS GOOD"

### Label 2: `Stream`
Any comments that talk about streaming this music video or encourages other fans to 
e.g. Please stream udududud for 1.5B come on lets googgo

### Label 3: `Hype`
Any comments that praise the artist with no substantial reasoning.

e.g. "2019 IS GONNA BE BLACKPINK'S YEAR
Where are you at BLINKS?"

### Label 4: `Genuine_comment`
Any comments that involve substantial reasoning for a particular opinion, or anything that doesn't fit into the above 3 category (still organic discussion)

e.g. Im just too much obsessed with this song the tuning, the rap, the dance, the vocals
---

## Hard Edge Cases

**Anticipated ambiguous post type:** 
**Which labels could it belong to:** 

**Decision rule:** 

**At least 3 specific examples from annotation:**

---

## Data Collection Plan

**Source:** YouTube comments on BLACKPINK "DDU-DU DDU-DU" (video ID: `IHNzOHi8sJs`)

**Collection method:** `scrape_comments.py` — uses `youtube-comment-downloader` (no API key required), sorted by top/popular, filters out pure emoji comments, links, and comments under 15 or over 500 characters. Outputs `raw_comments.csv`.


---

## Evaluation Metrics

**Metrics I will use:**
- Overall accuracy — gives a single comparable number between the baseline and fine-tuned model, useful for the headline comparison
- Per-class F1 — because the three classes are not equally hard; a model could score 80% accuracy by mostly predicting `hype` and `spam` while completely missing `opinion`, which F1 per class would expose
- Confusion matrix — to see which specific label pairs are being confused, which reveals whether errors are random or systematic (e.g., model conflating `hype` with `opinion`)

**Why accuracy alone isn't sufficient for this task:** Opinion is the least frequent class at 22%. A model that always predicts `hype` or `spam` could achieve ~78% accuracy without ever correctly identifying a single opinion comment. Per-class F1 catches this failure mode; accuracy masks it.

---

## Definition of Success

**Minimum acceptable performance:** All per-class F1 ≥ 0.60 and the fine-tuned model beats the zero-shot baseline by at least 10 percentage points in overall accuracy.

**What would make this classifier genuinely useful in practice:** F1 ≥ 0.75 on all three classes, especially `opinion` — since the real-world use case is surfacing genuine opinions from a flood of hype and spam, a high-recall opinion classifier is what actually creates value. Missing an opinion (low recall) is worse than flagging a hype comment as opinion (low precision), so recall on `opinion` is the metric that matters most for deployment.

--
## Baseline

I was able to reach a baseline performance of 60% accuracy based on the 50 test cases. 

🎯 Baseline accuracy: 0.600  (evaluated on 50/50 parseable responses)

Per-class metrics (baseline):
              precision    recall  f1-score   support

        hype       0.50      0.75      0.60        20
        spam       0.78      0.35      0.48        20
     opinion       0.73      0.80      0.76        10

    accuracy                           0.60        50
   macro avg       0.67      0.63      0.61        50
weighted avg       0.66      0.60      0.59        50

Investingating further, I found that the main problem lies within the model categorizing spam as hype.
---

## AI Tool Plan

### Label stress-testing
Used Claude (claude-sonnet-4-6) to generate boundary cases before annotation by providing the initial 5-label taxonomy (opinion, hype, spam, nostalgia, criticism) and asking it to produce posts that sit at the boundary between two labels. This surfaced 6 hard cases (e.g., hype vs opinion, spam vs nostalgia fusion) that sharpened the decision rules before labeling began. As a result of stress-testing, nostalgia was merged into spam and criticism was merged into opinion, collapsing the taxonomy from 5 to 3 labels.

### Annotation assistance
I used Claude to label all 599 comments in `raw_comments.csv` by reading each comment and applying the taxonomy decision rules. Every label was assigned with an explicit rationale recorded in the `notes` column of `dataset.csv`. Then I read through all the comments and corrected ones that didn't make sense. 

### Failure analysis
After fine-tuning, will paste the full list of misclassified test examples into Claude and ask: "What common patterns do you see across these wrong predictions — length, tone, topic, label pair confused?" Will then manually re-read each flagged example to verify whether the pattern holds or is a hallucination. Findings go into the evaluation report's wrong-prediction analysis section.

---

## Stretch Features *(update before starting each)*

- [ ] Inter-annotator reliability
- [ ] Confidence calibration
- [ ] Error pattern analysis
- [ ] Deployed interface

**Notes on stretch features:**
<!-- Add a subsection here before starting each one. -->
