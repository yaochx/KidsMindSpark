"use client";

import { FormEvent, useMemo, useState } from "react";
import { ScriptPageList } from "@/components/script/ScriptPageList";
import { TimelineConfirmation } from "@/components/timeline/TimelineConfirmation";
import { createStoryOutline } from "@/lib/api/story";
import type {
  StoryOutlineResponse,
  VisualStyle
} from "@/lib/types/story";

const targetAgeOptions = ["小学 1-4 年级", "小学 5-6 年级"];

const visualStyleOptions: { label: string; value: VisualStyle }[] = [
  { label: "中式彩色漫画", value: "chinese_color_comic" },
  { label: "日式彩色漫画", value: "japanese_color_manga" },
  { label: "中日混合彩色漫画", value: "mixed_east_asian_color_comic" }
];

const exampleConcept =
  "三只小猫老大老二老三，拿着猎枪去森林流浪冒险，遇到刺猬、眼珠和奇怪动物，最后发现一座世外桃源。";

export function StoryInputForm() {
  const [title, setTitle] = useState("三只小猫的森林桃源");
  const [concept, setConcept] = useState(exampleConcept);
  const [targetAge, setTargetAge] = useState(targetAgeOptions[0]);
  const [visualStyle, setVisualStyle] = useState<VisualStyle>(
    "mixed_east_asian_color_comic"
  );
  const [outline, setOutline] = useState<StoryOutlineResponse | null>(null);
  const [isTimelineConfirmed, setIsTimelineConfirmed] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const canSubmit = useMemo(
    () => title.trim().length > 0 && concept.trim().length >= 8 && !isLoading,
    [concept, isLoading, title]
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!canSubmit) {
      setError("请填写标题和至少 8 个字的故事概念。");
      return;
    }

    setIsLoading(true);
    setError("");
    setOutline(null);
    setIsTimelineConfirmed(false);

    try {
      const result = await createStoryOutline({
        title: title.trim(),
        concept: concept.trim(),
        targetAge,
        visualStyle
      });
      setOutline(result);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "生成失败，请重试。");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="flex flex-col gap-6">
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
        <form
          className="flex flex-col gap-5 rounded-lg border border-amber-200 bg-white p-5 shadow-sm"
          onSubmit={handleSubmit}
        >
          <div>
            <label className="text-base font-semibold text-ink" htmlFor="title">
              故事标题
            </label>
            <input
              className="mt-2 w-full rounded-md border border-slate-300 px-4 py-3 text-base outline-none transition focus:border-leaf focus:ring-2 focus:ring-green-100"
              id="title"
              maxLength={40}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="给故事起一个名字"
              value={title}
            />
          </div>

          <div>
            <label className="text-base font-semibold text-ink" htmlFor="concept">
              故事概念
            </label>
            <textarea
              className="mt-2 min-h-40 w-full resize-y rounded-md border border-slate-300 px-4 py-3 text-base leading-7 outline-none transition focus:border-leaf focus:ring-2 focus:ring-green-100"
              id="concept"
              maxLength={500}
              onChange={(event) => setConcept(event.target.value)}
              placeholder="写下角色、地点、想遇到的事情和结局"
              value={concept}
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="text-base font-semibold text-ink" htmlFor="age">
                目标读者
              </label>
              <select
                className="mt-2 w-full rounded-md border border-slate-300 px-4 py-3 text-base outline-none transition focus:border-leaf focus:ring-2 focus:ring-green-100"
                id="age"
                onChange={(event) => setTargetAge(event.target.value)}
                value={targetAge}
              >
                {targetAgeOptions.map((option) => (
                  <option key={option}>{option}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-base font-semibold text-ink" htmlFor="style">
                漫画风格
              </label>
              <select
                className="mt-2 w-full rounded-md border border-slate-300 px-4 py-3 text-base outline-none transition focus:border-leaf focus:ring-2 focus:ring-green-100"
                id="style"
                onChange={(event) =>
                  setVisualStyle(event.target.value as VisualStyle)
                }
                value={visualStyle}
              >
                {visualStyleOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {error ? (
            <p className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-base text-red-700">
              {error}
            </p>
          ) : null}

          <button
            className="min-h-11 rounded-md bg-leaf px-5 py-3 text-base font-semibold text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:bg-slate-300"
            disabled={!canSubmit}
            type="submit"
          >
            {isLoading ? "正在整理核心设定" : "生成故事核心设定"}
          </button>
        </form>

        <aside className="flex flex-col gap-4">
          <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-xl font-semibold text-ink">M5 范围</h2>
            <p className="mt-3 text-base leading-7 text-slate-700">
              本阶段可以生成 16-48 页分镜脚本、彩色 mock 漫画预览，并导出 A4 PDF 预览。
            </p>
          </section>

          {outline ? (
            <section className="rounded-lg border border-green-200 bg-green-50 p-5 shadow-sm">
              <p className="text-sm font-semibold text-leaf">已生成核心设定</p>
              <h2 className="mt-2 text-xl font-semibold text-ink">
                {outline.title}
              </h2>
              <p className="mt-3 text-base leading-7 text-slate-700">
                {outline.safeConcept}
              </p>
              <p className="mt-4 rounded-md bg-white px-4 py-3 text-sm font-semibold text-slate-700">
                现在可以生成图形化故事主线。
              </p>
            </section>
          ) : (
            <section className="rounded-lg border border-dashed border-slate-300 bg-white p-5">
              <h2 className="text-xl font-semibold text-ink">等待输入</h2>
              <p className="mt-3 text-base leading-7 text-slate-700">
                提交后会得到儿童适龄改写后的故事核心设定。
              </p>
            </section>
          )}
        </aside>
      </div>

      {outline ? (
        <>
          <TimelineConfirmation
            onConfirmed={() => setIsTimelineConfirmed(true)}
            storyId={outline.storyId}
          />
          <ScriptPageList
            canGenerate={isTimelineConfirmed}
            storyId={outline.storyId}
          />
        </>
      ) : null}
    </section>
  );
}
