# -*- coding: utf-8 -*-
"""Промпты на арты ролика 2 «Жульничество» для Sol (Codex). Пишет p_NN.txt, r_NN.txt и md для волта."""
import os, sys, io

OUT = r"C:\Azlanti\Video\Session0\02__Жульничество\art\sol_run1"
MD = r"C:\DND\sync\Sync\Obsidian\PF2e\Кампейны\Азланти\Sessions\Session0\Видео\02__Жульничество__промпты.md"

LINE = ("DRAWING STYLE: ink and light watercolour wash. Crisp, confident dark-brown ink contour of medium-bold, "
        "slightly varying weight - the contour does the work, shading is minimal. Stylised semi-realistic faces with "
        "large expressive eyes, clean nose and lip lines. Hair drawn as flowing outlined locks, not single strands. "
        "Flat pale watercolour tints inside the lines with one soft shadow tone; muted earth palette - sepia, ochre, "
        "warm grey, a little soft green outdoors, warm amber only where there is firelight or low sun. The paper shows "
        "real watercolour pooling. NOT a pencil drawing, NOT an etching, NOT a painting, NOT photorealistic, NOT anime, "
        "NOT flat vector lineart.")
PAPER = ("PAPER: drawn on a FLAT rectangular sheet of LIGHT warm cream aged parchment (pale, never orange or dark tan) "
         "with softly ragged torn edges; the whole sheet is visible inside the frame on a thin plain white margin - NOT a "
         "rolled scroll, no curled corners. A few pale tea stains, one coffee ring, small dark ink splatters. NO drawn "
         "border, NO frame, NO ruled box - the drawing bleeds softly into bare parchment.")
DENS = {
 "sketch": ("DENSITY - SKETCH: the figures are drawn LARGE and are the whole point; around them the setting is only "
            "hinted with a few loose strokes and one faint wash. Roughly a third to a half of the sheet stays bare "
            "parchment. No sky, no detailed scenery."),
 "scene": ("DENSITY - SCENE: a complete little scene drawn across most of the sheet in ink line and light washes, with a "
           "real setting and depth, but airy: washes stay pale, the paper tone shows through everywhere, and the drawing "
           "fades out into bare parchment toward the edges of the sheet instead of filling it corner to corner."),
 "object": ("DENSITY - STILL LIFE: only the described objects, drawn with care in ink and pale wash in the middle of the "
            "sheet; everything around them is bare parchment."),
}
TAIL = ("Build the composition inside the central horizontal band so it survives a 16:9 crop; every head fully visible "
        "with margin above it. Poses are calm, held states, not mid-motion. No text, no letters, no labels, no signature. "
        "Landscape 16:9. One single illustration, no variant sheet, no multiple poses.")

BEL = "Bel: a pale adult elf woman with long blue-black wavy hair, pointed ears, large violet-grey eyes, in a cream off-shoulder dress."
ANK = "Ankanto: a tanned young man with wavy white hair half tied back in a short ponytail, loose strands at the face, pale grey-blue eyes, in an ivory open-collar shirt."
MIK = "Mikael: a calm fair man with short blond hair swept back, square clean-shaven face, in a dark cassock with a white clerical collar tab. Nothing hangs around his neck - no cross, no pendant, no necklace."
BEADS = "He holds wooden prayer beads with a small golden eight-rayed sun pendant in his hands ONLY - none around his neck, no second string; absolutely NOT a cross, no cross shape anywhere."
VAR = "Varen: a tired young man in his twenties with short tousled chestnut hair and light stubble, in a white tunic with a golden eight-rayed sun on the chest (a sun, NOT a cross)."
TAR = "Tarven: an old priest with white hair and a short white beard, a kind weathered face, in a plain white robe with a small golden eight-rayed sun on the chest (a sun, NOT a cross) and a rope belt."
BIRD = ("a European nightjar - a small mottled grey-brown bird with a broad flat head, a tiny beak and large dark eyes, "
        "crouching LENGTHWISE along the wood with long folded wings; NOT an owl, no ear tufts, no facial disk, not a songbird")
HW = "Hearthwick is a small forest village: dark log cabins with plank roofs among tall pines, kitchen gardens, rough pole fences."

R = {"bel": ("ref_bel.png", "Bel"), "ank": ("ref_ankanto.jpg", "Ankanto"), "mik": ("ref_mikael.jpg", "Mikael"),
     "var": ("ref_varen.jpg", "Varen"), "tar": ("ref_tarven.jpg", "Tarven")}
S = {"village": ("ref_village.jpg", "how Hearthwick and landscapes are drawn in this series"),
     "sheet": ("ref_sheet.jpg", "how a report sheet on the desk is drawn in this series"),
     "inn": ("ref_inn.png", "the previous frame of this sequence: the same room and the same figure - keep the room, the counter, the light and the figure identical"),
     "bird": ("ref_nightjar.png", "the same bird as drawn earlier in this series - keep it identical")}

# кадр, slug, плотность, персонажи-референсы, стилевые референсы, сцена
A = [
(1, "village_garden", "scene", ["bel","ank","mik"], ["village"],
 f"Early morning in Hearthwick. {HW} Seen from beside a stone well, whose rim and winch sit partly in the near foreground on the left. Beyond it a kitchen garden with rows of vegetable beds between two cabins. Among the beds, small in the frame and seen FROM BEHIND, stand three people together: a woman with long blue-black hair in a cream dress, a man with white hair in an ivory shirt, a man with blond hair in a long dark cassock. Their faces are not visible. Quiet, spacious morning."),
(2, "nightjar_fence_v2", "sketch", ["bel","ank","mik"], ["bird"],
 f"Close foreground: the top rail of a rough wooden pole fence running across the sheet, and on it {BIRD}. The bird is the subject, drawn large. Lower down and further away, beyond the rail, three small human figures stand talking, drawn simply but recognisable by hair and clothes: a woman with long BLUE-BLACK hair in a cream dress; a young tanned man with WHITE hair in a ponytail, in an ivory shirt with no vest; a blond man in a long dark ankle-length cassock. Faces are only indicated. The bird is listening to them."),
(3, "three_at_fence", "sketch", ["bel","ank","mik"], [],
 f"Three people at a rough wooden pole fence, from the waist up, close together. {BEL} She is speaking, relaxed and friendly, with a small conversational hand gesture. {ANK} He is turned to her and beams with open delight, as if he has just been handed an award. {MIK} {BEADS} He stands beside them, serene, running the beads through his fingers. Behind them one cabin roofline and a pine, barely indicated."),
(4, "bel_road_v2", "sketch", ["bel"], [],
 f"{BEL} She stands at a rough wooden fence in the left third of the sheet, drawn large from the waist up, with her head turned in PROFILE toward the right, away from the viewer, gazing down a dirt road - a serious, searching look. She does NOT look at the viewer. The road is a few curving lines running off to the right into bare parchment."),
(5, "report_two_names", "object", [], ["sheet"],
 "A report sheet lying on a dark wooden desk, seen from above at a slight angle; the worn leather edge of a folder is visible along one side and a corner of the desk shows beyond it. On the sheet: two short lines of handwriting rendered ONLY as loose wavering ink strokes - no letters, nothing readable - one upper left, one upper right; from each a thin ink arrow runs down and the two arrows meet at a single ink dot in the lower middle. A quill pen and a small inkwell rest beside the sheet."),
(6, "hidden_settlement", "scene", [], ["village"],
 "A memory, a flashback. A deep forest thicket with a few tall trunks in the foreground. Beyond them thick pale mist, and in the mist the faint outlines of a small hidden settlement - a few roofs and a fence that seem almost not to be there, as if the eye invents them. No people, no animals. The mist is one soft grey wash; quiet and uncertain."),
(7, "bel_lost_forest", "sketch", ["bel"], ["village"],
 "A memory, a flashback. One small lone woman in a cream dress with long blue-black hair stands in an empty forest, seen from a distance, her figure no taller than a quarter of the sheet. Around her on every side stand tree trunks that all look the same, evenly spaced, with no path between them. She has stopped and is looking around. Pale, cool, a little eerie."),
(8, "nightjar_listening", "sketch", [], [],
 f"On the top rail of a rough wooden pole fence sits {BIRD}. Its head is turned sharply to one side, toward something out of frame that it is listening to, and one feather on its back is slightly raised. The bird is drawn large in the middle-left of the sheet; the rail runs across; the rest is bare parchment with a few grass strokes."),
(9, "kyonin_mist", "scene", [], ["village"],
 "Kyonin, the closed elven kingdom, imagined from hearsay: an ancient misty forest of very tall, slender, graceful trees. Between the trunks, far off and barely distinguishable in the mist, the outlines of slim elven towers. No people. Layers of pale mist as soft grey-green washes; mysterious and remote."),
(10, "silent_look", "sketch", ["ank","mik"], [],
 f"Two men face each other in profile across the sheet, each from the chest up, one at the left edge of the drawing and one at the right, looking straight into each other's eyes in silence. {ANK} His mouth is slightly open, a sentence cut off. {MIK} His face is perfectly still. Between them is a wide gap of completely EMPTY parchment - nothing is drawn there; the composition holds the emptiness."),
(11, "ankanto_careful", "sketch", ["ank"], [],
 f"{ANK} Drawn large from the waist up in the right third of the sheet, in three-quarter view. He is speaking carefully now: shoulders lowered, hands quiet and loosely held together in front of him, eyebrows slightly raised, choosing words. No broad smile."),
(12, "bel_shrug", "sketch", ["bel"], [],
 f"{BEL} Drawn large from the waist up in the left third of the sheet, facing the viewer. She shrugs lightly - both shoulders a little raised, one open palm turned up - with a calm, untroubled face."),
(13, "ankanto_asks", "sketch", ["ank"], [],
 f"{ANK} Drawn large from the waist up in the right third of the sheet, in three-quarter view facing left. He leans slightly forward from the waist with a curious, friendly, slightly cheeky look, one hand lifted with the index finger half raised - asking a question."),
(14, "bel_squint", "sketch", ["bel"], [],
 f"{BEL} A close head-and-shoulders view in the left third of the sheet. She is looking PAST the viewer, a little to the side, with narrowed eyes - a shrewd, appraising squint - and the faintest knowing smile. She has noticed something."),
(15, "ankanto_caught_v2", "sketch", ["ank","mik"], [],
 f"Two men from the waist up. {ANK} He spreads both hands wide, palms up, with a broad disarming grin - caught, and not sorry at all. {MIK} He stands next to him with a completely impassive face, empty hands folded in front of him, looking straight ahead. No beads anywhere in this picture."),
(16, "mikael_unreadable", "sketch", ["mik"], [],
 f"{MIK} A close head-and-shoulders study in the right third of the sheet, in THREE-QUARTER VIEW, head turned slightly away, eyes glancing sideways - NOT facing the viewer, do not copy the pose of the reference. His hands are not in the picture. His expression can be read two opposite ways at once, agreement and objection: the corner of the mouth barely lifted, one brow slightly raised. He says nothing."),
(17, "ankanto_asks_again", "sketch", ["ank"], [],
 f"{ANK} Drawn large from the waist up in the right third of the sheet, in three-quarter view facing left, leaning slightly forward with one hand lifted and the index finger half raised - asking a question for the second time. This time his smile is sheepish and a little guilty, eyebrows tilted up apologetically, the other hand rubbing the back of his neck."),
(18, "bel_no", "sketch", ["bel"], [],
 f"{BEL} A close head-and-shoulders view in the middle-left of the sheet, facing the viewer directly, with a calm, level, composed face and closed lips. She has just said one short word. Nothing else is drawn; the rest of the sheet is bare parchment."),
(20, "bel_libraries", "sketch", ["bel","ank"], [],
 f"Two people from the waist up at a rough wooden fence. {BEL} She leans a little forward and speaks earnestly, hopeful, one hand resting on the rail. {ANK} He listens with his head tilted to one side and a puzzled, surprised half-smile."),
(21, "bel_puzzled", "sketch", ["bel"], [],
 f"{BEL} Drawn from the waist up in the middle of the sheet, facing the viewer, with a look of mild honest puzzlement - eyebrows slightly raised, head a touch tilted, one hand half lifted as if saying 'who knows'. There is NO background at all: only her figure on bare parchment that fades away around her."),
(22, "endless_library", "scene", [], [],
 "The inside of a library that is larger than any building could hold. Very tall bookshelves stand in long rows and recede into the distance far further than seems possible, vanishing in pale haze. A slanting shaft of light falls from a high window across the aisle. A rolling ladder leans on one shelf. Not a single person. Still, quiet, slightly uncanny. Books are simple spines with no lettering."),
(23, "ankanto_sun_symbol", "sketch", ["ank"], [],
 f"{ANK} Drawn from the waist up in the left third of the sheet, in three-quarter view, speaking with one open hand lifted, thoughtful and gentle. In the empty parchment behind his shoulder a large eight-rayed sun emerges very faintly as a pale golden wash with no hard outline - as if remembered rather than drawn. A sun, absolutely NOT a cross."),
(24, "bel_looks_away", "sketch", ["bel"], [],
 f"{BEL} Drawn from the waist up in the left third of the sheet. She has turned her head away and looks down and to the side; one hand holds her other arm across her body - a slightly closed, guarded posture. Polite, but the subject is closed."),
(25, "report_broken_line", "object", [], ["sheet"],
 "A report sheet lying on a dark wooden desk, seen from above at a slight angle; the worn leather edge of a folder is visible along one side and a corner of the desk shows beyond it. On the sheet a few rows of handwriting rendered ONLY as loose wavering ink strokes - no letters, nothing readable. The last row stops abruptly in the middle of the line. The quill pen has been laid aside, away from the sheet, next to a small inkwell."),
(26, "hearthwick_from_above", "scene", [], ["village"],
 f"Hearthwick in daylight seen from high above, a bird's-eye view. {HW} In the centre a slightly larger house with a fenced yard - the old priest's home - and from it the lanes and the other cabins spread outward in loose rings, like ripples on water. Tiny figures of villagers at work: carrying water, chopping wood, tending beds. Pines all around the edge, fading into bare parchment."),
(27, "huge_backpack_v2", "sketch", ["bel","mik"], [],
 f"Morning at the doorway of a log cabin. {BEL} She stands proudly beside an enormous, overstuffed travelling backpack that stands on the ground and reaches up to her shoulder, with a rolled blanket, a pot and bundles tied all over it. {MIK} He stands a step away and covers his eyes with one hand in quiet despair. No beads in this picture. Both drawn full-figure, the backpack between them."),
(28, "ankanto_opens_pack", "sketch", ["ank","bel"], [],
 f"{ANK} He is crouched on one knee beside an enormous overstuffed backpack that stands on the ground, both hands untying the drawstring at its mouth, peering in with interest. {BEL} She stands next to it with her hands clasped behind her back, looking up and away with the innocent face of someone who has done nothing wrong."),
(29, "three_towels", "object", [], [],
 "Three folded linen towels laid out on the ground in a neat row, side by side: a large one, a medium one and a small one, each with a slightly different woven border. A few blades of grass and a corner of an open backpack at the edge."),
(30, "thirty_dresses", "sketch", ["bel","ank"], [],
 f"{BEL} She holds a fine dress up in front of her at arm's length by the shoulders, showing it off, entirely serious. A heap of more folded dresses lies by her feet. {ANK} Facing her, he spreads both hands in helpless disbelief, eyebrows up, half laughing."),
(31, "mikael_packs", "sketch", ["mik"], [],
 f"{MIK} He kneels on the ground beside an open backpack and packs it: one hand presses a tightly rolled bundle down inside, the other holds the next folded item ready. Calm, precise, practised hands - the hands are the centre of the drawing. No beads in this picture. Neat small piles of folded things wait in a row beside him."),
(32, "bel_asks_directly", "sketch", ["bel"], [],
 f"{BEL} Drawn from the waist up in the middle of the sheet, facing the viewer straight on with a direct, open, serious look and slightly parted lips - she has just asked an important question. In the near foreground at the left and right edges, out of focus and barely sketched, the backs of two men's shoulders: one in an ivory shirt with white hair, one in a dark cassock with blond hair."),
(33, "hand_on_shoulder", "sketch", ["mik","ank"], [],
 "An extreme close-up: a man's hand rests firmly and calmly on another man's shoulder. The hand comes out of a dark cassock sleeve; a string of wooden prayer beads with a small golden eight-rayed sun pendant is wrapped around that wrist and nowhere else - a sun, absolutely NOT a cross. The shoulder wears an ivory linen shirt; above it only the jaw, an ear and a few loose white locks of the second man are visible, his mouth just closing. The hand is the centre of the drawing."),
(34, "ankanto_far_city", "sketch", ["ank"], [],
 f"{ANK} Drawn from the waist up in the left third of the sheet, in three-quarter view, speaking steadily and reassuringly, one hand lifted in a small gesture toward the distance. Far behind him, across the empty parchment, the faint hazy silhouette of a great distant city with towers and domes on the horizon - a pale wash with almost no line."),
(35, "dawn_farewell_v2", "scene", ["tar","var","bel","ank"], ["village"],
 f"Dawn in the fenced yard in front of a log cabin in Hearthwick. Five people stand in a loose group, full-figure and fairly small in the frame, with very long shadows stretching across the ground from the low sun: an old white-bearded priest in a white robe, a young chestnut-haired man in a white tunic with a golden sun, a dark-haired elf woman in a cream dress, a white-haired tanned young man in an ivory shirt, and a blond man in a dark cassock. Travel packs wait by the gate. Warm amber light low on the horizon, pines behind."),
(36, "ankanto_hugs_varen", "sketch", ["ank","var"], [],
 f"Two men in a tight, heartfelt embrace, from the waist up. {ANK} He hugs hard, eyes shut, chin over the other's shoulder. {VAR} He is a little surprised and moved, one arm around his friend's back."),
(38, "mikael_hugs_varen", "sketch", ["mik","var"], [],
 f"Two men in a gentle, restrained embrace, from the waist up. {MIK} He holds the other lightly, barely touching, his head inclined close to the other's ear, lips slightly parted - he is saying something very quietly. No beads in this picture. {VAR} He listens, eyes lowered."),
(40, "bel_hugs_varen", "sketch", ["bel","var"], [],
 f"A warm, tight hug, from the waist up. {BEL} She throws both arms around him and holds on tight, cheek against his shoulder, eyes closed, smiling. {VAR} He is taken aback, arms half raised, then smiling awkwardly."),
(41, "tarven_blessing", "sketch", ["tar","bel"], [],
 f"{TAR} He stands and holds one open hand just above the head of a woman in front of him, in blessing, his face gentle. {BEL} She stands before him, shorter, looking up at him from below with a stubborn, earnest expression. Both from the waist up; the raised hand is the centre of the drawing."),
(42, "nightjar_dawn", "scene", [], ["bird","village"],
 f"On a bare pine branch in the upper foreground sits {BIRD}, seen against a pale dawn sky, looking down with weary patience. Far below, small in the frame, a fenced yard in front of a log cabin where five tiny figures are still hugging one another. Low amber sun, long shadows."),
(44, "path_from_above", "scene", [], ["village"],
 "A view from high above and behind, through the eyes of a flying bird: a wide, straight, well-trodden path runs away from the viewer along the bank of a broad calm river, with open meadow on the other side and no tree canopy overhead. Far below on the path, three tiny walking figures in a row - one in cream, one in ivory, one in dark. Hazy mountains beyond the river. Open, calm, bright."),
(45, "bel_rests", "sketch", ["bel","ank","mik"], [],
 f"By the side of a path. {BEL} She sits on a large roadside stone, one shoe taken off and held in her hand, inspecting her foot with a pained, indignant face. A few steps further along the path, smaller, two men stand waiting patiently: a white-haired one in an ivory shirt with a pack on his back, hands on hips, and a blond one in a dark cassock, perfectly still."),
(46, "bel_marches_v2", "sketch", ["bel","ank","mik"], [],
 f"On a path. {BEL} She walks in front, drawn large, coming toward the viewer with brows drawn down, lips pressed into a thin line and a stony, grimly determined glare fixed straight ahead, hands gripping the straps of a backpack. Several steps behind her, smaller, two men follow and exchange a sideways glance with each other: a white-haired one in an ivory shirt, eyebrows raised, and a blond one in a dark cassock with nothing around his neck and no beads."),
(47, "greenford_sunset", "scene", [], ["village"],
 "Greenford seen from a low hill at sunset: a farming village of some five hundred people - many thatched and shingled roofs clustered together, surrounded by open meadows and strips of ploughed fields instead of forest, with a broad calm river curving past it and a small ferry landing. Low amber sun, long soft shadows, hazy mountains far beyond. The road descends from the viewer toward the river."),
(48, "ferry", "scene", [], [],
 "A flat wooden rope ferry crossing a broad calm river at sunset. On it four dark figures seen as silhouettes against the bright low sun and its reflection on the water: a ferryman standing at one end pushing a long pole down into the water, and three passengers - a woman with long hair, a man with a ponytail, a tall man in a long cassock. The far bank is a low line with a few roofs. Amber and sepia washes, glittering water left as bare paper."),
(49, "bel_and_cart", "sketch", ["bel"], [],
 f"{BEL} Drawn large from the waist up in the left third of the sheet, her face lit up with sudden radiant joy, both hands clasped in front of her chest, eyes wide. Behind her shoulder, further away and smaller, an ordinary empty two-wheeled farm cart stands by the open gates of a wooden warehouse."),
(50, "inn_outside_v2", "scene", [], [],
 "A village inn at dusk, seen from the lane: a two-storey timber building with a shingled roof. Above the door hangs a plain dark wooden signboard with NO lettering at all, and tied to it a bundle of dried grass and herbs. A small pretty garden with flower beds runs along the side and back. Warm amber light glows in the windows and spills from the slightly open door; a small lantern under the eaves. A tub of water and a boot brush stand by the wall. The sky is a cool dusk wash; quiet and welcoming. There are NO people and NO animals anywhere in the picture - the lane and the doorway are empty."),
(51, "figure_at_counter_v2", "scene", [], [],
 "The dim, quiet common room of a village inn, seen from just inside the door. The room is EMPTY of guests: no other people, no animals, the two tables and their chairs stand empty. The counter and the figure behind it fill the right half of the picture, drawn large. A wooden counter with barrels behind it; on the wall an animal hide; bunches of herbs drying on the windowsill. Behind the counter stands a very tall, broad-shouldered figure seen against the last light of a window, almost a silhouette: only the head and shoulders are clearly readable - dark grey skin, silver-grey hair pulled smoothly back, a dark laced leather vest over a linen shirt. The figure is framed so that nothing behind the shoulders can be made out - deep shadow there. Dark warm-brown washes, one amber glow from a candle on the counter. The figure is the centre; calm, still, slightly unsettling."),
(52, "folded_wings_v2", "scene", [], ["inn"],
 "The same dim, quiet, EMPTY common room of a village inn as in the reference - no guests, no other people, no animals - in a slightly wider view: a wooden counter with barrels, a candle on it, a window behind. Behind the counter stands a very tall, broad-shouldered man seen against the window light, nearly a silhouette: dark grey skin, silver-grey hair pulled smoothly back, a dark laced leather vest over a linen shirt. Rising behind his back are TWO large feathered wings, folded: the left one folded easily, the right one held slightly lower and stiffer. He is not an angel and has no halo - a quiet innkeeper of a winged people. The wings are the revelation of the picture and are clearly readable against the window."),
]

# ---- правки после просмотра Влада 06.10.2026 (референсы из Foundry) ----
REDRAW = "redraw it in the ink-and-wash style of this series, do NOT copy its painted rendering"
KER = ("Kerren: a very tall, broad-shouldered man of a winged people (a strix): dark grey skin, pointed ears, large fully black eyes, "
       "silver-grey hair pulled smoothly back, a brown laced leather vest over a linen shirt with rolled sleeves. Calm, reserved, dignified.")
R["ker"] = ("ref_kerren.jpg", "Kerren")
S["road"] = ("ref_road.jpg", "the real place from the campaign, the forest road along the river; keep its geography (forest on one side of the path, the river on the other, misty wooded hills beyond) but " + REDRAW)
S["gf_aerial"] = ("ref_greenford_aerial.jpg", "the real Greenford from the campaign; keep its layout (village on the far bank of the river, fields beside it, forest around) but " + REDRAW)
S["gf_street"] = ("ref_greenford_street.jpg", "what Greenford houses look like (half-timbered, thatched); use for architecture only, not for style")
S["lane"] = ("ref_lane.jpg", "what a Greenford lane and its houses look like (half-timbered, thatched, rutted dirt road); use for architecture only, and " + REDRAW)
S["inn_in"] = ("ref_inn_interior.jpg", "the real common room of this inn from the campaign; keep its layout and furniture (counter with barrels and shelves, hanging herbs, lantern, staircase on the right, stone floor) but " + REDRAW)
S["inn_prev"] = ("ref_inn_prev.png", "the previous frame of this sequence; keep the room, the light and the man identical")
OV = {
 5: (5, "report_two_portraits_v2", "object", ["bel","ank"], ["sheet"],
   "A report sheet lying on a dark wooden desk, seen from above at a slight angle; the worn leather edge of a folder is visible along one side and a corner of the desk shows beyond it. On the sheet the observer has drawn two small, quick ink portrait sketches side by side: on the left the head of the elf woman with long dark wavy hair and pointed ears, on the right the head of the young man with white hair in a ponytail. One loose ink line loops around both heads and joins them into a single oval. Under each head a short line of handwriting rendered ONLY as wavering ink strokes - no letters, nothing readable. A quill pen and a small inkwell rest beside the sheet."),
 6: (6, "hidden_settlement_v2", "scene", [], ["village"],
   "A memory, a flashback. A forest thicket: three or four tall trunks in the foreground. MIST dominates the picture: thick pale mist fills the whole middle of the sheet, swallows the lower parts of the trunks and the ground, and thins out into bare parchment toward the edges. Deep inside the mist, only as the palest grey ghost shapes with almost no line, a few roofs and a bit of fence of a hidden settlement - so faint that the eye is not sure they are there. Very little green, almost no detail. No people, no animals. Quiet and uncertain."),
 7: (7, "bel_lost_forest_v2", "sketch", ["bel"], ["village"],
   "A memory, a flashback. One small lone woman in a cream dress with long blue-black hair stands in an empty forest, seen from a distance, her figure no taller than a quarter of the sheet. Around her stand tree trunks that all look the same, evenly spaced, with no path between them. Thick pale mist closes in from every side: the trunks dissolve into it toward the edges of the drawing, so the forest has no visible end, and all four edges of the picture are only mist fading into bare parchment. She has stopped and is looking around. Pale, cool, a little eerie."),
 44: (44, "path_from_above_v2", "scene", [], ["road"],
   "A view from high above and behind, through the eyes of a flying bird, of the place shown in the reference: a well-trodden dirt path runs away from the viewer along the bank of a broad calm river - dense old forest on the left of the path, the water on the right, and across the river wooded hills and rocky ridges in haze. Far below on the path, three tiny walking figures in a row: one in cream with long dark hair, one in ivory with white hair, one in a dark cassock. The sky is open above the path. Calm, bright, spacious."),
 47: (47, "greenford_across_river_v3", "scene", [], ["gf_aerial","gf_street"],
   "Sunset. The viewer stands on the NEAR bank of a broad river, where a forest road comes down to a small wooden ferry landing in the foreground - a short jetty, a mooring post, a rope stretching out over the water. The whole width of the river lies between the viewer and the village. On the FAR bank lies Greenford: a farming village of about a hundred half-timbered and thatched houses clustered together, with strips of fields and meadows beside it and forest behind, and its own landing with a few boats on its shore. Low amber sun, long soft shadows, hazy hills far beyond. The village is clearly on the other side of the water. On the near landing, small and seen FROM BEHIND, stand exactly three travellers looking across the river: a woman with long blue-black hair in a cream dress, a man with white hair in a ponytail in an ivory shirt with a pack on his back, and a blond man in a long dark cassock. No other people and no animals anywhere."),
 50: (50, "inn_outside_v3", "scene", [], ["lane"],
   "A quiet side lane of Greenford at dusk, away from the ferry. A two-storey half-timbered inn with a thatched roof stands a little back from the rutted dirt lane, built like the houses in the reference. Above its door hangs a dark wooden signboard carved with leaves - NO lettering at all - with a bundle of dried herbs tied to it, and a small lantern glows softly under the eaves. The door stands slightly ajar; warm amber light in the windows; bunches of herbs dry on the windowsills. By the wall a tub of water and a boot brush; a narrow, clean yard; behind the house a small pretty garden. The sky is a cool dusk wash. There are NO people and NO animals anywhere in the picture."),
 51: (51, "kerren_at_counter_v3", "scene", ["ker"], ["inn_in"],
   f"The common room of the inn from the interior reference, in the evening, EMPTY of guests: no other people, no animals. A medium-close view of the wooden counter with the barrels and bottle shelves behind it, bunches of herbs hanging from the beam, a lantern. Behind the counter stands the innkeeper. {KER} He is seen from the front, from the chest up above the counter, drawn large in front of the shelves, one hand resting on the counter. In THIS picture his wings are NOT visible at all: the view is tight and nothing is drawn behind his shoulders but the shelves. He watches the door, still and quiet."),
 52: (52, "kerren_wings_v3", "scene", ["ker"], ["inn_in","inn_prev"],
   f"The same empty common room and the same man as in the previous frame, now in a wider view that shows the whole counter, the barrels and the staircase on the right. {KER} Now clearly visible behind his shoulders: TWO large folded feathered wings with reddish-brown feathers, as in the character reference - the left wing folded easily, the right wing held slightly lower and stiffer. He is not an angel and has no halo: a quiet innkeeper of a winged people. The wings are the revelation of the picture."),
}
NEW = [
 (19, "nightjar_watches_bel_v2", "sketch", ["bel"], ["bird"],
   f"Near foreground, lower LEFT: the top rail of a rough wooden pole fence running across the sheet, and on it the same nightjar as in the reference - crouched LOW and HORIZONTAL, lying lengthwise along the rail exactly as in the reference, NOT sitting upright, NOT an owl. We see the bird from behind and slightly from the side; its flat head is turned toward the right and tilted a little, looking up at a woman. On the right, beyond the rail and a few steps away, drawn clearly from the waist up: {BEL} She is seen in three-quarter view looking off to the side, calm, with the faintest smile, unaware of the bird. The bird watches her."),
 (37, "varen_speaks", "sketch", ["var","tar"], [],
   f"{VAR} He is drawn large from the chest up in the left-middle of the sheet, speaking earnestly and gratefully to someone out of frame, one hand pressed to his chest, a tired, warm half-smile. Behind his shoulder, further back, smaller and fainter: {TAR} The old man stands listening with his hands folded and his eyes lowered, a small quiet smile under the beard."),
]
A = sorted([OV.get(a[0], a) for a in A] + NEW, key=lambda a: a[0])

# ---- вторая волна правок 06.10.2026: «картинки» вместо набросков -> жёсткий стиль, серые референсы ----
DENS["scene_ink"] = ("DENSITY - INK SCENE, NOT A PAINTING: a scene drawn with the pen first. The dark-brown ink line carries everything; "
    "colour is only a few PALE, flat washes laid over it. STRICTLY LIMITED PALETTE: sepia, ochre, warm grey-brown and one muted grey-green. "
    "NO blue anywhere, NO orange or purple sunset gradients, NO painted clouds, NO saturated colour. Sky and water are left as BARE PARCHMENT "
    "with only a few ink lines and at most one faint ochre wash for low sun. Shadows are light hatching, not dark paint. The drawing is a vignette: "
    "it fades into bare parchment well before the edges, and at least a third of the sheet stays empty. It must look like the SERIES STYLE reference, "
    "not like a finished illustration.")
S["series"] = ("ref_series_style.png", "SERIES STYLE reference - an approved frame of this series: match its line, its pale washes, its limited palette and how much bare parchment it leaves")
GEO = "a grey photo of the real place from the campaign - take ONLY the geography and architecture from it, nothing of its rendering"
S["road"] = ("ref_road_gray.jpg", GEO + " (forest on one side of the path, the river on the other, wooded hills beyond)")
S["gf_aerial"] = ("ref_greenford_aerial_gray.jpg", GEO + " (the village on the far bank of the river, fields beside it, forest around)")
S["lane"] = ("ref_lane_gray.jpg", GEO + " (half-timbered thatched houses along a rutted dirt lane)")
S["inn_in"] = ("ref_inn_interior_gray.jpg", GEO + " (counter with barrels and bottle shelves, hanging herbs, lantern, staircase on the right, stone floor)")
S["inn_prev"] = ("ref_inn_prev2.png", "the previous frame of this sequence; keep the room, the light and the man identical")
def _re(n, slug, style):
    a = [x for x in A if x[0] == n][0]
    return (n, slug, "scene_ink", a[3], style, a[5])
OV2 = {
 44: _re(44, "path_from_above_v3", ["series", "road"]),
 47: _re(47, "greenford_across_river_v4", ["series", "gf_aerial"]),
 50: _re(50, "inn_outside_v4", ["series", "lane"]),
 51: _re(51, "kerren_at_counter_v4", ["series", "inn_in"]),
 52: _re(52, "kerren_wings_v4", ["series", "inn_in", "inn_prev"]),
 48: (48, "ferry_v2", "scene_ink", [], ["series"],
   "A broad calm river at sunset, seen from the bank. A flat wooden rope ferry - a wide raft-like deck of planks with a low rail, guided along a thick rope that stretches across the river - is halfway across. On it four small figures drawn in ink, seen from behind and from the side: a ferryman at one end leaning on a long pole pushed down into the water, and three passengers - a woman with long dark hair in a cream dress, a man with white hair in a ponytail, a tall blond man in a long dark cassock. The far bank is a low line with a few thatched roofs and a landing. The low sun is only a pale ochre disc and one faint wash on the horizon; the water is bare parchment with a few horizontal ink lines and the broken reflection of the rope."),
 19: (19, "nightjar_watches_bel_v3", "sketch", ["bel"], ["bird"],
   "Near foreground, lower LEFT: the top rail of a rough wooden pole fence, and on it the same nightjar as in the reference - crouched LOW and HORIZONTAL, lying lengthwise along the rail exactly as in the reference, NOT upright, NOT an owl - seen from behind, its flat head turned and tilted, watching something far away. FAR in the distance on the right, at least twenty paces from the bird and no taller than a quarter of the sheet: the small figure of the elf woman with long blue-black hair in a cream dress, standing in three-quarter back view and looking the other way, entirely unaware of the bird. A wide stretch of empty parchment separates them. The bird is watching her from afar."),
}
A = sorted([OV2.get(a[0], a) for a in A], key=lambda a: a[0])

# ---- третья волна 06.10.2026: рост, рюкзаки, причёска Анканто, узнаваемые фигуры ----
HEI = "HEIGHTS (canon): Ankanto is the tallest of the three (185 cm), Mikael slightly shorter (179 cm), Bel clearly shorter than both men (170 cm)."
GEAR = "GEAR (canon): Ankanto carries one big travel pack on his back - he carries for himself and for Mikael; Bel carries her own backpack; Mikael carries nothing."
SM_BEL = "Bel - a slender elf woman with long blue-black wavy hair and pointed ears, in a cream off-shoulder dress"
SM_ANK = "Ankanto - a tanned young man with wavy WHITE hair half tied back into a short ponytail at the back of his head, loose strands at the face (NOT long loose hair, NOT grey, NOT an old man), ivory open-collar shirt, brown trousers"
SM_MIK = "Mikael - a fair man with SHORT blond hair swept back and a square clean-shaven face, in a long dark ankle-length cassock with a white collar tab"
TRIO = f"The three travellers must be recognisable even though they are small: {SM_BEL}; {SM_ANK}; {SM_MIK}. {HEI} {GEAR}"
OV3 = {
 42: (42, "nightjar_dawn_v2", "scene_ink", ["tar","var"], ["series","bird"],
   f"On a bare pine branch in the upper left foreground lies the same nightjar as in the reference - crouched LOW and HORIZONTAL along the branch, NOT upright, NOT an owl - looking down with weary patience. Far below, small in the frame, a fenced yard in front of a log cabin at dawn, with five small but recognisable people saying goodbye, and nobody else: an old white-bearded man in a long white robe (Tarven); a young chestnut-haired man in a white tunic with a small golden sun (Varen), who is being hugged by {SM_BEL}; and standing close beside them {SM_ANK}, and {SM_MIK}. They are these five people, not strangers; no hoods, no cloaks, no extra figures. {HEI} Low sun only as one pale ochre wash, long thin shadows drawn in ink."),
 44: (44, "path_from_above_v4", "scene_ink", ["bel","ank","mik"], ["series","road"],
   f"The place shown in the grey reference, seen from a high bank: a well-trodden dirt path runs away from the viewer along a broad calm river - dense old forest on the left of the path, the water on the right, wooded hills and rocky ridges across the river. On the path, walking away from the viewer in a row and drawn small, three travellers seen from behind. {TRIO}"),
 47: (47, "greenford_across_river_v5", "scene_ink", ["bel","ank","mik"], ["series","gf_aerial"],
   f"Sunset. The viewer stands on the NEAR bank of a broad river, where a forest road comes down to a small wooden ferry landing in the foreground - a short jetty, a mooring post, a rope stretching out over the water. The whole width of the river lies between the viewer and the village. On the FAR bank lies Greenford: a farming village of about a hundred half-timbered and thatched houses clustered together, with strips of fields and meadows beside it and forest behind, and its own landing with a few boats. On the near landing, seen FROM BEHIND and drawn small, the three travellers stand looking across the river; no other people and no animals anywhere. {TRIO}"),
 48: (48, "ferry_v3", "scene_ink", ["bel","ank","mik"], ["series"],
   f"A broad calm river at sunset, seen from the bank. A flat wooden rope ferry - a wide raft-like deck of planks with a low rail, guided along a thick rope that stretches across the river - is halfway across. On it four small figures drawn in ink: a ferryman in a hat at one end leaning on a long pole pushed down into the water, and three passengers standing together, seen from behind and from the side. {TRIO} The far bank is a low line with a few thatched roofs and a landing. The low sun is only a pale ochre disc and one faint wash on the horizon; the water is bare parchment with a few horizontal ink lines."),
}
A = sorted([OV3.get(a[0], a) for a in A], key=lambda a: a[0])

def build(a):
    n, slug, dens, chars, style, scene = a
    refs, lines = [], []
    for c in chars:
        f, name = R[c]; refs.append(f)
        lines.append(f"- {f}: CHARACTER reference for {name} - match this face exactly: same bone structure, features and hair. Also a reference for the drawing style and the paper. Do not copy its pose.")
    for s in style:
        f, what = S[s]; refs.append(f)
        lines.append(f"- {f}: STYLE reference only - {what}. Do not copy its subject or composition.")
    head = ("Attached reference images:\n" + "\n".join(lines)) if lines else "There are no reference images - work from the text only."
    body = "\n\n".join([head, LINE, PAPER, DENS[dens], "SCENE: " + scene, TAIL])
    return refs, body

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    md = ["# Жульничество — промпты для генерации (Sol через Codex)", "",
          "Порядок кадров и текст — в `02__Жульничество__раскадровка.md`. Номер здесь — номер **кадра**, не арта.",
          "Генерация: headless Codex, модель `gpt-6.1-sol`, встроенный image_gen. Файлы — `C:\\Azlanti\\Video\\Session0\\02__Жульничество\\shotNN_имя.png`.",
          "Референсы персонажей — `C:\\Azlanti\\Video\\References\\`. Тарвен в ink-стиле — `shot15_tarven` из ролика 1; деревня — `shot01_village_wide`; лист отчёта — `shot00c_report_sheet`; козодой — готовый кадр 8.",
          "", "Три плотности: **набросок** (фигуры крупно, фон намёком), **сцена** (полная сцена, но воздушная), **натюрморт** (только предметы).",
          "Кадры 39, 43 и интро — переиспользование, промптов нет. Референсы мест и Керрена — из Foundry, копии в C:/Azlanti/Video/References/foundry/.", "", "---", ""]
    names = {"sketch": "набросок", "scene": "сцена", "object": "натюрморт", "scene_ink": "сцена тушью (жёсткая палитра)"}
    for a in A:
        refs, body = build(a)
        n, slug = a[0], a[1]
        io.open(os.path.join(OUT, f"p_{n:02d}.txt"), "w", encoding="utf-8", newline="\n").write(body + "\n")
        io.open(os.path.join(OUT, f"r_{n:02d}.txt"), "w", encoding="utf-8", newline="\n").write(" ".join(refs) + "\n")
        io.open(os.path.join(OUT, f"n_{n:02d}.txt"), "w", encoding="utf-8", newline="\n").write(f"shot{n:02d}_{slug}.png\n")
        md += [f"## Кадр {n} — `shot{n:02d}_{slug}`", "",
               f"Плотность: **{names[a[2]]}**. Референсы: " + (", ".join(f"`{r}`" for r in refs) if refs else "нет"), "",
               "```", body, "```", "", "---", ""]
    io.open(MD, "w", encoding="utf-8", newline="\n").write("\n".join(md).rstrip() + "\n")
    print(len(A), "prompts; frames:", [a[0] for a in A])
