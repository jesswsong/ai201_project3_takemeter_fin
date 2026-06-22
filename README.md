# TakeMeter — Discourse Quality Classifier

> AI201 Project 3 | Jessica Song

---

## Community

**Chosen community:** YouTube comments on BLACKPINK — "DDU-DU DDU-DU" M/V  
**Video URL:** https://www.youtube.com/watch?v=IHNzOHi8sJs  

**Why this community:** <!-- 2–3 sentences. What makes discourse here varied and text-heavy? Why is discourse quality a real distinction people in this community care about? -->
Kpop music videos have always provided a space with a diverse and polarized discourse. Some people provide opinions, some spam, some root for Youtube streams, others start fan wars. Through labeling these texts, we can filter out spam messsages and get a data-driven understanding of how the public received a certain music video. 

To choose a representative and highly popular community, I chose the Youtube comments under Blackpink's music video "Ddu-du-ddu-du".

---

## Label Taxonomy

### Label 1: `Fan_war`
Any comments that involve criticism towards the artist with no real proof or while praising another.

e.g. BLACKPINK SHOULD DISBAND TWICE IS GOOD
e.g. @nayeon4191  your own faves is definition of flop


### Label 2: `Stream`
Any comments that talk about streaming this music video or encourages other fans to 
e.g. Please stream udududud for 1.5B come on lets googgo
e.g. Time travelled to inform its no more a billion hon,it’s successfully 2.3B

### Label 3: `Hype`
Any comments that praise the artist with no substantial reasoning.

e.g. 2019 IS GONNA BE BLACKPINK'S YEAR
Where are you at BLINKS?
e.g. @standnowever6625 Yes I love her new song and I’m excited for her to perform in fifa World Cup!

### Label 4: `Genuine_comment`
Any comments that involve substantial reasoning for a particular opinion, or anything that doesn't fit into the above 3 category (still organic discussion)

e.g. Im just too much obsessed with this song the tuning, the rap, the dance, the vocals
e.g. More than that, I can't wait for BP and RVs interaction/moments at awards shows. 😊

---

## Dataset

**Source:** YouTube comments on BLACKPINK — "DDU-DU DDU-DU" M/V (https://www.youtube.com/watch?v=IHNzOHi8sJs), sorted by most popular.

**Collection method:** Automated scraper using the `youtube-comment-downloader` Python library (no API key required). The script (`scrape_comments.py`) targets up to 600 comments, filters out entries shorter than 15 characters, longer than 500 characters, pure emoji/punctuation runs, "first" bot posts, and comments containing URLs. The surviving comments are saved with their text, vote count, and reply count to `raw_comments.csv`.

**Labeling process:** I reviewed the top 100 comments and designed the labels myself. I then manually labeled 150 records, added taxonomy description, examples and my labeled dataset, and let Claude label the rest 71 to create a dataset of 221. 

**Label distribution:**

| Label | Count | % of dataset |
|---|---|---|
| `fan_war` | 34 | 15.45% |
| `genuine_comment` | 48 | 21.82% |
| `hype` | 50 | 22.73% |
| `stream` | 88 | 40.00% |
| **Total** | **220** | 100% |

**Difficult-to-label examples:**

1. **Example:** :oh well haters are coming back because another achievement will be achieve
   - **Could be:** hype vs. fan war
   - **Decision:** I ended up choosing hype because this comment doesn't mention another fandom. 

2. **Example:** Here after more than 2b
   - **Could be:** hype vs. stream
   - **Decision:** Most comments that fit into stream mentions a number (e.g. MV views), so I chose stream. This one mentions it, but it doesn't encourage streams, so it can be just a hype comment too. 

3. **Example:** "Do you think that your blinks can help us reach 500M on dna by bts (if us armys help you on your goal with beating twice).........
Even if y'all dont help...this a.r.m.y is gonna help ya cause i really like Blackpinks music.... (i hope yall get 400m first)"
   - **Could be:** genuine_comment vs. stream
   - **Decision:** I decided on genuine comment because this one contains reasoning and doesn't blindly encourage streaming. However, it does contain things about streaming.

---

## Fine-Tuning Approach

**Base model:** `distilbert-base-uncased`

**Training setup:**
- Epochs: 11
- Learning rate: 2e-5
- Batch size: 16
- Train / val / test split: 70% / 15% / 15%

**Hyperparameter decision:** 
I initially trained for 3 epochs following the default setup, but validation loss was still decreasing at that point, so I extended training to 15 epochs to find the true optimum. Reviewing the training lxog, the model was largely stagnant for the first 6 epochs — validation accuracy was stuck at 0.394 — before jumping to 0.667 at epoch 7. However, from epoch 11 onward, training loss continued to fall while validation loss began rising, a clear sign of overfitting. Since epoch 11 produced the lowest validation loss and highest validation accuracy, I re-trained for 11 epochs. I then reduced `warmup_steps` from 50 to 15, since the small dataset (~154 training samples) meant 50 warmup steps spanned nearly 5 full epochs before meaningful learning began. With the lower warmup, the model peaked earlier and higher — reaching 0.84 validation accuracy at epoch 8. I therefore set `num_train_epochs=8` as the final configuration, aligning training length with the best checkpoint and avoiding unnecessary overfitting.

---

## Baseline

**Model:** `llama-3.3-70b-versatile` via Groq (zero-shot)

**Prompt used:**

```
You are classifying YouTube comments from the BLACKPINK "DDU-DU DDU-DU" music video.
Assign each comment to exactly one of the following categories.

Fan_war: A comment that criticizes an artist without real proof, or dismisses them while praising a rival group or artist.
Example: "BLACKPINK SHOULD DISBAND TWICE IS GOOD"

Stream: A comment whose primary purpose is to encourage streaming, celebrate view milestones, call others to action on charts/votes, or coordinate fandom streaming efforts.
Example: "Everyone needs to go stream kill this love and make it the most streamed video of YouTube in 24 hours. Let's go blinks ❤️🖤"

Hype: A comment expressing blind praise, fandom excitement, milestone celebration, or emotional reaction with no supporting argument or reasoning.
Example: "2019 IS GONNA BE BLACKPINK'S YEAR Where are you at BLINKS?"

Genuine_comment: A comment that expresses a substantive personal take on the song, video, artist, or K-pop more broadly — grounded in a specific observation, comparison, or reasoned argument. Also use this label for anything that does not clearly fit the above three categories.
Example: "Im just too much obsessed with this song the tuning, the rap, the dance, the vocals"

Respond with ONLY the label name.
Do not explain your reasoning.

Valid labels:
Fan_war
Stream
Hype
Genuine_comment
```

**How results were collected:** I ran Section 5 of the Colab notebook on the locked test set before fine-tuning.

---

## Evaluation Report

### Overall Accuracy

| Model | Accuracy |
|---|---|
| Zero-shot baseline (Llama 3.3 70B) | 61.8% |
| Fine-tuned DistilBERT | 61.8% |

### Per-Class Metrics — Fine-Tuned Model

| Label | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| `hype` | 1.00 | 0.62 | 0.77 | 8 |
| `genuine_comment` | 0.30 | 0.43 | 0.35 | 7 |
| `fan_war` | 1.00 | 0.20 | 0.33 | 5 |
| `stream` | 0.67 | 0.86 | 0.75 | 14 |
| **Macro avg** | 0.74 | 0.53 | 0.55 | 34 |
| **Weighted avg** | 0.72 | 0.62 | 0.61 | 34 |

### Per-Class Metrics — Zero-Shot Baseline

| Label | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| `hype` | 0.50 | 0.75 | 0.60 | 8 |
| `genuine_comment` | 0.45 | 0.71 | 0.56 | 7 |
| `fan_war` | 0.67 | 0.40 | 0.50 | 5 |
| `stream` | 1.00 | 0.57 | 0.73 | 14 |
| **Macro avg** | 0.66 | 0.61 | 0.60 | 34 |
| **Weighted avg** | 0.72 | 0.62 | 0.63 | 34 |

### Confusion Matrix (Fine-Tuned Model)
*[confusion_matrix.png](confusion_matrix.png)*

### Wrong Predictions — Analysis

**1.**
- **Post:** Why? You can't even reach them up to the charts to tell them that they should disband
- **True label:** fan_war **Predicted:** stream
- **Analysis:** <!-- Which boundary was crossed? Why was it hard? Is this a labeling issue, a data distribution issue, or an inherent ambiguity? What would fix it? -->I think this line is hard to categorize. This line is a reply to a hateful comment and involved the word disband, so I categorized it as fan war, but the word "charts" can be misleading. More context regarding this line (e.g. the line this person was replying to) would be helpful to categorize it better. 

**2.**
- **Post:** Me I am your top fan I go so crazy about all of you guys and I’m sorry I cannot go to your concert I am just 8 that’s why
- **True label:** hype **Predicted:** genuine comment
- **Analysis:** I think this line has inherent ambiguity. Even looking through it manually, I find it hard to understand what this person mean.

**3.**
- **Post:** Yesss I can't wait. We are getting there blinks. Let's go
- **True label:** stream **Predicted:** genuine comment
- **Analysis:** This is a bad record/a labeling issue. With the context of a youtube video and Kpop MVs, I understand that "we are getting there" means that this person is referring to streaming. However, it's not inherently clear from the text. 

### Sample Classifications

| Post (excerpt) | True label | Predicted | Confidence |
|---|---|---|---|
| Unbelievable!!i want to cry😭😭😍 | `hype` | `hype` | 0.49 |
| They have 2.3b now! | `stream` | `stream` | 0.90 |
| Noah I am here after 1.4B views | `stream` | `stream` | 0.89 |
| Did I ever said that? Did I ever denied to the fact that DDDD is the most viewed KPOP MV? No. And sis I saw what you did there so don't pretend to be innocent,. If you don't like BTS atl... | `fan_war` | `fan_war` | 0.50 |
| Please stream udududud for 1.5B come on lets googgo | `stream` | `stream` | 0.90 |

**Correct prediction explained:** <!-- Pick one correct row above and explain in 1–2 sentences why the prediction is reasonable. -->
The last comment directly addresses the number of views and call people to stream the music video, exactly fitting the definition of `stream`. Both the call to action and mentioning of a number makes it easy to categorize as stream.

---

## Reflection: What the Model Learned vs. What I Intended

The model learned to identify `stream` and `hype` well — both classes have strong surface-level signals like view counts, milestone numbers, and exclamation-heavy language. However, it struggled most with `genuine_comment`, which is a catch-all label with no single distinguishing pattern. The model likely overfitted to lexical cues (e.g. numbers → stream, caps → hype) rather than discourse structure. It also nearly ignored `fan_war` — predicting it correctly only 20% of the time — possibly because fan war typically happens in a comments hierarchy structure. While the definition of `fan_war` is putting down another group to praise the other, this is often not clear through one comment, but through one conversation. When a reply doesn't reference another group, it makes it hard for the model to capture that. Moreover, a lot of Kpop group names are likely not denoted similar to other Kpop group name entities through distilled bert. Lacking the context makes it hard for the model to categorize them correctly. What I intended the model to learn was discourse intent, but what it actually picked up on was surface vocabulary.

---

## Spec Reflection

**One way the spec helped:** The spec's requirement to lock a test set before any fine-tuning forced an honest evaluation. Having a baseline zero-shot result before touching the fine-tuned model made it clear that fine-tuning didn't meaningfully outperform Llama 3.3 70B on raw accuracy, which was a more informative outcome than if I had only evaluated after training.

**One way my implementation diverged from the spec and why:** The spec suggested a 70/15/15 train/val/test split, but with only 220 samples, the test set ended up being just 34 examples — too small for per-class metrics to be statistically meaningful, especially for underrepresented labels like `fan_war` (support=5). A larger dataset or a different split ratio would have produced more reliable evaluation results.

---

## AI Usage

**Instance 1 — Annotation pre-labeling:**
- *What I directed the AI to do:* After manually labeling 150 comments, I provided Claude with my label taxonomy, definitions, and examples, then asked it to label the remaining 71 comments to complete the dataset.
- *What it produced:* A fully labeled set of 71 comments using the four categories.
- *What I changed or overrode:* I spot-checked a sample of the AI-assigned labels against my own judgment and adjusted borderline cases, particularly ones that sat between `stream` and `genuine_comment`.

**Instance 2 — Hyperparameter analysis:**
- *What I directed the AI to do:* I shared my training logs (epoch-by-epoch training loss, validation loss, and accuracy) and asked Claude to diagnose what was happening and suggest hyperparameter changes.
- *What it produced:* An analysis identifying the slow warmup as the cause of the stagnant first epochs, and recommendations to reduce `warmup_steps`, lower `num_train_epochs`, and increase `weight_decay`.
- *What I changed or overrode:* I applied the warmup and epoch changes but kept `weight_decay` at its original value. I also made the final epoch count decision myself based on re-running the training and observing where validation loss bottomed out.

---

## Demo video

https://drive.google.com/file/d/1ymNEKouzVk462iB4S1KYRfBhn3q7SJ7Q/view?usp=sharing
