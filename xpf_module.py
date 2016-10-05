from lxml import etree
#import json
#from urllib.request import Request, urlopen
#from urllib.error import URLError, HTTPError

#xwd_url = "The Hindu Crossword 11718 - The Hindu.html"
#xwd_url = 'http://www.thehindu.com/crossword/the-hindu-crossword-11718/article8686670.ece'
#xwd_url = 'http://www.thehindu.com/crossword/the-hindu-crossword-11717/article8681827.ece'
#xwd_url = 'http://www.thehindu.com/crossword/the-hindu-crossword-11716/article8677222.ece'

def generate_xpf(xwd_url):
    
    #req = Request(xwd_url)
    #try:
    #    response = urlopen(req)
    #except HTTPError as e:
    #    print('The server couldn\'t fulfill the request.')
    #    print('Error code: ', e.code)
    #except URLError as e:
    #    print('We failed to reach a server.')
    #    print('Reason: ', e.reason)
    #
    #xwd_html = response.read()
    
    parser = etree.HTMLParser()
    try:
        tree = etree.parse(xwd_url, parser)
    except etree.ParseError as e:
        print(e)
    
    date = tree.xpath("//span[@class='dateline']/text()")[1].strip()
    
    title = tree.xpath("//h1[@class='detail-title']/text()")[0]
    
    author = tree.xpath("//span[@class='artauthor']/ul/li/a/text()")

    if author:
        author = replace_unicode(author[0])
    else:
        author = ''
    
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
    
            clues_across.append(clue)
    
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
    
            clues_down.append(clue)
    
    for item in across_nums_tree[0]:
        nums_across.append(item.get('data-clue-no'))
        lens_across.append(item.xpath("span[@class='clueCount']/text()")[0])
    
    
    for item in down_nums_tree[0]:
        nums_down.append(item.get('data-clue-no'))
        lens_down.append(item.xpath("span[@class='clueCount']/text()")[0])
    
    
    n_rows = len(xwd_table[0])
    n_cols = len(xwd_table[0][0])
    
    xwd_sol = [None]*n_rows
    xwd_xy = {}
    
    for k, row in enumerate(xwd_table[0]):
        xwd_sol[k] = []
        for k_col, cell in enumerate(row):
            if cell.get("class") == "blCrossBlock":
                xwd_sol[k].append('.')
            else:
                xwd_sol[k].append(cell.get("data-cw-solution"))
    
                data_cw_number = cell.get("data-cw-number")
                if data_cw_number != None:
                    xwd_xy[data_cw_number] = [str(k+1), str(k_col+1)]
    
    
    xpf_across = [{'row': xwd_xy[num][0], 'col': xwd_xy[num][1], 'number':num, 'clue':clue, 'enumeration':length} for num, clue, length in zip(nums_across, clues_across, lens_across)]
    xpf_down = [{'row': xwd_xy[num][0], 'col': xwd_xy[num][1], 'number':num, 'clue':clue, 'enumeration':length} for num, clue, length in zip(nums_down, clues_down, lens_down)]
    
    
    puzzles = etree.Element('Puzzles', Version='1.0')
    doc = etree.ElementTree(puzzles)
    
    puzzle = etree.SubElement(puzzles, 'Puzzle')
    etree.SubElement(puzzle, 'Title').text = title
    etree.SubElement(puzzle, 'Author').text = author
    etree.SubElement(puzzle, 'Date').text = date
    etree.SubElement(puzzle, 'Publisher').text = 'The Hindu'
    
    size = etree.SubElement(puzzle, 'Size')
    etree.SubElement(size, 'Rows').text = str(n_rows)
    etree.SubElement(size, 'Cols').text = str(n_cols)
    
    grid = etree.SubElement(puzzle, 'Grid')
    for row in xwd_sol:
        etree.SubElement(grid, 'Row').text = ''.join(row)
    
    clues = etree.SubElement(puzzle, 'Clues')
    for item in xpf_across:
        etree.SubElement(clues, 'Clue', Row=item['row'], Col=item['col'], Num=item['number'], Dir='Across').text = item['clue']+' ('+item['enumeration']+')'
    for item in xpf_down:
        etree.SubElement(clues, 'Clue', Row=item['row'], Col=item['col'], Num=item['number'], Dir='Down').text = item['clue']+' ('+item['enumeration']+')'
    
    xml_string = etree.tostring(puzzles, pretty_print=True, xml_declaration=True, encoding="UTF-8")

    filename = title.replace(' ','_').lower()+'.xml'
    #output = StringIO.StringIO()
    #output.write(xml_string)
    #output.close()

    return [xml_string, filename]
    
    #xml_filename = './test/'+title.replace(' ','_').lower()+'.xml'
    #with open(xml_filename, 'wb') as xml_file:
    #    #doc.write(xml_file, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    #    doc.write(xml_file, xml_declaration=True, encoding='UTF-8')
