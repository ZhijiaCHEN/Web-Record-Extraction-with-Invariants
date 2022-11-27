import argparse
from univeral_tree import build_lxml_tree, StructTree
from lxml import html
import os

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='Input HTML file.')
    parser.add_argument('--output', type=str, default='output.html', help='Output HTML file.')
    parser.add_argument(
        '--encoding', 
        type=str, 
        choices=[StructTree.STRUCT_PATTERN, StructTree.NODE_SIGNATURE_PATTERN, StructTree.HTP_PATTERN, StructTree.TAG_PATTERN],
        default=StructTree.STRUCT_PATTERN, 
        help='The encoding scheme for nodes on the DOM tree, should be one of "tag" (encode by tag name), "signature" (encode by node signature), "htp" (encode by HTML Tag Path), and "structure" (encode by subtree structure). Defaults to "structure".'
    )
    parser.add_argument(
        '--len-thresh', 
        type=int, 
        default=3,
        help='Pattern length threshold. Default to 3.'
    )
    parser.add_argument(
        '--freq-thresh', 
        type=int, 
        default=3,
        help='Pattern frequency threshold. Default to 3.'
    )
    parser.add_argument(
        '--record-height-thresh', 
        type=int,
        default=2,
        help='Subtree height threshold for target records. Default to 2.'
    )
    parser.add_argument(
        '--record-size-thresh', 
        type=int, 
        default=2,
        help='Subtree size threshold for target records. Default to 2.'
    )
    parser.add_argument(
        '--greedy-pattern', 
        action='store_true',
        dest='greedy',
        help='Search frequent patterns with greedy strategy.'
    )
    parser.add_argument(
        '--evaluate-xpath', 
        type=str, 
        help='XPath for the ground truth of record container nodes.'
    )
    return parser.parse_args()

def elm2text(e):
    textElm = [x for x in e.xpath('descendant-or-self::*[@data-index]') if x.text is not None] # only consider elements that are touched
    return ' '.join([x.text.strip() for x in textElm]).strip()

args = get_args()

def run_one(inputPath, outputPath, evaluate_xpath = None):
    hitCnt = missCnt = mistakeCnt = 0
    with open(inputPath, encoding='utf-8') as file:
        eTree = build_lxml_tree(file.read())
        if evaluate_xpath is not None:
            golden = eTree.xpath(evaluate_xpath)
            if len(golden) == 0:
                print('No element found using the XPath {evaluate_xpath} for {inputPath}.')
                return -1, -1, -1
        sTree = StructTree(eTree, pattern_method=args.encoding)
        recordGroups = sTree.record_boundary(
            lenThresh=args.len_thresh, 
            freqThresh=args.freq_thresh, 
            recordHeightThresh=args.record_height_thresh, 
            recordSizeThresh=args.record_size_thresh, 
            greedyPattern=(args.greedy),
        )
        if evaluate_xpath is None:
            for i, recordIndexes in enumerate(recordGroups):
                for i in recordIndexes:
                    sTree[i].elm.attrib["data-record-{i}"] = ""
                    sTree[i].elm.attrib["style"] = "border: dashed darkgreen;"
        else:
            index2text = {}
            annotatedTexts = set()
            for e in golden:
                t = elm2text(e)
                index2text[int(e.attrib['data-index'])] = t
                annotatedTexts.add(t)

            # only evaluate records regions that have intersection with ground truth
            detectedIndexes = set()
            for recordIndexes in recordGroups:
                groupTexts = set()
                for i in recordIndexes:
                    e = sTree[i].elm
                    t = elm2text(e)
                    index2text[i] = t
                    groupTexts.add(t)
                if len(groupTexts.intersection(annotatedTexts)) > 0:
                    detectedIndexes.update(set(recordIndexes))
            
            hit = set()
            miss = set()
            mistake = set()
            detectedTexts = set()
            for i in detectedIndexes:
                t = index2text[i]
                detectedTexts.add(t)
                if len(t) == 0:
                    continue
                if t in annotatedTexts:
                    sTree[i].elm.attrib["style"] = "border: dashed darkgreen;"
                    sTree[i].elm.attrib["data-record-hit"] = "1"
                    hit.add(t)
                else:
                    sTree[i].elm.attrib["style"] = "border: dashed yellow;"
                    sTree[i].elm.attrib["data-record-mistake"] = "1"
                    mistake.add(t)
            for e in golden:
                t = index2text[int(e.attrib['data-index'])]
                if len(t) == 0:
                    continue
                if t not in detectedTexts:
                    e.attrib["style"] = "border: dashed red;"
                    e.attrib["data-record-miss"] = "1"
                    miss.add(t)
            hitCnt = len(hit)
            missCnt = len(miss)
            mistakeCnt = len(mistake)
            if mistakeCnt > 10:
                print(inputPath)
        with open(outputPath, 'wb') as f:
            f.write(html.tostring(eTree, pretty_print=True, encoding='utf-8'))
        return hitCnt, missCnt, mistakeCnt

if __name__ == '__main__':
    assert os.path.isfile(args.input) and args.input.split('.')[-1] == 'html', "Expecting input to be an HTML file, or a folder containing HTML files."
    hitCnt, missCnt, mistakeCnt = run_one(args.input, args.output, evaluate_xpath=args.evaluate_xpath)
    if args.evaluate_xpath is not None:
        print(f"Results on {args.input}: Recall = {0 if (hitCnt + missCnt) == 0 else hitCnt/(hitCnt + missCnt):.2f}, precision = {0 if (hitCnt + mistakeCnt) == 0 else hitCnt/ (hitCnt + mistakeCnt):.2f}.")

