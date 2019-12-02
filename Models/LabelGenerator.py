# glyph = gardiners,glyphs
def generateLabel(glyphs):
    glyphs = sorted(glyphs, key = lambda x: x[1].left)
    output = ""
    #[A1,B2,C3]
    #[G1,G2,G3]
    prev = None
    blocks = []
    for gardiner,glyph in glyphs:
        if blocks == []:
            blocks.append([(gardiner,glyph)])
            continue
        leftMostGlyph = sorted(blocks[len(blocks)-1], key = lambda x: -(x[1].right))[0][1]
        #Zero overlap, create new block
        if leftMostGlyph.right < glyph.left:
            blocks.append([(gardiner,glyph)])
        else:
            blocks[len(blocks)-1].append((gardiner,glyph))
        
    for block in blocks:
        if len(output) > 0 :
            output += "-"
        if len(block) == 1:
            gardiner = block[0][0]
            output += "(" + gardiner + ")"
        elif len(block) == 2:
            gard1,glyph1 = block[0][0], block[0][1]
            gard2,glyph2 = block[1][0], block[1][1]
            if glyph1.upper < glyph2.upper:
                output += "(" +gard1 + ":" + gard2+ ")"
            else:
                output += "(" +gard2 + ":" + gard1+ ")"
        elif len(block) == 3:
            #INSERT THE CASE OF 3 VERTICALS
            verticalSort = sorted(block, key = lambda x: x[1].upper)
            #vertical stack check
            if verticalSort[0][1].lower < verticalSort[1][1].upper and verticalSort[1][1].lower < verticalSort[2][1].upper:
                output += "(" + verticalSort[0][0] + ":" + verticalSort[1][0] + ":" + verticalSort[2][0] + ")"
                continue

            widestSort = sorted(block, key = lambda x: -(x[1].width))
            widest,first,second = widestSort[0][1],widestSort[1][1],widestSort[2][1]
            #Widest is above the other two
            if widest.lower < first.upper and widest.lower < second.upper:
                if first.left < second.left:
                    output +=  "(" + widestSort[0][0] + ":" + "(" + widestSort[1][0] + "-" + widestSort[2][0] + ")" + ")"
                else:
                    output += widestSort[0][0] + ":" + "(" + widestSort[2][0] + "-" + widestSort[1][0] + ")"
            #Widest is below the other two.
            else:
                if first.left < second.left:
                    output += "(" + "(" + widestSort[1][0] + "-" + widestSort[2][0] + ")" + ":" + widestSort[0][0]+ ")"
                else:
                    output += "(" + "(" + widestSort[2][0] + "-" + widestSort[1][0] + ")" + ":" + widestSort[0][0]+ ")"
        elif len(block) == 4:
            verticalSort = sorted(block, key = lambda x: x[1].upper)
            widestSort = sorted(block, key = lambda x: -(x[1].width))
            innerBlocks = []
            for glyph in verticalSort:
                if innerBlocks == []:
                    innerBlocks.append([glyph])
                    continue
                lastBlockLowestGlyph = sorted(innerBlocks[len(innerBlocks)-1], key = lambda x: -x[1].lower )[0][1]
                if glyph[1].upper < lastBlockLowestGlyph.lower:
                    innerBlocks[len(innerBlocks)-1].append(glyph)
                else:
                    innerBlocks.append([glyph])
            output += "("
            puts = []
            for innerBlock in innerBlocks:
                lrSort = sorted(innerBlock, key = lambda x: x[1].left)
                gardinersSorted = [gardiner for gardiner,glyph in lrSort]
                puts.append( "("+ "-".join(gardinersSorted) + ")" )
            output += ":".join(puts)
            output += ")"
    print(output)