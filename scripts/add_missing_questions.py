#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复缺失的题目 22（2）和 23
"""

import json


def add_missing_questions():
    # 读取现有的JSON文件
    with open('data/02_temp_build/test_extracted.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 检查是否已存在这些题目
    existing_numbers = {item['number'] for item in data if 'number' in item}

    # 添加缺失的题目
    missing_items = []

    # 题目 22(2)
    if '22（2）' not in existing_numbers:
        item_22_2 = {
            "type": "question",
            "number": "22（2）",
            "content": "概括\"无短板\"饮食方案的要点。",
            "answer": "①优先食用天然食材②摄入多样性食材\n③服用补充剂要有针对性④定期调整饮食结构",
            "analysis": "本题考查学生语段压缩概括的能力。\n①根据\"打造'无短板'饮食方案……要优先通过天然食材获取营养\"概括出\"优先食用天然食材\"；\n②根据\"平均每天摄入12种以上食材，每周至少25种\"概括出\"摄入多样性食材\"；\n③根据\"孕妇要注重补充叶酸，老年人要补充维生素B12，避免盲目服用补充剂\"概括出\"服用补充剂要有针对性\"；\n④根据\"每半年对照《中国居民膳食指南》调整饮食结构\"概括出\"定期调整饮食结构\"。"
        }
        missing_items.append(item_22_2)

    # 题目 23
    if '23' not in existing_numbers:
        item_23 = {
            "type": "question",
            "number": "23",
            "content": "根据下图，对比线性经济参考示例，指出循环经济体现了哪些理念。\n示例：节约理念\n![学科网(www.zxxk.com)--教育资源门户，提供试卷、教案、课件、论文、素材以及各类教学资源下载，还有大量而丰富的教学相关资讯！ 3Se6LuOtP2PNAx1ODbqMbQ==](data:image/png;base64...)",
            "answer": "①统筹理念（\"可持续发展理念\"亦可）\n②环保理念（\"低碳理念\"\"人与自然和谐发展理念\"亦可）",
            "analysis": "本题考查学生图文转换的能力。\n①统筹理念（\"可持续发展理念\"）：线性经济是\"原材料获取-制造-使用-处置-废弃\"的单向流程，资源一次性消耗后废弃；循环经济则形成\"设计-制造-使用-再用及维修-收集-循环利用-原材料\"的闭环，资源可长期循环，符合经济、社会、环境长期发展的需求。\n②环保理念（\"低碳理念\"\"人与自然和谐发展理念\"）：线性经济最终\"废弃\"会造成资源浪费与污染；循环经济通过\"循环利用\"\"收集\"等环节，减少废弃物排放，保护生态环境，体现低碳、绿色的环保追求。"
        }
        missing_items.append(item_23)

    # 添加缺失的题目
    for item in missing_items:
        data.append(item)
        print(f"Added missing question {item['number']}")

    # 按照题目编号排序
    def sort_key(item):
        if 'number' not in item:
            return float('inf')  # 将没有number的项放到最后

        num_str = item['number']
        # 处理带括号的编号，如 "22（2）"
        if '（' in num_str:
            # 提取数字部分，如从 "22（2）" 中提取 22.2
            import re
            parts = re.match(r'(\d+)（(\d+)）', num_str)
            if parts:
                main_num, sub_num = parts.groups()
                return int(main_num) + int(sub_num)/10.0
        elif num_str.isdigit():
            # 纯数字
            return int(num_str)
        else:
            # 非数字编号，如 "一" "二" "三" 等，放到前面
            if num_str in ["一", "二", "三", "四", "五", "六", "七"]:
                return {"一": 0.1, "二": 0.2, "三": 0.3, "四": 0.4, "五": 0.5, "六": 0.6, "七": 0.7}[num_str]
            else:
                # 将字母或特殊字符编号放在最后
                return ord(num_str[0]) * 1000 if num_str else 9999

    data.sort(key=sort_key)

    # 保存文件
    with open('data/02_temp_build/test_extracted.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Total items after fix: {len(data)}")

    # 验证修复
    numbers = []
    for item in data:
        if 'number' in item:
            num_str = item['number']
            if num_str.isdigit():
                numbers.append(int(num_str))
            elif '（' in num_str:
                import re
                parts = re.match(r'(\d+)（(\d+)）', num_str)
                if parts:
                    main_num, sub_num = parts.groups()
                    numbers.append(int(main_num))  # 主题号也要计入

    if numbers:
        numbers = sorted(set(numbers))  # 去重并排序
        print(f"Unique question numbers: {numbers[-10:]}")  # 显示最后10个

    return len(missing_items)


if __name__ == "__main__":
    count = add_missing_questions()
    print(f"Added {count} missing questions.")