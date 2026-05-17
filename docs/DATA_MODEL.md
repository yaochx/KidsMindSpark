# 数据模型

MVP 使用本地 JSON 保存。字段命名建议在前后端保持一致。

## Story

```ts
type Story = {
  id: string;
  title: string;
  concept: string;
  safeConcept: string;
  targetAge: string;
  visualStyle: "chinese_color_comic" | "japanese_color_manga" | "mixed_east_asian_color_comic";
  status: "draft" | "outlined" | "timeline_confirmed" | "script_generated" | "preview_generated" | "exported";
  characters: Character[];
  timeline: TimelineNode[];
  pages: ScriptPage[];
  images: ComicImage[];
  exportJobs: ExportJob[];
  createdAt: string;
  updatedAt: string;
};
```

## Character

```ts
type Character = {
  id: string;
  name: string;
  role: "hero" | "companion" | "helper" | "obstacle" | "mystery";
  ageLabel?: string;
  personality: string;
  appearance: string;
  colorPalette: string[];
};
```

## TimelineNode

```ts
type TimelineNode = {
  id: string;
  type: "opening" | "hero" | "goal" | "companion" | "obstacle" | "twist" | "crisis" | "resolution" | "ending";
  title: string;
  summary: string;
  order: number;
  x?: number;
  y?: number;
  nextNodeIds: string[];
};
```

## ScriptPage

```ts
type ScriptPage = {
  pageNumber: number;
  title: string;
  storyBeat: string;
  panels: Panel[];
  pageNote: string;
};
```

## Panel

```ts
type Panel = {
  id: string;
  panelNumber: number;
  shotType: "wide" | "medium" | "closeup" | "detail" | "action";
  sceneDescription: string;
  characters: string[];
  narration?: string;
  dialogue: {
    characterId: string;
    text: string;
  }[];
  imagePrompt: string;
  imageId?: string;
};
```

## ComicImage

```ts
type ComicImage = {
  id: string;
  panelId: string;
  provider: "mock" | "real";
  status: "pending" | "generated" | "failed";
  uri: string;
  prompt: string;
  promptHash?: string;
  width: number;
  height: number;
  style: string;
};
```

## ExportJob

```ts
type ExportJob = {
  id: string;
  storyId: string;
  format: "a4_preview_pdf" | "future_32k_print_pdf";
  status: "pending" | "running" | "completed" | "failed";
  outputUri?: string;
  createdAt: string;
  completedAt?: string;
  errorMessage?: string;
};
```

## 完整 JSON 示例

示例故事原始概念包含“三只小猫老大老二老三，拿着猎枪去森林流浪冒险，遇到刺猬、眼珠和奇怪动物，最后发现一座世外桃源。”儿童适龄版本中，“猎枪”被改写为“木头探险杖”。

```json
{
  "id": "story_cat_adventure_001",
  "title": "三只小猫的森林桃源",
  "concept": "三只小猫老大老二老三，拿着猎枪去森林流浪冒险，遇到刺猬、眼珠和奇怪动物，最后发现一座世外桃源。",
  "safeConcept": "三只小猫老大、老二、老三，带着木头探险杖去森林冒险，遇到刺猬、会眨眼的神秘果实和奇怪动物，最后发现一座世外桃源。",
  "targetAge": "小学 1-4 年级",
  "visualStyle": "mixed_east_asian_color_comic",
  "status": "preview_generated",
  "characters": [
    {
      "id": "char_cat_big",
      "name": "老大",
      "role": "hero",
      "ageLabel": "小猫哥哥",
      "personality": "勇敢、爱照顾大家",
      "appearance": "橘色小猫，背着蓝色小包",
      "colorPalette": ["#F59E0B", "#2563EB", "#FFFFFF"]
    },
    {
      "id": "char_cat_middle",
      "name": "老二",
      "role": "companion",
      "ageLabel": "小猫姐姐",
      "personality": "聪明、喜欢观察",
      "appearance": "白色小猫，戴红色围巾",
      "colorPalette": ["#FFFFFF", "#DC2626", "#111827"]
    },
    {
      "id": "char_cat_little",
      "name": "老三",
      "role": "companion",
      "ageLabel": "小猫弟弟",
      "personality": "好奇、容易兴奋",
      "appearance": "灰色小猫，拿着木头探险杖",
      "colorPalette": ["#9CA3AF", "#92400E", "#FDE68A"]
    },
    {
      "id": "char_hedgehog",
      "name": "刺猬爷爷",
      "role": "helper",
      "personality": "慢吞吞但很可靠",
      "appearance": "戴草帽的小刺猬",
      "colorPalette": ["#8B5E3C", "#84CC16", "#FACC15"]
    },
    {
      "id": "char_blink_fruit",
      "name": "眨眼果",
      "role": "mystery",
      "personality": "调皮、会发光",
      "appearance": "像眼睛一样会眨动的蓝色果实",
      "colorPalette": ["#38BDF8", "#1D4ED8", "#F8FAFC"]
    }
  ],
  "timeline": [
    {
      "id": "node_opening",
      "type": "opening",
      "title": "森林边的小路",
      "summary": "三只小猫听说森林深处有一条会发光的小溪。",
      "order": 1,
      "x": 0,
      "y": 0,
      "nextNodeIds": ["node_hero"]
    },
    {
      "id": "node_hero",
      "type": "hero",
      "title": "三只小猫出发",
      "summary": "老大、老二、老三带上地图和木头探险杖。",
      "order": 2,
      "x": 240,
      "y": 0,
      "nextNodeIds": ["node_goal"]
    },
    {
      "id": "node_goal",
      "type": "goal",
      "title": "寻找发光小溪",
      "summary": "他们想找到小溪，并画下森林里最美的地方。",
      "order": 3,
      "x": 480,
      "y": 0,
      "nextNodeIds": ["node_companion"]
    },
    {
      "id": "node_companion",
      "type": "companion",
      "title": "遇见刺猬爷爷",
      "summary": "刺猬爷爷提醒他们要听森林的声音。",
      "order": 4,
      "x": 720,
      "y": 0,
      "nextNodeIds": ["node_obstacle"]
    },
    {
      "id": "node_obstacle",
      "type": "obstacle",
      "title": "迷路的雾",
      "summary": "白雾升起，小路不见了，奇怪动物在树后偷看。",
      "order": 5,
      "x": 960,
      "y": 0,
      "nextNodeIds": ["node_twist"]
    },
    {
      "id": "node_twist",
      "type": "twist",
      "title": "眨眼果指路",
      "summary": "会眨眼的蓝色果实排成箭头，带他们走向山洞。",
      "order": 6,
      "x": 1200,
      "y": 0,
      "nextNodeIds": ["node_crisis"]
    },
    {
      "id": "node_crisis",
      "type": "crisis",
      "title": "断桥前的选择",
      "summary": "通往小溪的木桥断了，老三的探险杖也掉进水里。",
      "order": 7,
      "x": 1440,
      "y": 0,
      "nextNodeIds": ["node_resolution"]
    },
    {
      "id": "node_resolution",
      "type": "resolution",
      "title": "大家一起搭桥",
      "summary": "小猫、刺猬和奇怪动物用藤蔓和木板搭起安全小桥。",
      "order": 8,
      "x": 1680,
      "y": 0,
      "nextNodeIds": ["node_ending"]
    },
    {
      "id": "node_ending",
      "type": "ending",
      "title": "发现世外桃源",
      "summary": "他们找到发光小溪和花树村，明白冒险要靠合作。",
      "order": 9,
      "x": 1920,
      "y": 0,
      "nextNodeIds": []
    }
  ],
  "pages": [
    {
      "pageNumber": 1,
      "title": "森林的邀请",
      "storyBeat": "三只小猫在家门口发现一张发光树叶地图。",
      "pageNote": "开场页，明亮温暖。",
      "panels": [
        {
          "id": "panel_001_01",
          "panelNumber": 1,
          "shotType": "wide",
          "sceneDescription": "村口小路，三只小猫围着一片发光树叶。",
          "characters": ["char_cat_big", "char_cat_middle", "char_cat_little"],
          "narration": "清晨，森林送来一封闪亮的邀请。",
          "dialogue": [
            {
              "characterId": "char_cat_little",
              "text": "它在发光！"
            }
          ],
          "imagePrompt": "color east asian children's comic, three kittens finding a glowing leaf map near a forest path",
          "imageId": "img_panel_001_01"
        },
        {
          "id": "panel_001_02",
          "panelNumber": 2,
          "shotType": "medium",
          "sceneDescription": "老大举起地图，老二认真看路线，老三拿着木头探险杖。",
          "characters": ["char_cat_big", "char_cat_middle", "char_cat_little"],
          "dialogue": [
            {
              "characterId": "char_cat_big",
              "text": "我们一起去看看。"
            },
            {
              "characterId": "char_cat_middle",
              "text": "先记好回家的路。"
            }
          ],
          "imagePrompt": "warm colorful manga style, kitten siblings preparing for a safe forest adventure with a wooden explorer staff",
          "imageId": "img_panel_001_02"
        }
      ]
    },
    {
      "pageNumber": 32,
      "title": "花树村的约定",
      "storyBeat": "小猫们在世外桃源画下新朋友，并约定以后守护森林。",
      "pageNote": "结尾页，明亮、安心、充满希望。",
      "panels": [
        {
          "id": "panel_032_01",
          "panelNumber": 1,
          "shotType": "wide",
          "sceneDescription": "发光小溪旁，花树村展开在阳光里。",
          "characters": ["char_cat_big", "char_cat_middle", "char_cat_little", "char_hedgehog"],
          "narration": "森林深处，真的有一座温柔的花树村。",
          "dialogue": [],
          "imagePrompt": "beautiful colorful chinese japanese comic, hidden paradise village beside glowing creek, kitten adventurers smiling",
          "imageId": "img_panel_032_01"
        },
        {
          "id": "panel_032_02",
          "panelNumber": 2,
          "shotType": "medium",
          "sceneDescription": "三只小猫和新朋友一起看着画册。",
          "characters": ["char_cat_big", "char_cat_middle", "char_cat_little", "char_hedgehog", "char_blink_fruit"],
          "dialogue": [
            {
              "characterId": "char_cat_middle",
              "text": "这是我们的森林朋友。"
            },
            {
              "characterId": "char_cat_big",
              "text": "以后一起守护这里。"
            }
          ],
          "imagePrompt": "children's color manga ending, kitten siblings sharing a sketchbook with forest friends in a paradise village",
          "imageId": "img_panel_032_02"
        }
      ]
    }
  ],
  "images": [
    {
      "id": "img_panel_001_01",
      "panelId": "panel_001_01",
      "provider": "mock",
      "status": "generated",
      "uri": "/mock-images/color-comic-placeholder-001.svg",
      "prompt": "color east asian children's comic, three kittens finding a glowing leaf map near a forest path",
      "promptHash": "optional-sha256-prompt-hash-for-real-image-provider",
      "width": 1024,
      "height": 768,
      "style": "mixed_east_asian_color_comic"
    },
    {
      "id": "img_panel_032_02",
      "panelId": "panel_032_02",
      "provider": "mock",
      "status": "generated",
      "uri": "/mock-images/color-comic-placeholder-032.svg",
      "prompt": "children's color manga ending, kitten siblings sharing a sketchbook with forest friends in a paradise village",
      "promptHash": "optional-sha256-prompt-hash-for-real-image-provider",
      "width": 1024,
      "height": 768,
      "style": "mixed_east_asian_color_comic"
    }
  ],
  "exportJobs": [
    {
      "id": "export_001",
      "storyId": "story_cat_adventure_001",
      "format": "a4_preview_pdf",
      "status": "completed",
      "outputUri": "/exports/story_cat_adventure_001_a4_preview.pdf",
      "createdAt": "2026-05-16T10:00:00+08:00",
      "completedAt": "2026-05-16T10:01:00+08:00"
    }
  ],
  "createdAt": "2026-05-16T09:30:00+08:00",
  "updatedAt": "2026-05-16T10:01:00+08:00"
}
```

说明：完整运行时 `pages` 必须包含 1-32 全部页面。上方示例为文档可读性展示第 1 页和第 32 页，实际数据不得省略中间页。
