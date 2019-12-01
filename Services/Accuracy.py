import re
from Models.Entry import Entry

def processing_accuracy(entries):
    num, N = 0.0, len(entries)
    if N == 0: return N

    filtered_entries = []
    for ent in entries:
        out = len(ent.gardinerSigns) == len(ent.glyphs)
        num += int(out)
        if out:
            filtered_entries.append(ent)
    return float(num) / N, filtered_entries

def get_entry_accuracy(targets, predictions):
    """
    Returns the % of pairs whose target and prediction are identical strings.
    """
    __err_check(targets, predictions)
    N = len(targets)
    if N == 0: return 0.0

    num = 0.0
    for i in range(N):
        if targets[i] == predictions[i]:
            num += 1.0
    return num / N

def get_order_accuracy(targets, predictions):
    """
    Gets the % of target/prediction pairs whose glyphs are in the same
    order, regardless of formatting.
    """
    __err_check(targets, predictions)
    N = len(targets)
    if N == 0: return 0.0

    num = 0.0
    for i in range(N):
        preproc_target = re.split("-|\(|\)|:", targets[i])
        preproc_pred = re.split("-|\(|\)|:", predictions[i])
        filter_empty = lambda x: x != ""
        preproc_target = list(filter(filter_empty, preproc_target))
        preproc_pred = list(filter(filter_empty, preproc_pred))
        preproc_target = " ".join(preproc_target)
        preproc_pred = " ".join(preproc_pred)
        if preproc_target == preproc_pred:
            num += 1.0
    return num / N

def get_glyph_accuracy(targets, predictions):
    """
    Gets the % of all glyph-blocks in the target/prediction pairs
    whose formatting and glyph order are both correct.
    """
    __err_check(targets, predictions)
    N = len(targets)
    if N == 0: return 0.0

    num = 0.0
    den = 0.0
    for i in range(N):
        target = targets[i].split('-')
        pred = predictions[i].split('-')

        # Should do target-in-pred instead of walking over both.
        # While slower, eliminates case of incorrect segmentation
        # w/ different length lists.
        for block in target:
            den += 1.0
            if block in pred:
                num += 1.0
    return num / den

def __err_check(targets, predictions):
    assert len(targets) == len(predictions)
    assert targets is not None and predictions is not None