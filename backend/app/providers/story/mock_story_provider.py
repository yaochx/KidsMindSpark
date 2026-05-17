from __future__ import annotations

from typing import Any

UNSAFE_REPLACEMENTS = {
    "猎枪": "木头探险杖",
    "枪": "玩具探险杖",
    "刀": "木头小铲子",
    "炸弹": "彩色烟花图案",
}


class MockStoryProvider:
    name = "mock"

    def create_outline(self, payload: dict[str, Any], story_id: str) -> dict[str, Any]:
        safe_concept = self.make_child_safe_concept(payload["concept"])

        return {
            "storyId": story_id,
            "title": payload["title"],
            "safeConcept": safe_concept,
            "characters": [],
            "status": "outlined",
        }

    def create_timeline(self, story: dict[str, Any]) -> list[dict[str, Any]]:
        safe_concept = story.get("safeConcept") or story.get("concept") or "一次森林冒险"
        title = story.get("title") or "新的漫画故事"
        node_specs = [
            (
                "opening",
                "森林边的小路",
                f"{title}从一条安静又闪亮的小路开始，孩子能马上看懂故事地点。",
            ),
            (
                "hero",
                "勇敢的小主角",
                "主角带着安全的探险道具出发，保持好奇，也记得照顾伙伴。",
            ),
            (
                "goal",
                "寻找奇妙地方",
                "大家想找到传说中的美丽地点，并把一路的发现画进探险本。",
            ),
            (
                "companion",
                "遇见森林朋友",
                "温和的新朋友加入旅程，提醒大家观察线索、互相帮助。",
            ),
            (
                "obstacle",
                "迷雾和怪声音",
                "森林出现迷雾和奇怪声音，队伍需要停下来想办法。",
            ),
            (
                "twist",
                "会眨眼的线索",
                "神秘线索改变路线，让大家发现原来森林在考验他们的合作。",
            ),
            (
                "crisis",
                "断桥前的选择",
                "通往终点的小桥断了，主角必须保护伙伴并寻找安全办法。",
            ),
            (
                "resolution",
                "一起搭起小桥",
                "大家用智慧和合作解决困难，危险被转化成温柔的挑战。",
            ),
            (
                "ending",
                "发现世外桃源",
                f"他们终于抵达世外桃源，也明白这次冒险真正的礼物是友情。故事核心：{safe_concept[:36]}",
            ),
        ]

        timeline: list[dict[str, Any]] = []
        for index, (node_type, title, summary) in enumerate(node_specs):
            next_node_id = (
                f"node_{node_specs[index + 1][0]}"
                if index < len(node_specs) - 1
                else None
            )
            timeline.append(
                {
                    "id": f"node_{node_type}",
                    "type": node_type,
                    "title": title,
                    "summary": summary,
                    "order": index + 1,
                    "x": index * 240,
                    "y": 0,
                    "nextNodeIds": [next_node_id] if next_node_id else [],
                }
            )

        return timeline

    def create_script_pages(self, story: dict[str, Any]) -> list[dict[str, Any]]:
        timeline = story.get("timeline", [])
        timeline_by_order = sorted(timeline, key=lambda node: node.get("order", 0))
        page_titles = [
            "出发的清晨",
            "地图上的亮点",
            "第一棵会唱歌的树",
            "老二发现脚印",
            "刺猬朋友出现",
            "森林午餐",
            "雾气慢慢升起",
            "木头探险杖发亮",
            "奇怪动物的影子",
            "大家停下听声音",
            "眨眼果滚出来",
            "蓝色果实排成箭头",
            "山洞门口的谜题",
            "小猫们分工寻找线索",
            "老三差点走错路",
            "伙伴们互相提醒",
            "断桥出现在眼前",
            "溪水唱着急急的歌",
            "老大先安慰大家",
            "刺猬找到藤蔓",
            "奇怪动物递来木板",
            "大家一起搭小桥",
            "桥面亮起花纹",
            "安全走过小溪",
            "花香从远处飘来",
            "树门慢慢打开",
            "世外桃源出现",
            "花树村欢迎客人",
            "小猫画下新朋友",
            "眨眼果变成星灯",
            "回家的路也发光",
            "森林桃源的约定",
        ]
        shot_cycle = ["wide", "medium", "closeup", "detail", "action"]
        pages: list[dict[str, Any]] = []

        for page_number in range(1, 33):
            timeline_node = timeline_by_order[
                min((page_number - 1) // 4, len(timeline_by_order) - 1)
            ]
            panel_count = (page_number - 1) % 4 + 1
            panels = []

            for panel_index in range(1, panel_count + 1):
                panel_id = f"panel_{page_number:03d}_{panel_index:02d}"
                shot_type = shot_cycle[(page_number + panel_index - 2) % len(shot_cycle)]
                panels.append(
                    {
                        "id": panel_id,
                        "panelNumber": panel_index,
                        "shotType": shot_type,
                        "sceneDescription": (
                            f"{timeline_node['title']}的第 {panel_index} 个画面，"
                            "角色在彩色森林里推进冒险。"
                        ),
                        "characters": ["主角小队"],
                        "narration": self._short_narration(page_number, panel_index),
                        "dialogue": self._short_dialogue(page_number, panel_index),
                        "imagePrompt": (
                            "color chinese japanese children comic panel, "
                            f"{timeline_node['title']}, page {page_number}, panel {panel_index}"
                        ),
                    }
                )

            pages.append(
                {
                    "pageNumber": page_number,
                    "title": page_titles[page_number - 1],
                    "storyBeat": timeline_node["summary"],
                    "panels": panels,
                    "pageNote": "MVP 脚本页：后续 M4 会为这些分镜补充 mock 彩色漫画图像。",
                }
            )

        return pages

    def make_child_safe_concept(self, concept: str) -> str:
        safe_concept = concept.strip()
        for unsafe_word, safe_word in UNSAFE_REPLACEMENTS.items():
            safe_concept = safe_concept.replace(unsafe_word, safe_word)
        return safe_concept

    def _short_narration(self, page_number: int, panel_index: int) -> str | None:
        if panel_index != 1:
            return None
        notes = [
            "森林轻轻亮了起来。",
            "他们继续向前走。",
            "新的线索出现了。",
            "大家靠得更近了。",
        ]
        return notes[(page_number - 1) % len(notes)]

    def _short_dialogue(self, page_number: int, panel_index: int) -> list[dict[str, str]]:
        if panel_index == 1:
            return [{"characterId": "老大", "text": "我们一起想办法。"}]
        if panel_index == 2:
            return [{"characterId": "老二", "text": "我看到线索了。"}]
        if panel_index == 3:
            return [{"characterId": "老三", "text": "这里真奇妙！"}]
        return [{"characterId": "伙伴", "text": "慢慢来，很安全。"}]
