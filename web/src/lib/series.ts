/**
 * Series config — maps series IDs to ordered lists of story IDs.
 *
 * Episodes appear in chronological (publication) order.
 * Each entry uses the canonical numeric-prefixed story ID on the VPS.
 */

export interface Series {
  id: string;
  title: string;
  tagline: string;
  description: string;
  coverImage?: string; // optional path to series cover
  episodes: SeriesEpisode[];
}

export interface SeriesEpisode {
  code: string; // e.g. "S01E01"
  storyId: string; // canonical story ID
  title: string;
  synopsis: string;
}

export const SERIES: Series[] = [
  {
    id: "caleb-adventures",
    title: "Caleb's Adventures",
    tagline: "A warm, funny bedtime series starring Caleb, his sister Lily, puppy Bubbles, and friends.",
    description:
      "Follow Caleb — a curious 3-year-old explorer — through 40 cozy, beautifully illustrated adventures with his family and best friends. From backyard treasure hunts to messy pancake breakfasts, every episode is a gentle, read-aloud-friendly story designed for toddlers aged 2–5.",
    episodes: [
      { code: "S01E01", storyId: "203_The_Backyard_Treasure_Hunt", title: "The Backyard Treasure Hunt", synopsis: "Dad hides a treasure map and the kids follow clues while Bubbles digs up everything except the treasure." },
      { code: "S01E02", storyId: "204_Bubbles_First_Bath", title: "Bubbles' First Bath", synopsis: "Muddy Bubbles escapes bath time leading to a hilarious house chase that ends in a bubble-filled party." },
      { code: "S01E03", storyId: "205_Nana_Joys_Riddle_Day", title: "Nana Joy's Riddle Day", synopsis: "Nana's three riddles lead the kids room-by-room through her cottage to discover a surprise picnic." },
      { code: "S01E04", storyId: "206_Mila_Paints_the_Park", title: "Mila Paints the Park", synopsis: "Mila's quest for the perfect painting keeps going wrong but the messy result becomes the best art ever." },
      { code: "S01E05", storyId: "207_Aidens_Big_Race", title: "Aiden's Big Race", synopsis: "Caleb finishes last in the neighborhood race but wins everyone's hearts by helping others along the way." },
      { code: "S01E06", storyId: "209_The_Rainy_Day_Fort", title: "The Rainy Day Fort", synopsis: "A rained-out day turns into an epic blanket fort that becomes a castle, spaceship, and cave." },
      { code: "S01E07", storyId: "210_Sofia_Birthday_Surprise", title: "Sofia's Birthday Surprise", synopsis: "The friends plan a chaotic but heartfelt surprise party with crooked cards, popped balloons, and a homemade cake." },
      { code: "S01E08", storyId: "211_Ravi_Magnifying_Glass_Mystery", title: "Ravi's Magnifying Glass Mystery", synopsis: "Ravi and Caleb follow mysterious tiny footprints through the neighborhood to discover a hedgehog family." },
      { code: "S01E09", storyId: "212_Mom_Garden_Song", title: "Mom's Garden Song", synopsis: "Mom teaches the kids to plant seeds while humming — and the plants actually grow, proving love helps things bloom." },
      { code: "S01E10", storyId: "213_The_Lemonade_Stand", title: "The Lemonade Stand", synopsis: "Three failed lemonade batches later, the kids finally get it right and donate the earnings to an animal shelter." },
      { code: "S01E11", storyId: "215_Bubbles_Goes_Missing", title: "Bubbles Goes Missing", synopsis: "The whole family searches the neighborhood for escaped Bubbles, who's found begging at the ice cream truck." },
      { code: "S01E12", storyId: "216_The_Library_Dragon", title: "The Library Dragon", synopsis: "A library scavenger hunt leads through book sections to a dragon puppet guarding the prize of new library cards." },
      { code: "S01E13", storyId: "217_Dad_Pancake_Disaster", title: "Dad's Pancake Disaster", synopsis: "Dad's fancy shaped pancakes all go hilariously wrong but the kids love naming each blobby creation." },
      { code: "S01E14", storyId: "218_The_Playground_Challenge", title: "The Playground Challenge", synopsis: "Caleb fails the monkey bars four times before finally making it across on the fifth try." },
      { code: "S01E15", storyId: "219_Nana_Joy_Baking_Day", title: "Nana Joy's Baking Day", synopsis: "Shells in eggs, flour explosions, and a spoon-licking puppy still produce amazing cookies and family memories." },
      { code: "S01E16", storyId: "220_Calebs_Adventures_The_Brave_Backyard_Campout", title: "The Brave Backyard Campout", synopsis: "Jack sets up a backyard tent for Caleb and Lily's first camping trip with marshmallows, fireflies, and ukulele songs." },
      { code: "S01E17", storyId: "221_Calebs_Kite-Tangling_Tumble", title: "Caleb's Kite-Tangling Tumble", synopsis: "Kites nose-dive, get stuck in trees, and tangle together — but Nana Joy's simple newspaper kite flies the highest." },
      { code: "S01E18", storyId: "222_Calebs_Wobbly_Costume_Parade", title: "Caleb's Wobbly Costume Parade", synopsis: "A neighborhood costume parade where Caleb's cardboard dinosaur keeps falling apart and everyone wins Best Costume." },
      { code: "S01E19", storyId: "223_Calebs_Shake_Paw_Surprise_with_Bubbles", title: "Caleb's Shake Paw Surprise", synopsis: "A whole day of failed attempts to teach Bubbles to shake hands ends with one perfect paw — and a startled dash under the couch." },
      { code: "S01E20", storyId: "224_Calebs_Sparkly_Thank-You_Party", title: "Caleb's Sparkly Thank-You Party", synopsis: "Season finale — Caleb throws a thank-you party for everyone who made his year special, with messy cake, glitter cards, and backyard dancing." },
      { code: "S02E01", storyId: "225_Calebs_Brave_Preschool_Day", title: "Caleb's Brave Preschool Day", synopsis: "Caleb starts preschool and is too nervous to let go of Sarah's hand — until he discovers all his friends are in his class." },
      { code: "S02E02", storyId: "226_Calebs_First_Snowy_Surprise_Meet_Mr_Wobble", title: "Meet Mr. Wobble", synopsis: "The first snowfall turns the backyard into a winter wonderland — complete with a lopsided snowman, snow-eating puppy, and hot cocoa." },
      { code: "S02E03", storyId: "227_Calebs_Adventures_Pip_the_Lost_Duckling", title: "Pip the Lost Duckling", synopsis: "Bubbles finds a lost duckling and the family embarks on a gentle mission to reunite it with its mama at the park pond." },
      { code: "S02E04", storyId: "228_Calebs_Adventures_The_Mystery_of_Nana_Joys_Lost_Key", title: "Nana Joy's Mystery Box", synopsis: "A locked wooden box, a lost key, and a cottage-wide treasure hunt reveal hand-drawn pictures from Nana Joy's childhood." },
      { code: "S02E05", storyId: "229_Caleb_and_Ravis_Epic_Bug_Safari", title: "Ravi's Bug Safari", synopsis: "Ravi and Caleb catalogue every bug in the backyard — until Bubbles accidentally destroys the ant highway and they rebuild it together." },
      { code: "S02E06", storyId: "230_Calebs_Adventures_The_Dragon_Egg_Mix-Up", title: "The Dragon Egg Mix-Up", synopsis: "Caleb's in charge of the shopping list at the farmer's market — dragon fruit becomes a dragon egg and his star keychain gets traded for honey." },
      { code: "S02E07", storyId: "232_Calebs_Glitter_Wiggle_for_Sofia", title: "Sofia's Dance Recital", synopsis: "Sofia freezes on stage at her first recital until Caleb stands up and does a silly wiggle dance to make her laugh." },
      { code: "S02E08", storyId: "233_Calebs_Adventures_Jacks_Wacky_Fix-It_Day", title: "Jack's Wacky Fix-It Day", synopsis: "Jack tries to fix everything in one day with Caleb as his assistant — spatulas instead of screwdrivers, and Sarah saves the day." },
      { code: "S02E09", storyId: "234_Calebs_Adventures_The_Polka-Dot_Birdhouse_Surprise", title: "The Polka-Dot Birdhouse", synopsis: "Mila and Caleb build and paint a birdhouse — nothing comes all day, but a wren family moves in by morning." },
      { code: "S02E10", storyId: "235_Calebs_Adventures_The_Super_Silly_Soccer_Showdown", title: "The Super Silly Soccer Showdown", synopsis: "Aiden teaches Caleb soccer with puppy goals counting double, falling down earning hugs, and a final score nobody can explain." },
    ],
  },
];

export function getSeriesById(id: string): Series | undefined {
  return SERIES.find((s) => s.id === id);
}

/** Given a story ID, find which series (if any) it belongs to and the episode index. */
export function findSeriesContainingStory(
  storyId: string
): { series: Series; episodeIndex: number } | null {
  for (const series of SERIES) {
    const idx = series.episodes.findIndex((e) => e.storyId === storyId);
    if (idx !== -1) return { series, episodeIndex: idx };
  }
  return null;
}
