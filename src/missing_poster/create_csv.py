from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import random
import textwrap
from pathlib import Path
from typing import List, Tuple
import pandas as pd

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp")

attributes = {
    "Last Seen":    ["Declaring “one more drink” an hour ago","Convincing others to take shoots","Guarding the snack table with dedication","At the bar, Saying “I'll just have water (a known lie)","Chasing a pigeon “for research”","Emotionally attached to a houseplant","Whispering “it’s fine” to a clearly not fine situation","Texting their ex “by accident”","Making unrealistic life plans at 2 AM.","Stalking their crush’s Instagram"],
    "Last Words":   ["“One more drink won't hurt.”","“I'll be right back.”","“Just guarding the snacks.”","“I swear I will have water now.”","“This shot tastes like bad decisions.”","“Let’s just mix everything together.”","“What could possibly go wrong?”","“This is my song!”","“Why is the floor moving?”","“I can totally handle another round.”","“I just want a snack, not another drink.”","“I’m just gonna say hi real quick.”","“I think I offended someone but it’s fine.”","“I’m not drunk, I’m enlightened.”","“I thought this was the bathroom!”","“I regret nothing!”","“If I disappear, tell my story.”"],
    "Height":       ["Fun-sized","Emotionally tall","Unresonable confident for their size"],
    "Age":          ["Ageless","Eternally 21","Perpetually 25-something","Eternal","Reclassified as vintage","Emotionally 10","Forever young"],
    "Eyes":         ["Deadly but charming","Rolling since birth", "Powered by cahos coffein and alcohol","Magnetic","Beautiful but tired"],
    "Voice":        ["Audible chaos","Whispering secrets","Pure sarcasm","90% laugh 10% apology"],
    "Mood":         ["Approachable in theory,dangerous in practice","Overly enthusiastic","Unpredictable","Suspiciously friendly","Emiting main-character energy"],
    "Feature":      ["Runs on unstable code","Frequently distracted by snacks",""],
    "Classification": ["Chaos seeker","Snack driven lifeform","Attention magnet","Professional overthinker","Chronic people pleaser","Existentialist","Serial napper","Certified introvert","Meme enthusiast","Occasional philosopher","Full-time daydreamer"],
    "Weakness":     ["Free alcohol", "Snacks","Good music","Cute animals","Compliments","Gin Tonic","Songs from 2010","Any form of validation","Mornings","Work","Highly distractible by shiny objects","Reality"],
    "Nickname":     ["The DIVA","Shot-zilla","Social Butterfly","Beverage Bandite","Margarita Messiah","Dr. Dramatic","Sir Spills-a-Lot","Trust Me Guy","Hot Mess Express","Vodka Visionary","Beer Bard","Prosecco Princess","Sangria Sage","Shuffle Queen","Miss Technically Correct"],
    "Reward":       ["One high five", "Eternal gratitude","A firm handshake","Mild applause","A pat on the back","An awkward hug"],
    "Special Power":["Known to vanish mid-conversation","Summoning akward conversations","Can sleep anywhere, anytime.","Dramatic exits","Involuntary flirting aura","Regret postponement","Drunk text generation","Social chameleon","Hangover immunity","Eye contact avooidance","Existential Crisis summoning"],
    "Case note":    ["Investigation ongoing, morale low","Evidence suggests self-inflicted disappearance","Likely to reappear when food is served","Suspect left behind nothing but half a drink","Previously found hiding in plain sight","History of spontaneous dance-floor departures","Playlist may hold key evidence","Missing status upgraded to “vibing elsewhere”"],
    "Psycholocigal Profile":["Main character syndrom","Shows advanced coping through dance","Mild autism","ADHD symptoms detected","Uses humor as a defense mechanism","Borderline deluisional","Mild narcissm balanced by bad decisions","stable-ish, if fed"],
}


def get_font(size: int, bold: bool = False):
    font_candidates = [
        ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ("Arial Bold.ttf" if bold else "Arial.ttf"),
        ("Helvetica Bold.ttf" if bold else "Helvetica.ttf"),
    ]
    for fp in font_candidates:
        try:
            return ImageFont.truetype(fp, size=size)
        except Exception:
            pass
    return ImageFont.load_default()


def get_file_paths(directory:str, exts: Tuple[str]=IMAGE_EXTS) -> List[Path]:
    p = Path(directory)
    return [f for f in p.iterdir() if f.suffix.lower() in exts and f.is_file()]


def get_names(list_of_paths: List[Path]) -> List[str]:
    names = []
    for path in list_of_paths:
        name = path.stem.replace("_", " ").replace("-", " ").title()
        names.append(name)
    return names


def generate_filenumber() -> str:
    return str(random.randint(0, 99999999)).zfill(8)


def get_classification()->str|None:
    classifications = ["Cold Case","Endangered","Unsolved","Reopened","Top Secret","Do not Approach"]
    classifications = [random.choice(classifications),"X"] #Half the images dont have a classifiaction
    return random.choice(classifications)


def get_attributes(n_attributes:int,attributes:dict=attributes)->List[str]:
    selected_attributes = []
    keys = list(attributes.keys())
    if n_attributes > len(keys):
        raise Exception("Not enough attributes to sample from")
    sample_pool = [(key, val) for key, values in attributes.items() for val in values]
    for _ in range(n_attributes):
        key, val = random.choice(sample_pool)
        selected_attributes.append((key,val))
        sample_pool = [item for item in sample_pool if item[0] != key]

    return selected_attributes


def create_csv(in_file:str,out_file:str,out_dir:str,n_attributes:int,seed:int)->None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if seed is not None:
        random.seed(seed)
    columns = ["Name","Classification","File Number","Image Path"]
    #attributes_columns = []
    attribute_columns = [[f"Attributename {i}",f"Attribute {i}"] for i in range(n_attributes)]
    flat_attribute_list = [item for sublist in attribute_columns for item in sublist]
    columns += flat_attribute_list
    df = pd.DataFrame(columns=columns)
    file_paths = get_file_paths(Path(in_file))
    names = get_names(file_paths)
    for i,(name,filepath) in enumerate(zip(names,file_paths)):
        attrs = get_attributes(n_attributes=n_attributes,attributes=attributes)
        #print(attrs)
        classification = get_classification()
        file_number = generate_filenumber()
        data = [name,classification,file_number,str(filepath)]
        attr = [item for pair in attrs for item in pair]
        data += attr
        df.loc[i] = data
    output = out_dir / out_file
    df.to_csv(output,index=False,sep=";")
    print(f"CSV saved to {output}")
