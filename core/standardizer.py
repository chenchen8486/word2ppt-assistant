import os
import re
import zipfile
import xml.etree.ElementTree as ET
import docx
from utils.logger import get_logger

logger = get_logger()

class ImageExtractor:
    def __init__(self, file_path, output_dir):
        self.file_path = file_path
        self.output_dir = output_dir

    def extract(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        with zipfile.ZipFile(self.file_path, "r") as zf:
            self._extract_media(zf)
            rels = self._load_relationships(zf)
            image_map = self._map_images(zf, rels)
        return image_map

    def _extract_media(self, zf):
        for info in zf.infolist():
            if info.filename.startswith("word/media/") and not info.is_dir():
                filename = os.path.basename(info.filename)
                out_path = os.path.join(self.output_dir, filename)
                with zf.open(info) as src, open(out_path, "wb") as dst:
                    dst.write(src.read())

    def _load_relationships(self, zf):
        rels = {}
        try:
            rels_xml = zf.read("word/_rels/document.xml.rels")
            root = ET.fromstring(rels_xml)
            for rel in root.findall(".//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"):
                rid = rel.get("Id")
                target = rel.get("Target")
                if rid and target:
                    rels[rid] = target
        except Exception as e:
            logger.warning(f"Failed to read relationships: {e}")
        return rels

    def _map_images(self, zf, rels):
        image_map = {}
        try:
            doc_xml = zf.read("word/document.xml")
            root = ET.fromstring(doc_xml)
            ns = {
                "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
                "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
                "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
            }
            paragraphs = root.findall(".//w:p", ns)
            for idx, p in enumerate(paragraphs):
                blips = p.findall(".//a:blip", ns)
                paths = []
                for blip in blips:
                    rid = blip.get(f"{{{ns['r']}}}embed")
                    if rid and rid in rels:
                        filename = os.path.basename(rels[rid])
                        path = os.path.join(self.output_dir, filename)
                        if os.path.exists(path) and path not in paths:
                            paths.append(path)
                if paths:
                    image_map[idx] = paths
        except Exception as e:
            logger.warning(f"Failed to parse document.xml: {e}")
        return image_map

class Standardizer:
    def __init__(self, file_path, output_image_dir="temp_images", llm_client=None):
        self.file_path = file_path
        self.output_image_dir = output_image_dir
        self.llm_client = llm_client
        self.context_pattern = re.compile(r'^[一二三四五六七八九十]+、')
        self.question_pattern = re.compile(r'^(\d+)[\.．、\s]|^[(（](\d+)[)）]|^Question\s*(\d+)', re.I)
        self.exclude_patterns = [
            re.compile(r'^【导语】'),
            re.compile(r'^参考译文')
        ]
        self.answer_keyword = "【答案】"
        self.analysis_keyword = "【解析】"

    def load_and_parse(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")
        logger.info(f"Loading document: {self.file_path}")
        image_map = ImageExtractor(self.file_path, self.output_image_dir).extract()
        doc = docx.Document(self.file_path)
        paragraphs = []
        for idx, p in enumerate(doc.paragraphs):
            text = p.text.replace("\xa0", " ").strip()
            images = image_map.get(idx, [])
            paragraphs.append({"text": text, "images": images, "line_index": idx})
        filtered = self._filter_paragraphs(paragraphs)
        contexts, questions, answers, analyses = self._bucket(filtered)
        aligned_questions = self._align(questions, answers, analyses)
        if self.llm_client:
            aligned_questions = self._refine_questions_with_llm(aligned_questions)
        items = self._build_items(contexts, aligned_questions)
        return items

    def _filter_paragraphs(self, paragraphs):
        start_index = 0
        for p in paragraphs:
            if self.context_pattern.match(p["text"]):
                start_index = p["line_index"]
                break
        filtered = []
        for p in paragraphs:
            if p["line_index"] < start_index:
                continue
            if not p["text"] and not p["images"]:
                continue
            if any(pat.search(p["text"]) for pat in self.exclude_patterns):
                continue
            filtered.append(p)
        return filtered

    def _bucket(self, paragraphs):
        contexts = []
        questions = []
        answers = []
        analyses = []
        last_type = None
        last_item = None
        for p in paragraphs:
            text = p["text"]
            images = p["images"]
            if self.answer_keyword in text:
                item = {"id": self._extract_any_id(text), "content": text, "line_index": p["line_index"]}
                answers.append(item)
                last_type = "answer"
                last_item = item
                continue
            if self.analysis_keyword in text:
                item = {"id": self._extract_any_id(text), "content": text, "line_index": p["line_index"]}
                analyses.append(item)
                last_type = "analysis"
                last_item = item
                continue
            qid = self._extract_question_id(text)
            if qid:
                item = {"id": qid, "content": text, "line_index": p["line_index"], "images": list(images)}
                questions.append(item)
                last_type = "question"
                last_item = item
                continue
            if self.context_pattern.match(text):
                item = {"content": text, "line_index": p["line_index"]}
                contexts.append(item)
                last_type = "context"
                last_item = item
                continue
            if last_item:
                if text:
                    last_item["content"] = f"{last_item['content']}\n{text}" if last_item["content"] else text
                if last_type == "question" and images:
                    for img in images:
                        if img not in last_item["images"]:
                            last_item["images"].append(img)
        return contexts, questions, answers, analyses

    def _align(self, questions, answers, analyses):
        questions_sorted = sorted(questions, key=lambda x: x["line_index"])
        answers_by_id = {a["id"]: a["content"] for a in answers if a.get("id")}
        analyses_by_id = {a["id"]: a["content"] for a in analyses if a.get("id")}
        answers_un = sorted([a for a in answers if not a.get("id")], key=lambda x: x["line_index"])
        analyses_un = sorted([a for a in analyses if not a.get("id")], key=lambda x: x["line_index"])
        used_answers = set()
        used_analyses = set()
        aligned = []
        for q in questions_sorted:
            qid = q["id"]
            answer_text = answers_by_id.get(qid)
            if not answer_text:
                nearest = self._find_nearest_after(answers_un, q["line_index"], used_answers)
                if nearest:
                    answer_text = nearest["content"]
            analysis_text = analyses_by_id.get(qid)
            if not analysis_text:
                nearest = self._find_nearest_after(analyses_un, q["line_index"], used_analyses)
                if nearest:
                    analysis_text = nearest["content"]
            if not analysis_text:
                analysis_text = "【解析待补充】"
            aligned.append({
                "type": "question",
                "id": qid,
                "line_index": q["line_index"],
                "question": q["content"],
                "options": [],
                "answer": answer_text or "",
                "analysis": analysis_text,
                "images": q.get("images", [])
            })
        return aligned

    def _build_items(self, contexts, questions):
        contexts_sorted = sorted(contexts, key=lambda x: x["line_index"])
        questions_sorted = sorted(questions, key=lambda x: x["line_index"])
        items = []
        ctx_idx = 0
        last_context = None
        for q in questions_sorted:
            while ctx_idx < len(contexts_sorted) and contexts_sorted[ctx_idx]["line_index"] < q["line_index"]:
                ctx_text = contexts_sorted[ctx_idx]["content"].strip()
                if ctx_text and ctx_text != last_context:
                    items.append({"type": "context", "content": ctx_text})
                    last_context = ctx_text
                ctx_idx += 1
            items.append(q)
        while ctx_idx < len(contexts_sorted):
            ctx_text = contexts_sorted[ctx_idx]["content"].strip()
            if ctx_text and ctx_text != last_context:
                items.append({"type": "context", "content": ctx_text})
                last_context = ctx_text
            ctx_idx += 1
        return items

    def _find_nearest_after(self, items, line_index, used_set):
        for item in items:
            if item["line_index"] > line_index and id(item) not in used_set:
                used_set.add(id(item))
                return item
        return None

    def _extract_question_id(self, text):
        match = self.question_pattern.search(text)
        if not match:
            return None
        for group in match.groups():
            if group:
                return group
        return None

    def _extract_any_id(self, text):
        match = self.question_pattern.search(text)
        if match:
            for group in match.groups():
                if group:
                    return group
        num = re.search(r'(\d+)', text)
        return num.group(1) if num else None

    def _refine_questions_with_llm(self, questions):
        from concurrent.futures import ThreadPoolExecutor, as_completed
        q_map = {q["id"]: q for q in questions}
        q_ids = [q["id"] for q in questions]
        batch_size = 5
        batches = [q_ids[i:i + batch_size] for i in range(0, len(q_ids), batch_size)]

        def process_batch(batch_ids):
            batch_text = ""
            for qid in batch_ids:
                batch_text += f"--- Question {qid} ---\n{q_map[qid]['question']}\n\n"
            sys_prompt = (
                "You are an exam question parser. Your task is to split raw question text into 'Question Stem' and 'Options'.\n"
                "Return a JSON LIST of objects. Each object must have:\n"
                "- `id`: The question number (string).\n"
                "- `question`: The stem of the question.\n"
                "- `options`: A list of strings for options (e.g. ['A. xxx', 'B. xxx']). If no options, return empty list.\n"
                "Strictly return valid JSON."
            )
            try:
                return self.llm_client.process_chunk(batch_text, system_prompt_override=sys_prompt)
            except Exception as e:
                logger.error(f"LLM refinement failed: {e}")
                return None

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(process_batch, batch): batch for batch in batches}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    for item in result:
                        qid = str(item.get("id"))
                        if qid in q_map:
                            q_map[qid]["question"] = item.get("question", q_map[qid]["question"])
                            q_map[qid]["options"] = item.get("options", [])
        return [q_map[qid] for qid in q_ids]
