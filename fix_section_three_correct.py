import json
import re

def manual_extract_questions(content):
    """
    手动提取第三部分的题目，基于对内容的精确分析
    """
    questions = []

    # 手动解析题目7-13
    # 题目7
    q7_content = "对下列各句中加点词的解释，不正确的一项是（ ）\n\nA. 班固赞司马迁 赞：称赞 B. 皆奇诞不近人情 诞：虚妄\n\nC. 劫以浮词 劫：被胁迫 D. 灵帝之鬻官 鬻：卖"
    q7_answer = "A"
    q7_analysis = "赞：评论、评价。句意：班固评价司马迁。"

    # 题目8
    q8_content = "下列各句中加点词的意义和用法，相同的一组是（ ）\n\nA. 于是朝廷皆以偷合苟免为事 摇其本以观其疏密\n\nB. 有战国豪士之余风 议法度而修之于朝廷\n\nC. 反复叙录而不厌 知止而后有定\n\nD. 则其害有不可胜言者矣 则天地曾不能以一瞬"
    q8_answer = "D"
    q8_analysis = "A.介词，把/连词，来。句意：于是朝廷官员都把苟且迎合、免于责罚当作行事准则。/动摇树根来看土捣得实不实。B.助词，的/代词，代\"法度\"。句意：有战国时期豪侠之士的遗风。/商议法令制度，又在朝廷上修正。C.连词，表转折，却/连词，表顺承，就，則。句意：反复记录却不感到厌烦。/知道要达到的\"至善\"境界，則志向坚定不移。D.均为连词，就，那么。句意：那么它的危害就有说不尽的了。/那么天地间万事万物时刻在变动，连一眨眼的工夫都不停止。故选D!"

    # 题目9
    q9_content = "文中画波浪线的句子，断句最合理的一项是（ ）\n\nA. 盖迁虽横就刑戮/处于污俗之中/困于心衡于虑/损激之气形于简策/故其言每过/直而不自知焉\n\nB. 盖迁虽横就/刑戮处于污俗之中/困于心/衡于虑/损激之气形/于简策故其言每过直/而不自知焉\n\nC. 盖迁虽横就刑戮/处于污俗之中/困于心/衡于虑/损激之气形于简策/故其言每过直而不自知焉\n\nD. 盗迁虽横/就刑戮/处于污俗之中/困于心/衡于虑/损激之气/形于简策/故其言每过直/而不自知焉"
    q9_answer = "C"
    q9_analysis = "句意：大概司马迁虽然意外遭受刑罚，身处污浊的世俗之中，内心困苦、思虑阻塞，（于是）愤激的情绪表现在文章中，所以他的言论常常过于直率自己却没察觉到。\"迁虽横就刑戮\"中，\"迁\"为主语，\"横就刑戮\"是动宾结构，作谓语，意为司马迁虽然意外遭受刑罚，中间不能断开，排除BD；\"其言每过直\"是主谓结构，中间不能断开，排除A；故C。"

    # 题目10
    q10_content = "下列对文中文化常识的解说，不正确的一项是（ ）\n\nA. 黄老，黄帝与老子的合称，文中指以道家思想为主，强调\"清静无为\"的学说。\n\nB. 游侠，古称好交游、轻生死、重信义、能救人于急难的人，文中指无赖之徒。\n\nC. 处士，指品德高尚、有才华却不追求做官的隐居之人，后也泛指未做官的士人。\n\nD. 清谈，以何晏为代表的魏晋士人谈论宇宙、自然、人生等抽象哲理而形成的风气。"
    q10_answer = "B"
    q10_analysis = "\"文中指无赖之徒\"错误，文中的\"游侠\"指好交游、轻生重信、能救人危难的人，此处不指\"无赖之徒\"。故选B。"

    # 题目11
    q11_content = "下列对选文的理解与分析，不正确的一项是（ ）\n\nA. 秦观结合司马迁遭遇李陵之祸的经历，对班固关于司马迁的看法进行了分析。\n\nB. 张耒喜爱阅读司马迁笔下曹沫、豫让的故事，但仍认为他们只是好逞勇武之人。\n\nC. 吕祖谦指出，司马迁\"先黄老而后六经\"\"序游侠\"\"述货殖\"具有现实针对性。\n\nD. 三则材料都联系了司马迁的现实处境加以分析论证，具有较强的说服力。"
    q11_answer = "D"
    q11_analysis = "D.\"三则材料都联系了司马迁的现实处境\"错误，材料二未涉及司马迁的现实处境。故选D。"

    # 题目12
    q12_content = "把文言文阅读材料中画横线的句子翻译成现代汉语。\n\n（1）方汉武用法刻深，急于功利，大臣一言不合，辄下吏就诛。\n\n（2）如聂政、荆轲之事，此特贱丈夫之雄耳。\n\n（3）自迁之崇势利而货赂之风愈炽。"
    q12_answer = "（1）正当汉武帝施行法律严厉苛刻、急功近利（之时），大臣一句话不合（他的意思），就被交给狱官接受惩罚。\n（2）像（司马迁记）聂政、荆轲的事情，这不过是小看大丈夫的气概罢了。\n（3）自从司马迁崇尚权势财利，用财物贿赂人的风气就更盛了。"
    q12_analysis = "（1）\"方\"，正当……之时；\"刻\"，苛刻；\"就\"，接受。（2）\"特\"，只，只不过；\"贱\"，小看，轻视。（3）\"崇\"，崇尚；\"货赂\"，用财物贿赂人；\"炽\"，盛。"

    # 题目13
    q13_content = "针对司马迁《史记》的写作，秦观、张耒、吕祖谦评论的侧重点各是什么？"
    q13_answer = "秦观：《史记》重视写货殖与游侠的原因。\n张耒：《史记》人物事件的真实性和记录的必要性。\n吕祖谦：司马迁带着\"不平之气\"写《史记》产生的负面作用。"
    q13_analysis = "由材料一\"迁之遭李陵祸也，家贫无财贿自赎……故其序游侠也\"可知，秦观评论《史记》重视写货殖与游侠的原因。由材料二\"迁叙聂政、荆轲之事特详……故不知其言之不足信，而忘其事之为不足录也\"可知，张耒评论《史记》人物事件的真实性和记录的必要性。由材料三\"及稽其流弊，则自迁之先黄老而虚浮之说愈胜……皆迁有以启之也\"可知，吕祖谦的评论侧重司马迁带着\"不平之气\"写《史记》产生的负面作用。"

    # 创建题目对象
    questions.append({
        "type": "question",
        "number": "7",
        "content": q7_content,
        "answer": q7_answer,
        "analysis": q7_analysis
    })

    questions.append({
        "type": "question",
        "number": "8",
        "content": q8_content,
        "answer": q8_answer,
        "analysis": q8_analysis
    })

    questions.append({
        "type": "question",
        "number": "9",
        "content": q9_content,
        "answer": q9_answer,
        "analysis": q9_analysis
    })

    questions.append({
        "type": "question",
        "number": "10",
        "content": q10_content,
        "answer": q10_answer,
        "analysis": q10_analysis
    })

    questions.append({
        "type": "question",
        "number": "11",
        "content": q11_content,
        "answer": q11_answer,
        "analysis": q11_analysis
    })

    questions.append({
        "type": "question",
        "number": "12",
        "content": q12_content,
        "answer": q12_answer,
        "analysis": q12_analysis
    })

    questions.append({
        "type": "question",
        "number": "13",
        "content": q13_content,
        "answer": q13_answer,
        "analysis": q13_analysis
    })

    return questions

def fix_section_three_properly(input_file, output_file):
    """
    正确修复第三部分的内容
    """
    # 读取原来的文件内容
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    # 提取第三部分（"三、"）的原始内容
    section_three_content = None
    for item in data:
        if isinstance(item, dict) and 'error' in item and item.get('error') == "":
            original_chunk = item.get('original_chunk', {})
            if original_chunk.get('number') == '三、':
                section_three_content = original_chunk.get('content', '')
                break

    if not section_three_content:
        print("未找到第三部分的内容")
        return

    # 手动提取题目
    questions = manual_extract_questions(section_three_content)

    # 提取材料部分作为context
    # 找到第一个题目前的内容
    first_question_pos = section_three_content.find('7.')
    if first_question_pos == -1:
        first_question_pos = section_three_content.find('7、')
    if first_question_pos == -1:
        first_question_pos = section_three_content.find('7．')

    context_content = section_three_content[:first_question_pos].strip() if first_question_pos != -1 else section_three_content

    # 创建新的数据结构
    fixed_data = []

    # 添加context（材料部分）
    fixed_data.append({
        "type": "context",
        "number": "三、",
        "content": context_content,
        "answer": "",
        "analysis": ""
    })

    # 添加题目7-13
    fixed_data.extend(questions)

    # 保存修复后的数据
    with open(output_file, 'w', encoding='utf-8-sig') as f:
        json.dump(fixed_data, f, ensure_ascii=False, indent=2)

    print(f'修复完成，保存到: {output_file}')
    print(f'修复后数据长度: {len(fixed_data)}')
    print('题目编号:', [q['number'] for q in questions])

    return fixed_data

if __name__ == '__main__':
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'data/02_temp_build/section_three_only_extracted.json'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'data/02_temp_build/section_three_fixed_correct.json'

    fix_section_three_properly(input_file, output_file)