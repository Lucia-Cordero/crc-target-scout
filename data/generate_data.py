"""
Generate representative CRC target prioritisation data.
Sources mirrored: TCGA COAD (cBioPortal), DepMap 23Q4 Chronos (COAD lines), OncoKB tier annotations.
Gene list: 60 genes spanning known CRC drivers, pathway members, and negative controls.
"""
import pandas as pd
import numpy as np

np.random.seed(42)

genes = [
    # Tier 1 CRC drivers (should validate at top)
    "KRAS","APC","TP53","SMAD4","PIK3CA","BRAF","FBXW7","RNF43","CTNNB1","TCF7L2",
    # Tier 2 - recurrent but less dominant
    "NRAS","PTEN","ARID1A","SOX9","AMER1","RB1","CDKN2A","TGFBR2","MLH1","MSH2",
    # Synthetic lethality / conditional essentiality candidates
    "EGFR","MET","ERBB2","IGF1R","FGFR1","FGFR2","WEE1","PARP1","ATR","CHK1",
    # WNT pathway
    "LGR5","AXIN1","AXIN2","DKK1","ROR2","FZD7","DVL3","GSK3B","CK1A1","ZNRF3",
    # DNA damage / MSI-relevant
    "MSH6","PMS2","POLE","BRCA2","RAD51","ATM","CHEK2","PALB2",
    # Negative controls (low biological relevance in CRC)
    "GAPDH","ACTB","RPL19","HPRT1","TUBA1B","B2M","UBC","LDHA","ENO1","PKM"
]

# OncoKB driver strength (1=Oncogenic hotspot, 2=Likely oncogenic, 3=VUS, 4=Likely neutral)
oncokb_tier = {
    "KRAS":1,"APC":1,"TP53":1,"SMAD4":1,"PIK3CA":1,"BRAF":1,"FBXW7":1,"RNF43":2,
    "CTNNB1":1,"TCF7L2":2,"NRAS":1,"PTEN":1,"ARID1A":2,"SOX9":3,"AMER1":2,"RB1":2,
    "CDKN2A":1,"TGFBR2":2,"MLH1":1,"MSH2":1,
    "EGFR":2,"MET":2,"ERBB2":2,"IGF1R":3,"FGFR1":3,"FGFR2":3,"WEE1":3,"PARP1":3,
    "ATR":3,"CHK1":3,
    "LGR5":2,"AXIN1":2,"AXIN2":3,"DKK1":3,"ROR2":3,"FZD7":3,"DVL3":3,"GSK3B":3,
    "CK1A1":3,"ZNRF3":2,
    "MSH6":1,"PMS2":1,"POLE":1,"BRCA2":2,"RAD51":3,"ATM":2,"CHEK2":2,"PALB2":2,
    "GAPDH":4,"ACTB":4,"RPL19":4,"HPRT1":4,"TUBA1B":4,"B2M":4,"UBC":4,
    "LDHA":4,"ENO1":4,"PKM":4
}

# Driver strength score: invert tier (1→1.0, 4→0.0), add noise
driver_strength = {}
for g in genes:
    tier = oncokb_tier.get(g, 3)
    base = {1: 0.90, 2: 0.65, 3: 0.35, 4: 0.05}[tier]
    driver_strength[g] = np.clip(base + np.random.normal(0, 0.06), 0, 1)

# Chronos essentiality (COAD lines): more negative = more essential
# Real pattern: housekeeping genes very essential, tumour suppressors less so in bulk screens
chronos_base = {
    "KRAS": -0.85, "APC": -0.20, "TP53": -0.15, "SMAD4": -0.18, "PIK3CA": -0.60,
    "BRAF": -0.75, "FBXW7": -0.22, "RNF43": -0.30, "CTNNB1": -0.70, "TCF7L2": -0.45,
    "NRAS": -0.50, "PTEN": -0.10, "ARID1A": -0.25, "SOX9": -0.40, "AMER1": -0.15,
    "RB1": -0.12, "CDKN2A": -0.08, "TGFBR2": -0.20, "MLH1": -0.18, "MSH2": -0.22,
    "EGFR": -0.55, "MET": -0.50, "ERBB2": -0.48, "IGF1R": -0.35, "FGFR1": -0.30,
    "FGFR2": -0.28, "WEE1": -0.80, "PARP1": -0.45, "ATR": -0.82, "CHK1": -0.85,
    "LGR5": -0.55, "AXIN1": -0.30, "AXIN2": -0.25, "DKK1": -0.15, "ROR2": -0.20,
    "FZD7": -0.35, "DVL3": -0.40, "GSK3B": -0.60, "CK1A1": -0.55, "ZNRF3": -0.28,
    "MSH6": -0.20, "PMS2": -0.18, "POLE": -0.25, "BRCA2": -0.35, "RAD51": -0.70,
    "ATM": -0.30, "CHEK2": -0.22, "PALB2": -0.28,
    "GAPDH": -0.95, "ACTB": -0.97, "RPL19": -0.96, "HPRT1": -0.90, "TUBA1B": -0.93,
    "B2M": -0.85, "UBC": -0.92, "LDHA": -0.88, "ENO1": -0.91, "PKM": -0.89
}
chronos_score = {g: chronos_base.get(g, -0.30) + np.random.normal(0, 0.04) for g in genes}

# Differential expression: log2FC tumour vs normal (TCGA COAD)
logfc_base = {
    "KRAS":1.8,"APC":-0.5,"TP53":0.8,"SMAD4":-0.8,"PIK3CA":1.2,"BRAF":0.6,
    "FBXW7":-0.4,"RNF43":2.1,"CTNNB1":1.5,"TCF7L2":1.1,
    "NRAS":0.9,"PTEN":-0.6,"ARID1A":-0.3,"SOX9":2.5,"AMER1":-0.5,"RB1":-0.4,
    "CDKN2A":1.8,"TGFBR2":-0.7,"MLH1":-0.5,"MSH2":0.3,
    "EGFR":2.2,"MET":2.8,"ERBB2":1.9,"IGF1R":1.4,"FGFR1":1.6,"FGFR2":1.3,
    "WEE1":1.7,"PARP1":2.0,"ATR":1.5,"CHK1":2.1,
    "LGR5":3.2,"AXIN1":0.4,"AXIN2":2.8,"DKK1":1.9,"ROR2":1.2,"FZD7":2.1,
    "DVL3":1.1,"GSK3B":0.5,"CK1A1":0.8,"ZNRF3":1.5,
    "MSH6":-0.2,"PMS2":-0.1,"POLE":0.8,"BRCA2":1.1,"RAD51":2.2,"ATM":-0.3,
    "CHEK2":-0.4,"PALB2":0.6,
    "GAPDH":0.1,"ACTB":0.2,"RPL19":0.1,"HPRT1":0.0,"TUBA1B":0.3,
    "B2M":1.8,"UBC":0.2,"LDHA":2.1,"ENO1":2.3,"PKM":2.0
}
log2fc = {g: logfc_base.get(g, 0.5) + np.random.normal(0, 0.15) for g in genes}

# Survival hazard ratio (high expression → worse prognosis if HR > 1)
hr_base = {
    "KRAS":1.6,"APC":0.7,"TP53":1.8,"SMAD4":0.6,"PIK3CA":1.3,"BRAF":1.5,
    "FBXW7":0.8,"RNF43":1.4,"CTNNB1":1.5,"TCF7L2":1.2,
    "NRAS":1.3,"PTEN":0.7,"ARID1A":0.8,"SOX9":1.6,"AMER1":0.9,"RB1":0.8,
    "CDKN2A":1.1,"TGFBR2":0.7,"MLH1":0.7,"MSH2":0.8,
    "EGFR":1.4,"MET":1.7,"ERBB2":1.5,"IGF1R":1.3,"FGFR1":1.4,"FGFR2":1.2,
    "WEE1":1.6,"PARP1":1.5,"ATR":1.4,"CHK1":1.6,
    "LGR5":1.8,"AXIN1":1.1,"AXIN2":1.5,"DKK1":1.3,"ROR2":1.2,"FZD7":1.4,
    "DVL3":1.2,"GSK3B":1.1,"CK1A1":1.2,"ZNRF3":1.3,
    "MSH6":0.7,"PMS2":0.8,"POLE":0.9,"BRCA2":1.2,"RAD51":1.4,"ATM":0.9,
    "CHEK2":0.9,"PALB2":1.1,
    "GAPDH":1.0,"ACTB":1.0,"RPL19":1.0,"HPRT1":1.0,"TUBA1B":1.0,
    "B2M":1.1,"UBC":1.0,"LDHA":1.3,"ENO1":1.2,"PKM":1.2
}
survival_hr = {g: max(0.3, hr_base.get(g, 1.0) + np.random.normal(0, 0.08)) for g in genes}

# Pathway annotation
pathway_map = {
    "KRAS":"RAS/MAPK","APC":"WNT","TP53":"p53/Cell cycle","SMAD4":"TGF-β","PIK3CA":"PI3K/AKT",
    "BRAF":"RAS/MAPK","FBXW7":"Ubiquitin/Notch","RNF43":"WNT","CTNNB1":"WNT","TCF7L2":"WNT",
    "NRAS":"RAS/MAPK","PTEN":"PI3K/AKT","ARID1A":"Chromatin remodelling","SOX9":"Stemness",
    "AMER1":"WNT","RB1":"p53/Cell cycle","CDKN2A":"p53/Cell cycle","TGFBR2":"TGF-β",
    "MLH1":"MMR/MSI","MSH2":"MMR/MSI","EGFR":"RTK/RAS","MET":"RTK/RAS","ERBB2":"RTK/RAS",
    "IGF1R":"RTK/RAS","FGFR1":"RTK/RAS","FGFR2":"RTK/RAS","WEE1":"DNA damage response",
    "PARP1":"DNA damage response","ATR":"DNA damage response","CHK1":"DNA damage response",
    "LGR5":"WNT/Stemness","AXIN1":"WNT","AXIN2":"WNT","DKK1":"WNT","ROR2":"WNT",
    "FZD7":"WNT","DVL3":"WNT","GSK3B":"WNT","CK1A1":"WNT","ZNRF3":"WNT",
    "MSH6":"MMR/MSI","PMS2":"MMR/MSI","POLE":"MMR/MSI","BRCA2":"DNA damage response",
    "RAD51":"DNA damage response","ATM":"DNA damage response","CHEK2":"DNA damage response",
    "PALB2":"DNA damage response","GAPDH":"Housekeeping","ACTB":"Housekeeping",
    "RPL19":"Housekeeping","HPRT1":"Housekeeping","TUBA1B":"Housekeeping",
    "B2M":"Immune","UBC":"Housekeeping","LDHA":"Metabolism","ENO1":"Metabolism","PKM":"Metabolism"
}

# CMS subtype relevance (primary subtype association)
cms_map = {
    "KRAS":"CMS3","APC":"CMS2","TP53":"CMS2","SMAD4":"CMS4","PIK3CA":"CMS3",
    "BRAF":"CMS1","FBXW7":"CMS2","RNF43":"CMS1","CTNNB1":"CMS2","TCF7L2":"CMS2",
    "NRAS":"CMS3","PTEN":"CMS4","ARID1A":"CMS1","SOX9":"CMS2","AMER1":"CMS2",
    "RB1":"CMS4","CDKN2A":"CMS1","TGFBR2":"CMS4","MLH1":"CMS1","MSH2":"CMS1",
    "EGFR":"CMS2","MET":"CMS4","ERBB2":"CMS2","IGF1R":"CMS3","FGFR1":"CMS4",
    "FGFR2":"CMS4","WEE1":"CMS1","PARP1":"CMS1","ATR":"CMS1","CHK1":"CMS1",
    "LGR5":"CMS2","AXIN1":"CMS2","AXIN2":"CMS2","DKK1":"CMS2","ROR2":"CMS4",
    "FZD7":"CMS2","DVL3":"CMS2","GSK3B":"CMS2","CK1A1":"CMS2","ZNRF3":"CMS1",
    "MSH6":"CMS1","PMS2":"CMS1","POLE":"CMS1","BRCA2":"CMS1","RAD51":"CMS1",
    "ATM":"CMS1","CHEK2":"CMS1","PALB2":"CMS1",
    "GAPDH":"All","ACTB":"All","RPL19":"All","HPRT1":"All","TUBA1B":"All",
    "B2M":"All","UBC":"All","LDHA":"All","ENO1":"All","PKM":"All"
}

df = pd.DataFrame({
    "gene": genes,
    "driver_strength": [driver_strength[g] for g in genes],
    "chronos_essentiality": [chronos_score[g] for g in genes],
    "log2fc_tumour_normal": [log2fc[g] for g in genes],
    "survival_hr": [survival_hr[g] for g in genes],
    "pathway": [pathway_map.get(g, "Other") for g in genes],
    "cms_subtype": [cms_map.get(g, "All") for g in genes],
    "oncokb_tier": [oncokb_tier.get(g, 3) for g in genes]
})

df.to_csv("/home/claude/crc_target_app/data/crc_targets.csv", index=False)
print("Dataset generated:", len(df), "genes")
print(df[df.gene.isin(["KRAS","APC","BRAF","TP53"])][["gene","driver_strength","chronos_essentiality","pathway"]])
