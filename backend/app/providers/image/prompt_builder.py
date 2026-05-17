from __future__ import annotations

import hashlib
from typing import Any

from ..errors import ProviderResponseError


def build_panel_image_prompt(
    story: dict[str, Any], page: dict[str, Any], panel: dict[str, Any]
) -> str:
    image_prompt = str(panel.get("imagePrompt", "")).strip()
    if not image_prompt:
        raise ProviderResponseError(
            "IMAGE_PROMPT_REQUIRED",
            "分镜缺少 imagePrompt，无法生成图片。",
            {"panelId": str(panel.get("id", ""))},
        )

    dialogue_lines = _dialogue_prompt(panel)
    prompt_sections = [
        "你正在生成一张儿童彩色漫画单格画面。",
        "",
        "故事信息：",
        f"- 标题：{_text(story.get('title'), '未命名故事')}",
        f"- 页码：第 {_text(page.get('pageNumber'), '未知')} 页",
        f"- 分镜：第 {_text(panel.get('panelNumber'), '未知')} 格",
        f"- 当前页标题：{_text(page.get('title'), '未命名页面')}",
        f"- 当前页剧情：{_text(page.get('storyBeat'), '继续推进故事')}",
        "",
        "角色设定：",
        _character_prompt(story, panel),
        "",
        "画面描述：",
        f"- 场景：{_text(panel.get('sceneDescription'), '儿童友好的奇妙场景')}",
        f"- 镜头：{_shot_type_label(panel.get('shotType'))}",
        f"- 动作与情绪：{_text(panel.get('narration'), '角色自然行动，表情清晰')}",
        f"- 核心画面：{image_prompt}",
        "",
        "对白气泡：",
        dialogue_lines,
        "",
        "构图要求：",
        "- 只生成一个单格漫画画面，不要生成整页拼图。",
        "- 不要生成页码、分镜编号、标题栏、水印或额外文字。",
        "- 主体清晰，不要贴边，适合彩色中式/日式儿童漫画。",
        "- 中文对白气泡不要遮挡角色脸部、关键动作或重要线索。",
        "",
        "安全要求：",
        "- 儿童适龄，温暖、明亮、冒险但安全。",
        "- 不要真实武器，不要血腥、恐怖、危险行为。",
        "- 如果原始概念出现危险道具，用木头探险杖、玩具探险杖等安全道具表达。",
    ]
    return "\n".join(prompt_sections)


def build_panel_prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def _character_prompt(story: dict[str, Any], panel: dict[str, Any]) -> str:
    characters = story.get("characters", [])
    if isinstance(characters, list) and characters:
        descriptions = []
        for character in characters:
            if not isinstance(character, dict):
                continue
            name = _text(character.get("name") or character.get("id"), "角色")
            role = _text(character.get("role"), "故事角色")
            description = _text(character.get("description"), "")
            visual_prompt = _text(character.get("visualPrompt"), "")
            parts = [name, role]
            if description:
                parts.append(description)
            if visual_prompt:
                parts.append(f"外观：{visual_prompt}")
            descriptions.append(" - ".join(parts))
        if descriptions:
            return "\n".join(f"- {description}" for description in descriptions)

    panel_characters = panel.get("characters", [])
    if isinstance(panel_characters, list) and panel_characters:
        names = "、".join(str(character) for character in panel_characters if str(character).strip())
        if names:
            return f"- 本格角色：{names}"
    return "- 保持已生成故事中的主角和伙伴外观一致。"


def _dialogue_prompt(panel: dict[str, Any]) -> str:
    dialogue = panel.get("dialogue", [])
    if not isinstance(dialogue, list) or not dialogue:
        return "- 本格无对白。不要生成任何文字，不要生成对白气泡。"

    lines = [
        "- 请生成清晰中文漫画对白气泡。",
        "- 气泡内只允许写对白文本，不得写角色名、冒号、编号或额外旁白。",
        "- 说话角色必须通过气泡尾巴、指向线和靠近对应角色的位置表达。",
        "- 多个气泡按从左到右、从上到下的阅读顺序排列。",
    ]
    for index, line in enumerate(dialogue, start=1):
        if not isinstance(line, dict):
            continue
        speaker = _text(line.get("characterId"), "对应角色")
        text = _text(line.get("text"), "")
        if not text:
            continue
        lines.append(
            f"- 气泡 {index} 靠近或尾巴指向 {speaker}，气泡内只写：{text}"
        )
    return "\n".join(lines)


def _shot_type_label(shot_type: object) -> str:
    labels = {
        "wide": "远景，交代环境和角色位置",
        "medium": "中景，突出角色互动",
        "closeup": "近景，突出表情",
        "detail": "特写，突出关键道具或线索",
        "action": "动作镜头，突出动态和速度感",
    }
    return labels.get(str(shot_type), _text(shot_type, "中景"))


def _text(value: object, fallback: str) -> str:
    text = str(value or "").strip()
    return text if text else fallback
