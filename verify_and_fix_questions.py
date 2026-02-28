#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
校验和修复test_extracted.json文件中的题目缺失问题
"""

import json
import re
from typing import List, Dict, Any


def create_missing_questions():
    """
    创建丢失的题目
    """
    missing_questions = [
        {
            "type": "question",
            "number": "8",
            "content": "下列各句中加点词的意义和用法，相同的一组是（ ）\nA. 于是朝廷皆以偷合苟免为事 摇其本以观其疏密\nB. 有战国豪士之余风 议法度而修之于朝廷\nC. 反复叙录而不厌 知止而后有定\nD. 则其害有不可胜言者矣 则天地曾不能以一瞬",
            "answer": "D",
            "analysis": "本题考查学生理解文言虚词在文中的意义和用法的能力。\nA.介词，把/连词，来。句意：于是朝廷官员都把苟且迎合、免于责罚当作行事准则。/动摇树根来看土捣得实不实。\nB.助词，的/代词，代“法度”。句意：有战国时期豪侠之士的遗风。/商议法令制度，又在朝廷上修正。\nC.连词，表转折，却/连词，表顺承，就，则。句意：反复记录却不感到厌烦。/知道要达到的“至善”境界，则志向坚定不移。\nD.均为连词，就，那么。句意：那么它的危害就有说不尽的了。/那么天地间万事万物时刻在变动，连一眨眼的工夫都不停止。\n故选D。"
        },
        {
            "type": "question",
            "number": "9",
            "content": "文中画波浪线的句子，断句最合理的一项是（ ）\nA. 盖迁虽横就刑戮/处于污俗之中/困于心衡于虑/损激之气形于简策/故其言每过/直而不自知焉\nB. 盖迁虽横就/刑戮处于污俗之中/困于心/衡于虑/损激之气形/于简策故其言每过直/而不自知焉\nC. 盖迁虽横就刑戮/处于污俗之中/困于心/衡于虑/损激之气形于简策/故其言每过直而不自知焉\nD. 盖迁虽横/就刑戮/处于污俗之中/困于心/衡于虑/损激之气/形于简策/故其言每过直/而不自知焉",
            "answer": "C",
            "analysis": "本题考查学生文言文断句的能力。\n句意：大概司马迁虽然意外遭受刑罚，身处污浊的世俗之中，内心困苦、思虑阻塞，（于是）愤激的情绪表现在文章中，所以他的言论常常过于直率自己却没察觉到。\n“迁虽横就刑戮”中，“迁”为主语，“横就刑戮”是动宾结构，作谓语，意为司马迁虽然意外遭受刑罚，中间不能断开，排除BD；\n“其言每过直”是主谓结构，中间不能断开，排除A；\n故C。"
        },
        {
            "type": "question",
            "number": "10",
            "content": "下列对文中文化常识的解说，不正确的一项是（ ）\nA. 黄老，黄帝与老子的合称，文中指以道家思想为主，强调“清静无为”的学说。\nB. 游侠，古称好交游、轻生死、重信义、能救人于急难的人，文中指无赖之徒。\nC. 处士，指品德高尚、有才华却不追求做官的隐居之人，后也泛指未做官的士人。\nD. 清谈，以何晏为代表的魏晋士人谈论宇宙、自然、人生等抽象哲理而形成的风气。",
            "answer": "B",
            "analysis": "本题考查学生对古代文化常识的掌握能力。\n“文中指无赖之徒”错误，文中的“游侠”指好交游、轻生重信、能救人危难的人，此处不指“无赖之徒”。\n故选B。"
        },
        {
            "type": "question",
            "number": "11",
            "content": "下列对选文的理解与分析，不正确的一项是（ ）\nA. 秦观结合司马迁遭遇李陵之祸的经历，对班固关于司马迁的看法进行了分析。\nB. 张耒喜爱阅读司马迁笔下曹沫、豫让的故事，但仍认为他们只是好逞勇武之人。\nC. 吕祖谦指出，司马迁“先黄老而后六经”“序游侠”“述货殖”具有现实针对性。\nD. 三则材料都联系了司马迁的现实处境加以分析论证，具有较强的说服力。",
            "answer": "D",
            "analysis": "本题考查学生理解文章内容的能力。\nD.“三则材料都联系了司马迁的现实处境”错误，材料二未涉及司马迁的现实处境。\n故选D。"
        },
        {
            "type": "question",
            "number": "12",
            "content": "把文言文阅读材料中画横线的句子翻译成现代汉语。\n（1）方汉武用法刻深，急于功利，大臣一言不合，辄下吏就诛。\n（2）如聂政、荆轲之事，此特贱丈夫之雄耳。\n（3）自迁之崇势利而货赂之风愈炽。",
            "answer": "（1）正当汉武帝施行法律严厉苛刻、急功近利（之时），大臣一句话不合（他的意思），就被交给狱官接受惩罚。\n（2）像（司马迁记）聂政、荆轲的事情，这不过是小看大丈夫的气概罢了。\n（3）自从司马迁崇尚权势财利，用财物贿赂人的风气就更盛了。",
            "analysis": "本题考查学生理解并翻译文言文句子的能力。\n（1）“方”，正当……之时；“刻”，苛刻；“就”，接受。\n（2）“特”，只，只不过；“贱”，小看，轻视。\n（3）“崇”，崇尚；“货赂”，用财物贿赂人；“炽”，盛。"
        },
        {
            "type": "question",
            "number": "13",
            "content": "针对司马迁《史记》的写作，秦观、张耒、吕祖谦评论的侧重点各是什么？",
            "answer": "秦观：《史记》重视写货殖与游侠的原因。\n张耒：《史记》人物事件的真实性和记录的必要性。\n吕祖谦：司马迁带着“不平之气”写《史记》产生的负面作用。",
            "analysis": "本题考查学生评价探究文中思想观点的能力。\n由材料一“迁之遭李陵祸也，家贫无财贿自赎……故其序游侠也”可知，秦观评论《史记》重视写货殖与游侠的原因。\n由材料二“迁叙聂政、荆轲之事特详……故不知其言之不足信，而忘其事之为不足录也”可知，张耒评论《史记》人物事件的真实性和记录的必要性。\n由材料三“及稽其流弊，则自迁之先黄老而虚浮之说愈胜……皆迁有以启之也”可知，吕祖谦的评论侧重司马迁带着“不平之气”写《史记》产生的负面作用。"
        },
        {
            "type": "question",
            "number": "15",
            "content": "诗人创作时对空缺处的字颇为斟酌，你认为成稿后的文字最有可能是下面哪一组？结合诗意谈谈你的理由。\n①含引全半 ②引含全半 ③含引半全",
            "answer": "选①。根据诗题及全诗内容，填入空缺处的字应生动准确，切合初夏时节的景物特征。瀑布流泻，水雾弥漫，本身含有凉意，故用“含”；垂藤生阴而引来凉意，故用“引”；禾苗长得高而茂密，覆满田垄，故用“全”；荷叶尚未完全遮盖塘面，故用“半”。",
            "analysis": "本题考查学生鉴赏诗歌炼字的能力。\n“瀑水_______秋气”：初夏瀑布虽有凉意，但“秋气”是清冷感的借代，用“含”字可体现瀑布水雾中蕴含的清凉，而非“引”（引来）秋气（初夏无秋气可引），故第一空选“含”；\n“垂藤_______夏凉”：垂藤枝叶茂密可遮挡阳光，“引”字能生动表现藤蔓带来凉意的动态感，比“含”更贴合藤蔓的作用，故第二空选 “引”；\n“苗深_______覆陇”：初夏禾苗已长得茂密，“全”字可体现禾苗完全覆盖田垄的状态，符合“苗深”的描述；若用“半”则与“深”矛盾，故第三空选“全”；\n“荷上_______侵塘”：初夏荷叶尚未完全舒展，仅部分遮盖池塘，“半”字准确表现荷叶初长成的阶段特征，若用“全”则不符合初夏荷花生长规律，故第四空选“半”。"
        },
        {
            "type": "question",
            "number": "16",
            "content": "补写出下列句子中的空缺部分。\n（1）《沁园春•长沙》中“____________________，____________________”用色彩明艳的壮丽秋景，展现了毛泽东的乐观与豪迈；《蜀相》中“____________________，____________________”借色彩明丽的盎然春景，反衬了诗人对诸葛亮的惋惜之情。\n（2）小华用《劝学》中的“____________________，____________________”向弟弟讲述天赋再高如果不坚持也难成功的道理。",
            "answer": "①. 看万山红遍 ②. 层林尽染 ③. 映阶碧草自春色 ④. 隔叶黄鹂空好音 ⑤. 骐骥一跃 ⑥. 不能十步",
            "analysis": "本题考查学生默写常见的名篇名句的能力。\n易错字词：染、阶、鹂、骐骥。"
        },
        {
            "type": "question",
            "number": "18",
            "content": "第三段描写弹棉花的“奇景”，你认为多余吗？请说明理由。",
            "answer": "多余。导致叙事节奏拖沓，使文章结构变得松散；与文章主题无关。\n\n不多余。把浓雾比喻成轻盈、跳跃的棉花，形象生动，富有文学色彩；联想丰富，充分描写了“雾的世界”，体现了散文“形散而神不散”的特点。",
            "analysis": "本题考查学生分析文章重要语段的作用的能力。\n\n观点一：多余。文章开篇聚焦“登山见雾”，突然插入弹棉花场景，使“雾中登山→联想天界”的逻辑暂时断裂，让读者注意力从“雾与心境”转移，导致节奏拖沓。弹棉花的描写仅停留于“雾的形态”，未对“故乡思念”“抗战情怀”“天界象征” 等核心主题产生支撑，显得冗余。\n\n观点二：不多余。将雾比作“被弹起的新棉”，用“月光似的舞衣”“旋风似地跳舞”等描写，把无形的雾具象化为轻盈、灵动的画面，比直接写“雾浓”更生动，强化“雾的世界”的沉浸感。散文“形散神不散”，这段联想看似偏离“登山”主线，实则通过“棉”与 “雾”的关联，丰富了“雾”的质感，未脱离“天界”的核心感悟。"
        },
        {
            "type": "question",
            "number": "19",
            "content": "赏析文中画线的语句。",
            "answer": "通过拟人、比喻、视听结合等手法，生动形象地描写了一家人夏夜乘凉和谐、安宁、美好的场景，表达了作者对和平生活的怀念和渴望。",
            "analysis": "本题考查学生品味精彩的语言表达艺术的能力。\n\n手法丰富。拟人：“夜风替人涤去一天的烦热”“蚊虫，在耳边唱歌”，赋予自然景物人的动作，营造亲切氛围；比喻：“夜色也清朗得像山谷间的流泉”，将抽象的“清朗”转化为可感知的 “流泉”，画面清新；视听结合：青蛙、促织“叫鸣”（听觉），“萤火虫在屋檐边飞闪”“银色的群星”（视觉），还原夏夜的鲜活场景。\n\n通过描写家人乘凉、仰望星空的和谐画面，暗含对童年和平生活的怀念，与后文“故乡沦陷”的惨状形成对比，强化对和平的渴望。"
        },
        {
            "type": "question",
            "number": "20",
            "content": "作者为什么既赞美长江又怨恨长江？",
            "answer": "①作者赞美长江，因为长江养育了两岸人民，是祖国大好河山的象征，借赞美长江表达了对和平、对祖国的热爱。\n\n②作者怨恨长江，是因为长江沦为了日本侵略者的帮凶，但这并非真的怨恨长江，而是憎恨敌寇的侵略行径。",
            "analysis": "本题考查学生分析作者情感态度的能力。\n\n①赞美长江：长江是“祖国的第一条大水”，千百年“像一条温驯的老牛”为人民服役（航运、灌溉、供水），象征“源远流长的祖国”，赞美长江实则是赞美祖国山河与和平年代的生活。\n\n②“怨恨”长江：并非真的怨恨长江，而是痛恨侵略者——如今长江上“行驶着敌人的战舰”，成为敌人运输武器、残杀同胞的工具，“怨恨”是对侵略行径的愤怒转移，本质是控诉敌寇破坏祖国的罪行。"
        },
        {
            "type": "question",
            "number": "21",
            "content": "文中的“天界”有哪些含义？",
            "answer": "①现实中身处的雾的世界②童年听过的天上的世界③自由、未被占领的国土④未来完全自由、和平、安宁的祖国。",
            "analysis": "本题考查学生分析文章标题的含义和作用的能力。\n\n①现实层面：指作者登山时身处的“雾的世界”，雾浓如屏障，看不清周遭，如置身缥缈之境。\n\n②童年想象层面：指母亲故事中“可以上去的”天上，是充满云雾、神仙的奇幻世界，承载童年对美好境界的向往。\n\n③现实对照层面：指“自由、未被敌人占领的国土”，作者身处未沦陷之地，对比故乡的“战烟弥漫”，觉得此处如“天界”般珍贵。\n\n④理想层面：指“完全自由、和平的祖国”，文末“祖国不回复到完全自由的祖国，即使真有天界，即使真正到了天界，又将怎样打发灵魂上的负担”，将“天界”升华为对未来和平、安宁的期盼。"
        }
    ]

    return missing_questions


def fix_extracted_json():
    """
    修复extracted.json文件
    """
    # 读取现有的extracted文件
    with open('data/02_temp_build/test_extracted.json', 'r', encoding='utf-8') as f:
        extracted_data = json.load(f)

    # 获取所有已存在的题目编号
    existing_numbers = {item['number'] for item in extracted_data if 'number' in item}

    # 创建丢失的题目
    missing_questions = create_missing_questions()

    # 只添加缺失的题目
    added_count = 0
    for question in missing_questions:
        if question['number'] not in existing_numbers:
            extracted_data.append(question)
            print(f"Added missing question {question['number']}")
            added_count += 1

    if added_count == 0:
        print("No missing questions found to add.")
    else:
        print(f"Added {added_count} missing questions.")

    # 按照题目编号排序
    def sort_key(item):
        if 'number' not in item:
            return float('inf')  # 将没有number的项放到最后

        num_str = item['number']
        # 处理带括号的编号，如 "22（1）"
        if '（' in num_str:
            # 提取数字部分，如从 "22（1）" 中提取 22.1
            parts = re.match(r'(\d+)（(\d+)）', num_str)
            if parts:
                main_num, sub_num = parts.groups()
                return float(main_num) + float(sub_num)/10.0
        elif '.' in num_str and num_str.replace('.', '').replace('（','').replace('）','').isdigit():
            # 已经是浮点数格式
            return float(num_str.replace('（','').replace('）',''))
        elif num_str.isdigit():
            # 纯数字
            return int(num_str)
        else:
            # 非数字编号，如 "一" "二" "三" 等，放到前面
            if num_str in ["一", "二", "三", "四", "五", "六", "七"]:
                return {"一": 0.1, "二": 0.2, "三": 0.3, "四": 0.4, "五": 0.5, "六": 0.6, "七": 0.7}[num_str]
            else:
                return ord(num_str[0]) * 1000  # 使用ASCII值做粗略排序

    extracted_data.sort(key=sort_key)

    # 保存修复后的文件
    with open('data/02_temp_build/test_extracted.json', 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=2)

    print(f"Fixed test_extracted.json, total items: {len(extracted_data)}")

    # 验证修复结果
    print("\\nVerifying the sequence:")
    numbers = []
    for item in extracted_data:
        if 'number' in item and item['number'].isdigit():
            numbers.append(int(item['number']))

    if numbers:
        numbers.sort()
        print(f"Numbers found: {numbers[:20]}{'...' if len(numbers) > 20 else ''}")

        # 检查连续性
        if len(numbers) > 0:
            expected = list(range(min(numbers), max(numbers)+1))
            missing = [n for n in expected if n not in numbers]

            if missing:
                print(f"Still missing numbers: {missing}")
                return False
            else:
                print("All numbers present in sequence")

    return True


if __name__ == "__main__":
    print("Checking and fixing missing questions in test_extracted.json...")
    success = fix_extracted_json()

    if success:
        print("\\nSuccess! Missing questions have been restored.")
    else:
        print("\\nWarning: Some questions might still be missing.")