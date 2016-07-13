from lxml import etree
import puz
import re

#xwd_url = "The Hindu Crossword 11718 - The Hindu.html"
#xwd_url = 'http://www.thehindu.com/crossword/the-hindu-crossword-11718/article8686670.ece'
#xwd_url = 'http://www.thehindu.com/crossword/the-hindu-crossword-11717/article8681827.ece'
#xwd_url = 'http://www.thehindu.com/crossword/the-hindu-crossword-11716/article8677222.ece'

ENCODING = 'ISO-8859-1'

def replace_unicode(string):
    # stuff = {u'\u2018': "'", u'\u2019': "'", u'\u2013': '--', u'\u2014': '---'}
    # for key in stuff:
    #     string = string.replace(key, stuff[key])

    string = re.sub(u'[\u02bc\u2018\u2019\u201a\u201b\u2039\u203a\u300c\u300d]', "'", string) # fancy single quotes
    string = re.sub(u'[\u00ab\u00bb\u201c\u201d\u201e\u201f\u300e\u300f]', '"', string) # fancy double quotes
    string = re.sub(u'[\u2013]', '--', string) # en dash
    string = re.sub(u'[\u2014]', '---', string) # em dash
    string = re.sub(u'[\u2026]', '...', string) # horizontal ellipsis
    string = re.sub(u'[\u00a9\u24b8\u24d2]', '(c)', string) # copyright symbol
    string = re.sub(u'[\u00ae\u24c7]', '(r)', string) # registered symbol
    string = re.sub(u'[\u2117\u24c5\u24df]', '(p)', string) # sound recording copyright symbol
    string = re.sub(u'[\u2120]', '(sm)', string) #service mark symbol 
    string = re.sub(u'[\u2122]', '(tm)', string) #trade mark symbol 

    return string.encode(ENCODING, 'replace').decode(ENCODING)

def generate_puz(xwd_url):
    
    parser = etree.HTMLParser()
    try:
        tree = etree.parse(xwd_url, parser)
    except etree.ParseError as e:
        print(e)
    
    date = replace_unicode(tree.xpath("//span[@class='dateline']/text()")[1].strip())
    
    title = replace_unicode(tree.xpath("//h1[@class='detail-title']/text()")[0])
    
    author = replace_unicode(tree.xpath("//span[@class='artauthor']/ul/li/a/text()")[0])
    
    xwd_table = tree.xpath("//table[@class='blCrossword cwTable']/tbody")
    if xwd_table == []: # if <tbody> tag is not present 
        xwd_table = tree.xpath("//table[@class='blCrossword cwTable']")
    
    clues_across_raw = tree.xpath("//div[@class='cwClueAcross clueList']/div[@class='clueAcrossList']/ul/li/text()")
    clues_down_raw = tree.xpath("//div[@class='cwClueDown clueList']/div[@class='clueAcrossList']/ul/li/text()")
    across_nums_tree = tree.xpath("//div[@class='cwClueAcross clueList']/div[@class='clueAcrossList']/ul")
    down_nums_tree = tree.xpath("//div[@class='cwClueDown clueList']/div[@class='clueAcrossList']/ul")
    
    clues_across = []
    nums_across = []
    lens_across = []
    
    clues_down = []
    nums_down = []
    lens_down = []
    
    # sanitise across clues
    for clue_raw in clues_across_raw:
        clue = clue_raw.strip()
        if clue == ')': # if clue is just a parenth close, ignore
            pass
        else:
            if clue[-1] == '(': # remove trailing parenth open
                clue = clue[:-1]
            if clue[-1] == ' ': # remove trailing space
                clue = clue[:-1]
    
            clues_across.append(replace_unicode(clue))
    
    # sanitise down clues
    for clue_raw in clues_down_raw:
        clue = clue_raw.strip()
        if clue == ')': # if clue is just a parenth close, ignore
            pass
        else:
            if clue[-1] == '(': # remove trailing parenth open
                clue = clue[:-1]
            if clue[-1] == ' ': # remove trailing space
                clue = clue[:-1]
    
            #clues_down.append(clue.replace(u'\u2018',"'").replace(u'\u2019',"'"))
            clues_down.append(replace_unicode(clue))
    
    for item in across_nums_tree[0]:
        
        data_clue_no = item.get('data-clue-no')
        if len(data_clue_no) == 1:
            nums_across.append('0' + data_clue_no + 'A')
        else:
            nums_across.append(data_clue_no + 'A')

        lens_across.append(item.xpath("span[@class='clueCount']/text()")[0])
    
    
    for item in down_nums_tree[0]:
        
        data_clue_no = item.get('data-clue-no')
        if len(data_clue_no) == 1:
            nums_down.append('0' + data_clue_no + 'D')
        else:
            nums_down.append(data_clue_no + 'D')
        
        lens_down.append(item.xpath("span[@class='clueCount']/text()")[0])

    # concatenate across and down clues, clue numbers and enumerations
    clues = clues_across
    clues.extend(clues_down)

    nums = nums_across
    nums.extend(nums_down)

    lens = lens_across
    lens.extend(lens_down)

    # sort by clue numbers
    clues_out = sorted((num, clue, enum) for num, clue, enum in zip(nums, clues, lens))

    # print(clues_out) # to debug unicode error in clue
    
    
    n_rows = len(xwd_table[0])
    n_cols = len(xwd_table[0][0])

    xwd_sol = []
    xwd_grid = []
    
    for row in xwd_table[0]:
        for cell in row:
            if cell.get("class") == "blCrossBlock":
                xwd_sol.append('.')
                xwd_grid.append('.')
            else:
                xwd_sol.append(cell.get("data-cw-solution"))
                xwd_grid.append('-')
    
    
    # For text verion of .puz format
    # clues_across_dic = [{'clue':clue, 'enumeration':length} for clue, length in zip(clues_across, lens_across)]
    # clues_down_dic = [{'clue':clue, 'enumeration':length} for clue, length in zip(clues_down, lens_down)]
    # 
    # 
    # puztxt_header = "<ACROSS PUZZLE>\n<TITLE>\n"+ title +"\n<AUTHOR>\n" \
    #         + author + "\n<COPYRIGHT>\nThe Hindu\n<SIZE>\n" + str(n_rows) \
    #         + "x" + str(n_cols) + "\n"
    # 
    # puztxt_grid = "<GRID>\n"
    # for row in xwd_sol:
    #     puztxt_grid += ''.join(row) + '\n'

    # puztxt_clues_acr = "<ACROSS>\n"
    # for item in clues_across_dic:
    #     puztxt_clues_acr += item['clue'] + ' (' + item['enumeration'] + ')\n'

    # puztxt_clues_dow = "<DOWN>\n"
    # for item in clues_down_dic:
    #     puztxt_clues_dow += item['clue'] + ' (' + item['enumeration'] + ')\n'
    # 
    # puz_string = puztxt_header + puztxt_grid + puztxt_clues_acr + puztxt_clues_dow

    # filename = title.replace(' ','_').lower()+'.puz'
    # #output = StringIO.StringIO()
    # #output.write(puz_string)
    # #output.close()
    # return [puz_string, filename]

    # For binary version of .puz format
    puzbin = puz.Puzzle()

    puzbin.preamble = b''
    puzbin.title = title + ": " + date
    puzbin.author = author
    puzbin.copyright = "The Hindu"
    puzbin.width = n_cols
    puzbin.height = n_rows

    puzbin.solution = ''.join(xwd_sol)
    puzbin.fill = ''.join(xwd_grid)

    #clues_across_enum = [clue + ' (' + length + ')' for clue, length in zip(clues_across, lens_across)]
    #clues_down_enum = [clue + ' (' + length + ')' for clue, length in zip(clues_down, lens_down)]

    #puzbin.clues = clues_across_enum
    #puzbin.clues.extend(clues_down_enum)

    puzbin.clues = [item[1] + ' (' + item[2] + ')' for item in clues_out]

    puzbin_out = puzbin.tobytes()

    filename = str(title.replace(' ','_').lower()+'.puz')

    return [puzbin_out, filename]
    
