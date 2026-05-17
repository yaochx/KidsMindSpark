"use client";

import { useState } from "react";
import { createStoryTimeline, updateStoryTimeline } from "@/lib/api/story";
import type { TimelineNode } from "@/lib/types/timeline";

const nodeLabels: Record<TimelineNode["type"], string> = {
  opening: "开场",
  hero: "主角",
  goal: "目标",
  companion: "伙伴",
  obstacle: "阻碍",
  twist: "转折",
  crisis: "危机",
  resolution: "解决",
  ending: "结局"
};

type TimelineConfirmationProps = {
  storyId: string;
  onConfirmed?: () => void;
};

export function TimelineConfirmation({
  storyId,
  onConfirmed
}: TimelineConfirmationProps) {
  const [timeline, setTimeline] = useState<TimelineNode[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState("");
  const [status, setStatus] = useState<"idle" | "ready" | "confirmed">("idle");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const selectedNode =
    timeline.find((node) => node.id === selectedNodeId) ?? timeline[0];

  async function handleGenerateTimeline() {
    setIsLoading(true);
    setError("");

    try {
      const result = await createStoryTimeline({ storyId });
      const sortedTimeline = [...result.timeline].sort(
        (first, second) => first.order - second.order
      );
      setTimeline(sortedTimeline);
      setSelectedNodeId(sortedTimeline[0]?.id ?? "");
      setStatus(result.status === "timeline_confirmed" ? "confirmed" : "ready");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "主线生成失败，请重试。");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleConfirmTimeline() {
    if (timeline.length === 0) {
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const result = await updateStoryTimeline({
        storyId,
        timeline,
        confirmed: true
      });
      setTimeline(result.timeline);
      setStatus("confirmed");
      onConfirmed?.();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "主线确认失败，请重试。");
    } finally {
      setIsLoading(false);
    }
  }

  function updateSelectedSummary(summary: string) {
    if (!selectedNode) {
      return;
    }
    setTimeline((current) =>
      current.map((node) =>
        node.id === selectedNode.id ? { ...node, summary } : node
      )
    );
    if (status === "confirmed") {
      setStatus("ready");
    }
  }

  return (
    <section className="rounded-lg border border-sky-200 bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-sm font-semibold text-sky-700">M2 主线确认页</p>
          <h2 className="mt-2 text-2xl font-bold text-ink">图形化故事主线</h2>
          <p className="mt-3 max-w-2xl text-base leading-7 text-slate-700">
            先确认这 9 个故事节点。确认后，下一阶段才能生成固定 32 页漫画分镜。
          </p>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row">
          <button
            className="min-h-11 rounded-md border border-sky-300 bg-white px-5 py-3 text-base font-semibold text-sky-800 transition hover:bg-sky-50 disabled:cursor-not-allowed disabled:border-slate-200 disabled:text-slate-400"
            disabled={isLoading}
            onClick={handleGenerateTimeline}
            type="button"
          >
            {timeline.length ? "重新生成主线" : "生成图形化主线"}
          </button>

          <button
            className="min-h-11 rounded-md bg-leaf px-5 py-3 text-base font-semibold text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:bg-slate-300"
            disabled={isLoading || timeline.length === 0}
            onClick={handleConfirmTimeline}
            type="button"
          >
            {status === "confirmed" ? "已确认主线" : "确认主线"}
          </button>
        </div>
      </div>

      {error ? (
        <p className="mt-5 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-base text-red-700">
          {error}
        </p>
      ) : null}

      {status === "confirmed" ? (
        <p className="mt-5 rounded-md border border-green-200 bg-green-50 px-4 py-3 text-base font-semibold text-green-800">
          主线已确认。下一步是 M3：基于已确认主线生成固定 32 页分镜脚本。
        </p>
      ) : null}

      {timeline.length ? (
        <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1fr)_320px]">
          <div className="overflow-x-auto rounded-lg border border-slate-200 bg-slate-50 p-4">
            <div className="flex min-w-max items-stretch gap-4">
              {timeline.map((node, index) => (
                <div className="flex items-center gap-4" key={node.id}>
                  <button
                    className={`flex min-h-28 w-56 shrink-0 flex-col rounded-lg border bg-white p-4 text-left shadow-sm transition ${
                      selectedNode?.id === node.id
                        ? "border-sky-500 ring-2 ring-sky-100"
                        : "border-slate-200 hover:border-sky-300"
                    }`}
                    onClick={() => setSelectedNodeId(node.id)}
                    type="button"
                  >
                    <span className="text-xs font-bold text-sky-700">
                      {String(node.order).padStart(2, "0")} ·{" "}
                      {nodeLabels[node.type]}
                    </span>
                    <span className="mt-2 text-lg font-bold text-ink">
                      {node.title}
                    </span>
                    <span className="mt-2 line-clamp-2 text-sm leading-6 text-slate-600">
                      {node.summary}
                    </span>
                  </button>
                  {index < timeline.length - 1 ? (
                    <span className="text-2xl font-bold text-sky-500">→</span>
                  ) : null}
                </div>
              ))}
            </div>
          </div>

          <aside className="rounded-lg border border-slate-200 bg-white p-5">
            {selectedNode ? (
              <>
                <p className="text-sm font-semibold text-sky-700">
                  {nodeLabels[selectedNode.type]}
                </p>
                <h3 className="mt-2 text-xl font-bold text-ink">
                  {selectedNode.title}
                </h3>
                <label
                  className="mt-4 block text-base font-semibold text-ink"
                  htmlFor="node-summary"
                >
                  节点摘要
                </label>
                <textarea
                  className="mt-2 min-h-36 w-full resize-y rounded-md border border-slate-300 px-4 py-3 text-base leading-7 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
                  id="node-summary"
                  maxLength={120}
                  onChange={(event) => updateSelectedSummary(event.target.value)}
                  value={selectedNode.summary}
                />
                <p className="mt-3 text-sm leading-6 text-slate-500">
                  摘要最多 120 字，节点卡片只展示前几行，避免图形重叠。
                </p>
              </>
            ) : null}
          </aside>
        </div>
      ) : (
        <div className="mt-6 rounded-lg border border-dashed border-slate-300 bg-slate-50 p-6">
          <h3 className="text-xl font-semibold text-ink">尚未生成主线</h3>
          <p className="mt-3 text-base leading-7 text-slate-700">
            点击“生成图形化主线”后，会出现开场、主角、目标、伙伴、阻碍、转折、危机、解决、结局 9 个节点。
          </p>
        </div>
      )}
    </section>
  );
}
