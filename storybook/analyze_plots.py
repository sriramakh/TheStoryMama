#!/usr/bin/env python3
"""
Analyze 100 story plots for uniqueness, character diversity, and quality.
Outputs a detailed report and flags stories that need modification.
"""

import os
import json
import re
from collections import Counter, defaultdict

os.chdir(os.path.dirname(os.path.abspath(__file__)))

PLOTS_DIR = "stories_plots"

# Load all stories
stories = []
for i in range(1, 101):
    filepath = os.path.join(PLOTS_DIR, f"story_{i:03d}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            story = json.load(f)
            story["_file"] = f"story_{i:03d}.json"
            story["_index"] = i
            stories.append(story)

print(f"Loaded {len(stories)} stories\n")

# ============================================================
# 1. TITLE ANALYSIS
# ============================================================
print("=" * 70)
print("1. TITLE ANALYSIS")
print("=" * 70)

titles = [s["title"] for s in stories]
title_words = Counter()
for t in titles:
    words = re.findall(r'\b[A-Z][a-z]+\b', t)
    for w in words:
        title_words[w.lower()] += 1

# Check for duplicate or near-duplicate titles
title_lower = [t.lower() for t in titles]
dupes = [t for t, count in Counter(title_lower).items() if count > 1]
if dupes:
    print(f"\nDUPLICATE TITLES ({len(dupes)}):")
    for d in dupes:
        indices = [s["_file"] for s in stories if s["title"].lower() == d]
        print(f"  '{d}' -> {indices}")

# Titles starting with same words
title_starts = Counter()
for t in titles:
    start = " ".join(t.split()[:3])
    title_starts[start] += 1
repeated_starts = {k: v for k, v in title_starts.items() if v > 2}
if repeated_starts:
    print(f"\nOVERUSED TITLE PATTERNS (>2 stories with same 3-word start):")
    for pattern, count in sorted(repeated_starts.items(), key=lambda x: -x[1]):
        matching = [s["_file"] + ": " + s["title"] for s in stories if s["title"].startswith(pattern)]
        print(f"  '{pattern}...' x{count}: {matching}")

# Most common words in titles
print(f"\nMost common title words (top 15):")
for word, count in title_words.most_common(15):
    print(f"  {word}: {count}")

# ============================================================
# 2. CHARACTER ANALYSIS
# ============================================================
print(f"\n{'=' * 70}")
print("2. CHARACTER ANALYSIS")
print("=" * 70)

# Character counts
char_counts = Counter(len(s.get("characters", [])) for s in stories)
print(f"\nCharacter count distribution:")
for count in sorted(char_counts.keys()):
    print(f"  {count} characters: {char_counts[count]} stories")

# Species diversity
all_species = []
species_per_story = []
for s in stories:
    species = [c.get("type", "unknown").lower().strip() for c in s.get("characters", [])]
    all_species.extend(species)
    species_per_story.append(species)

species_counter = Counter(all_species)
print(f"\nTotal unique species/types: {len(species_counter)}")
print(f"\nMost common species (top 20):")
for species, count in species_counter.most_common(20):
    print(f"  {species}: {count}")

# Character names
all_names = []
for s in stories:
    for c in s.get("characters", []):
        all_names.append(c["name"].split()[0].lower())  # First name only
name_counter = Counter(all_names)
repeated_names = {k: v for k, v in name_counter.items() if v > 3}
if repeated_names:
    print(f"\nOVERUSED CHARACTER NAMES (>3 uses):")
    for name, count in sorted(repeated_names.items(), key=lambda x: -x[1]):
        print(f"  {name}: {count}")

# Habitat coherence check
LAND_SPECIES = {"squirrel", "rabbit", "hedgehog", "fox", "deer", "mouse", "badger", "bear",
                "raccoon", "chipmunk", "mole", "porcupine", "beaver", "puppy", "kitten", "cat",
                "dog", "goat", "donkey", "piglet", "lamb", "rooster", "hen", "goose", "alpaca",
                "pony", "cow", "girl", "boy", "grandmother", "grandfather", "baker"}
OCEAN_SPECIES = {"fish", "clownfish", "seahorse", "octopus", "dolphin", "jellyfish", "whale",
                 "shark", "starfish", "pufferfish", "narwhal", "crab", "shrimp", "angelfish",
                 "manta", "coral", "sea turtle", "manatee"}

habitat_issues = []
for s in stories:
    species = [c.get("type", "").lower() for c in s.get("characters", [])]
    has_land = any(any(ls in sp for ls in LAND_SPECIES) for sp in species)
    has_ocean = any(any(os_ in sp for os_ in OCEAN_SPECIES) for sp in species)
    if has_land and has_ocean:
        habitat_issues.append(f"  {s['_file']}: {s['title']} -> {species}")

if habitat_issues:
    print(f"\nHABITAT CONFLICTS (land + ocean mixed):")
    for issue in habitat_issues:
        print(issue)
else:
    print(f"\nHabitat coherence: PASS (no land/ocean mixing detected)")

# ============================================================
# 3. PLOT/SETTING ANALYSIS
# ============================================================
print(f"\n{'=' * 70}")
print("3. PLOT & SETTING ANALYSIS")
print("=" * 70)

# Setting diversity
settings = [s.get("setting", "").lower() for s in stories]
setting_keywords = Counter()
for setting in settings:
    for word in re.findall(r'\b\w+\b', setting):
        if len(word) > 3:
            setting_keywords[word] += 1

print(f"\nMost common setting words (top 15):")
for word, count in setting_keywords.most_common(15):
    print(f"  {word}: {count}")

# Animation style distribution
style_counter = Counter(s.get("animation_style", "unknown") for s in stories)
print(f"\nAnimation style distribution:")
for style, count in style_counter.most_common():
    print(f"  {style}: {count}")

# ============================================================
# 4. ENDING ANALYSIS (no bedtime endings)
# ============================================================
print(f"\n{'=' * 70}")
print("4. ENDING ANALYSIS")
print("=" * 70)

NIGHT_WORDS = ["sleep", "dream", "night", "moon", "star", "bed", "yawn", "snore",
               "lullaby", "pillow", "blanket", "dark", "firefly", "lantern", "dusk",
               "sunset", "twilight", "sleepy"]

night_endings = []
for s in stories:
    scenes = s.get("scenes", [])
    if not scenes:
        continue
    last_3 = scenes[-3:]
    combined = " ".join(sc.get("text", "") + " " + sc.get("background", "") for sc in last_3).lower()
    matches = [w for w in NIGHT_WORDS if w in combined]
    if matches:
        night_endings.append(f"  {s['_file']}: {s['title']} -> matches: {matches}")

if night_endings:
    print(f"\nSTORIES WITH NIGHT/SLEEP ENDINGS ({len(night_endings)}):")
    for ne in night_endings:
        print(ne)
else:
    print(f"\nEnding check: PASS (no bedtime/night endings detected)")

# ============================================================
# 5. MORAL ANALYSIS
# ============================================================
print(f"\n{'=' * 70}")
print("5. MORAL ANALYSIS")
print("=" * 70)

morals = [s.get("moral") for s in stories if s.get("moral")]
no_moral = sum(1 for s in stories if not s.get("moral"))
print(f"\nStories with moral: {len(morals)}")
print(f"Stories without moral: {no_moral}")

moral_counter = Counter(m.lower().strip().rstrip(".") for m in morals)
repeated_morals = {k: v for k, v in moral_counter.items() if v > 1}
if repeated_morals:
    print(f"\nREPEATED MORALS:")
    for moral, count in sorted(repeated_morals.items(), key=lambda x: -x[1]):
        files = [s["_file"] for s in stories if s.get("moral") and s["moral"].lower().strip().rstrip(".") == moral]
        print(f"  x{count}: '{moral}' -> {files}")

# ============================================================
# 6. SCENE COUNT ANALYSIS
# ============================================================
print(f"\n{'=' * 70}")
print("6. SCENE COUNT DISTRIBUTION")
print("=" * 70)

scene_counts = Counter(len(s.get("scenes", [])) for s in stories)
for count in sorted(scene_counts.keys()):
    print(f"  {count} scenes: {scene_counts[count]} stories")

# ============================================================
# 7. SIMILARITY DETECTION (title + plot overlap)
# ============================================================
print(f"\n{'=' * 70}")
print("7. POTENTIAL DUPLICATES / VERY SIMILAR STORIES")
print("=" * 70)

# Compare first scene text for similarity
from difflib import SequenceMatcher

similar_pairs = []
for i in range(len(stories)):
    for j in range(i+1, len(stories)):
        # Compare titles
        title_sim = SequenceMatcher(None, stories[i]["title"].lower(), stories[j]["title"].lower()).ratio()
        # Compare first scene text
        text_i = stories[i].get("scenes", [{}])[0].get("text", "")
        text_j = stories[j].get("scenes", [{}])[0].get("text", "")
        text_sim = SequenceMatcher(None, text_i.lower(), text_j.lower()).ratio()
        # Compare settings
        set_i = stories[i].get("setting", "")
        set_j = stories[j].get("setting", "")
        set_sim = SequenceMatcher(None, set_i.lower(), set_j.lower()).ratio()

        avg_sim = (title_sim + text_sim + set_sim) / 3
        if avg_sim > 0.55 or title_sim > 0.75:
            similar_pairs.append((avg_sim, title_sim, stories[i]["_file"], stories[i]["title"],
                                  stories[j]["_file"], stories[j]["title"]))

if similar_pairs:
    similar_pairs.sort(reverse=True)
    print(f"\nSimilar story pairs ({len(similar_pairs)} found):")
    for avg, tsim, f1, t1, f2, t2 in similar_pairs[:20]:
        print(f"  [{avg:.2f} avg, {tsim:.2f} title] {f1}: '{t1}' <-> {f2}: '{t2}'")
else:
    print(f"\nNo highly similar stories detected.")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'=' * 70}")
print("SUMMARY")
print("=" * 70)
issues = []
if dupes:
    issues.append(f"Duplicate titles: {len(dupes)}")
if repeated_starts:
    issues.append(f"Overused title patterns: {len(repeated_starts)}")
if habitat_issues:
    issues.append(f"Habitat conflicts: {len(habitat_issues)}")
if night_endings:
    issues.append(f"Night/sleep endings: {len(night_endings)}")
if repeated_morals:
    issues.append(f"Repeated morals: {len(repeated_morals)}")
if similar_pairs:
    issues.append(f"Similar story pairs: {len(similar_pairs)}")

if issues:
    print(f"\nISSUES TO FIX:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print(f"\nAll checks passed!")

print(f"\nTotal stories: {len(stories)}")
print(f"Unique species: {len(species_counter)}")
print(f"Avg characters per story: {sum(len(s.get('characters',[])) for s in stories)/len(stories):.1f}")
