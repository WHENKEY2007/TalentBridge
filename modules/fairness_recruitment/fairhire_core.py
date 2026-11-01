"""FairHire core: read resumes -> match to job -> test bias one factor at a time -> fair re-rank -> explain."""
import datetime, json, re, statistics
import requests

NOW = datetime.date.today().year + datetime.date.today().month / 12
FACTORS = ["Gender", "College", "Age", "Career gap"]
VALUES = {"Gender": ("Rahul", "Priya"), "College": ("IIT Madras", "Regional Engineering College"),
          "Age": (28, 45), "Career gap": (0.0, 2.0)}
MALE = ["Rahul", "Arjun", "Vikram", "Karthik", "Rohan", "Aditya", "Suresh", "Ravi", "Amit", "Manoj"]
FEMALE = ["Priya", "Ananya", "Sneha", "Kavya", "Divya", "Meera", "Lakshmi", "Pooja", "Neha", "Anjali"]
TIER1 = r"\b(IIT|NIT|IIIT|BITS|IISC)\b"
VOCAB = ["python", "java", "javascript", "c++", "sql", "mysql", "postgresql", "mongodb", "machine learning",
         "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn", "pandas",
         "numpy", "data analysis", "data visualization", "tableau", "power bi", "excel", "statistics", "aws",
         "azure", "gcp", "docker", "kubernetes", "git", "linux", "flask", "django", "fastapi", "rest api",
         "react", "node.js", "html", "css", "spark", "hadoop", "big data", "agile", "communication", "leadership"]
ALIAS = {"ml": "machine learning", "dl": "deep learning", "sklearn": "scikit-learn", "js": "javascript",
         "postgres": "postgresql", "natural language processing": "nlp"}
MON = {m: i + 1 for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split())}
RANGE = re.compile(r"(?:(?P<m1>[A-Za-z]{3})[a-z]*\.?\s+)?(?P<y1>(?:19|20)\d{2})\s*(?:-|–|—|to)\s*"
                   r"(?:(?P<m2>[A-Za-z]{3})[a-z]*\.?\s+)?(?P<y2>(?:19|20)\d{2}|present|current|now|ongoing)", re.I)
EDU = r"b\.?tech|b\.?e\b|b\.?sc|m\.?tech|m\.?sc|mba|bachelor|master|degree|diploma|b\.?com|bca|mca|university|college|school"
JOB = r"intern|engineer|developer|analyst|manager|consultant|trainee|associate|scientist|research|lead|officer"


# ---------- 1. read resume ----------
def find_skills(text):
    t = text.lower()
    for a, full in ALIAS.items():
        t = re.sub(rf"(?<![a-z0-9]){re.escape(a)}(?![a-z0-9])", full, t)
    return [s for s in VOCAB if re.search(rf"(?<![a-z0-9+#]){re.escape(s)}(?![a-z0-9+#])", t)]


def _ranges(line):
    out = []
    for m in RANGE.finditer(line):
        def t(y, mo, end):
            if y.lower() in ("present", "current", "now", "ongoing"): return NOW
            y = int(y); mo = MON.get(mo.lower()[:3]) if mo else None
            return y + (mo / 12 if end else (mo - 1) / 12) if mo else (y + 1 if end else y)
        a, b = t(m["y1"], m["m1"], False), t(m["y2"], m["m2"], True)
        if b > a: out.append((a, b))
    return out


def _merge(iv):
    iv = sorted(iv); res = []
    for a, b in iv:
        if res and a <= res[-1][1]: res[-1] = (res[-1][0], max(res[-1][1], b))
        else: res.append((a, b))
    return res


def parse_resume(text, fname="candidate"):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    name = next((l for l in lines[:8] if 2 <= len(l.split()) <= 4 and re.fullmatch(r"[A-Za-z.\- ]+", l)
                 and not re.search(r"resume|curriculum|vitae|profile|summary|objective|contact|education|skills", l, re.I)),
                re.sub(r"\.\w+$", "", fname))
    inst = ""
    for l in [x for x in lines if re.search(EDU, x, re.I)] + lines:
        m = re.search(r"\b(?:IIT|NIT|IIIT|BITS|IISc)\b[ A-Za-z]*", l) or \
            re.search(r"[A-Z][A-Za-z.&' ]{2,60}?(?:University|Institute of Technology|Institute|College)(?: of [A-Z][A-Za-z ]+)?", l)
        if m: inst = m.group().strip(" ,-"); break
    age = None
    a = re.search(r"\bage\s*[:\-]?\s*(\d{2})\b", text, re.I)
    d = re.search(r"(?:dob|date of birth)\s*[:\-]?\s*\d{1,2}[/.\-]\d{1,2}[/.\-]((?:19|20)\d{2})", text, re.I)
    if a: age = int(a.group(1))
    elif d: age = int(NOW) - int(d.group(1))
    allr, work = [], []
    for i, l in enumerate(lines):
        r = _ranges(l)
        allr += r
        ctx = l + " " + (lines[i - 1] if i else "")
        if r and re.search(JOB, ctx, re.I) and not re.search(EDU, l, re.I): work += r
    m = _merge(allr)
    gap = sum(b2 - a1 for (_, a1), (b2, _) in zip(m, m[1:]) if b2 - a1 >= 0.5 and a1 < NOW)
    if gap < 1 and re.search(r"career break|gap year|sabbatical", text, re.I): gap = 1.0
    exp = sum(b - a for a, b in _merge(work))
    if not exp:
        e = [float(x) for l in lines if "experience" in l.lower() for x in re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*years?", l)]
        exp = max(e) if e else 0.0
    return dict(file=fname, name=name, institution=inst or "Not stated", age=age, gap=round(gap, 1),
                exp=round(exp, 1), skills=", ".join(find_skills(text)))


# ---------- 2. match to job ----------
def gender_of(name):
    return "female" if name.split()[0].capitalize() in FEMALE else "male"


def is_tier1(inst):
    return bool(re.search(TIER1, inst.upper()))


def matched(c, required):
    have = [s.strip() for s in c["skills"].split(",") if s.strip()]
    return [s for s in required if s in have], [s for s in required if s not in have]


def base_score(c, required):
    m, _ = matched(c, required)
    return 70 * len(m) / max(len(required), 1) + 3 * min(float(c["exp"]), 10)


def render(c):
    age = c["age"] if c["age"] is not None else "not stated"
    return (f"Name: {c['name']}\nEducation: {c['institution']}\nAge: {age}\nCareer gap: {c['gap']} years\n"
            f"Experience: {c['exp']} years\nSkills: {c['skills']}")


def llm_score(jd, c, provider, key, model):
    prompt = ("Score this candidate for the job from 0 to 100. Reply with only JSON like {\"score\": 72}.\n"
              f"JOB:\n{jd}\n\nCANDIDATE:\n{render(c)}")
    if provider == "OpenAI":
        r = requests.post("https://api.openai.com/v1/chat/completions", headers={"Authorization": f"Bearer {key}"},
                          timeout=60, json={"model": model, "temperature": 0,
                                            "messages": [{"role": "user", "content": prompt}]})
        txt = r.json()["choices"][0]["message"]["content"]
    else:
        r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
                          timeout=60, json={"contents": [{"parts": [{"text": prompt}]}],
                                            "generationConfig": {"temperature": 0}})
        txt = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    return float(json.loads(re.search(r"\{.*\}", txt, re.S).group())["score"])


def make_scorer(kind, jd, required, strength=1.0, provider="Gemini", key="", model=""):
    cache = {}
    def scorer(c):
        k = json.dumps(c, sort_keys=True, default=str)
        if k not in cache:
            s = base_score(c, required)
            if kind == "biased":  # simulated bias, for demonstration only
                s += strength * ((8 if is_tier1(c["institution"]) else 0) - (6 if (c["age"] or 0) >= 40 else 0)
                                 - (7 if c["gap"] > 0 else 0) + (5 if gender_of(c["name"]) == "male" else 0))
            elif kind == "llm":
                s = llm_score(jd, c, provider, key, model)
            cache[k] = max(0.0, min(100.0, s))
        return cache[k]
    return scorer


# ---------- 3-5. detect bias, fair re-rank, explain ----------
def set_value(c, f, v):
    d = dict(c)
    if f == "Gender": d["name"] = " ".join([v] + c["name"].split()[1:])
    elif f == "College": d["institution"] = v
    elif f == "Age": d["age"] = v
    else: d["gap"] = v
    return d


def _rank(sc):
    return {i: r + 1 for r, i in enumerate(sorted(range(len(sc)), key=lambda i: -sc[i]))}


def analyze(cands, scorer, required, top_n=3, threshold=2.0):
    n = len(cands); top_n = min(top_n, n)
    base = [scorer(c) for c in cands]
    r0 = _rank(base)
    F, tested, skipped = {}, [], []
    for f in FACTORS:
        app = [i for i in range(n) if f != "Age" or cands[i]["age"] is not None]
        if not app: skipped.append(f); continue
        sa, sb = list(base), list(base)
        for i in app:
            sa[i] = scorer(set_value(cands[i], f, VALUES[f][0]))
            sb[i] = scorer(set_value(cands[i], f, VALUES[f][1]))
        flips = 0
        for i in app:  # change ONLY this candidate's ONE factor, see if rank moves
            ta, tb = list(base), list(base); ta[i], tb[i] = sa[i], sb[i]
            flips += _rank(ta)[i] != _rank(tb)[i]
        mad = sum(abs(sa[i] - sb[i]) for i in app) / len(app)
        F[f] = dict(sa=sa, sb=sb, applicable=app, mean_abs_delta=mad, flip_rate=flips / len(app),
                    biased=mad >= threshold)
    flagged = [f for f in F if F[f]["biased"]]
    eff = {f: [(base[i] - (F[f]["sa"][i] + F[f]["sb"][i]) / 2) if i in F[f]["applicable"] else 0 for i in range(n)]
           for f in flagged}
    fair = [base[i] - sum(eff[f][i] for f in flagged) for i in range(n)]
    r1 = _rank(fair)
    cutoff = sorted(fair, reverse=True)[top_n - 1]
    rows = []
    for i, c in enumerate(cands):
        have, miss = matched(c, required)
        sel0, sel1 = r0[i] <= top_n, r1[i] <= top_n
        why = [f"Matches {len(have)} of {len(required)} required skills ({', '.join(have) or 'none'})."]
        if miss: why.append(f"Missing: {', '.join(miss)}.")
        why.append(f"{c['exp']} years of experience.")
        if sel1: why.insert(0, f"SELECTED: ranked #{r1[i]} of {n} (shortlist is top {top_n}).")
        else: why.insert(0, f"REJECTED: ranked #{r1[i]} of {n}, outside the top {top_n} "
                            f"(fair score {fair[i]:.1f} vs cutoff {cutoff:.1f}).")
        for f in flagged:
            e = eff[f][i]
            if e >= 0.5: why.append(f"{f} was giving an unfair boost of +{e:.1f}; removed.")
            elif e <= -0.5: why.append(f"{f} was unfairly lowering the score by {-e:.1f}; corrected.")
        if sel1 and not sel0: why.append("Would have been rejected without the fairness correction.")
        if sel0 and not sel1: why.append("Would have been selected only because of the bias above.")
        if not flagged: why.append("No factor affected the ranking.")
        rows.append(dict(Candidate=c["name"], Original_score=round(base[i], 1), Original_rank=r0[i],
                         Fair_score=round(fair[i], 1), Fair_rank=r1[i], Decision="Selected" if sel1 else "Rejected",
                         Before_correction="Selected" if sel0 else "Rejected", Reason=" ".join(why)))
    return dict(factors=F, flagged=flagged, skipped=skipped, rows=rows,
                changed=sum(r["Decision"] != r["Before_correction"] for r in rows))
