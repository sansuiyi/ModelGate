"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { getCustomers, getModels, sendPrompt } from "@/lib/api";
import type { CustomerProfile, ModelConfig } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { PlaygroundSkeleton } from "@/components/Skeletons";

interface HistoryEntry {
  prompt: string;
  response: string;
  routing: Record<string, string>;
  timestamp: string;
}

// The most expensive model that would be used without ModelGate
const PREMIUM_MODEL = {
  name: "gemini-2.5-pro",
  provider: "google",
  cost_per_m_input: 2.50,
  cost_per_m_output: 15.00,
  avg_latency_ms: 1500,
};

export default function PlaygroundPage() {
  return (
    <Suspense fallback={<div className="text-muted-foreground text-sm animate-pulse">加载中...</div>}>
      <PlaygroundContent />
    </Suspense>
  );
}

const TIER_LABELS: Record<string, string> = { simple: "简单", medium: "中等", complex: "复杂" };

const QUICK_PROMPTS = [
  { label: "简单", tier: "simple", text: "你的退货政策是什么？", color: "border-green-500/30 text-green-400 hover:bg-green-500/10" },
  { label: "中等", tier: "medium", text: "总结我的电子产品购买的保修范围，并说明延长保护计划包含哪些内容", color: "border-amber-500/30 text-amber-400 hover:bg-amber-500/10" },
  { label: "复杂", tier: "complex", text: "分析多个产品保修索赔的责任风险，评估当前保单结构中的覆盖缺口，并推荐一个综合解决方案，在保持客户满意度的同时将法律风险降至最低", color: "border-red-500/30 text-red-400 hover:bg-red-500/10" },
];

function PlaygroundContent() {
  const searchParams = useSearchParams();
  const [customers, setCustomers] = useState<CustomerProfile[]>([]);
  const [allModels, setAllModels] = useState<ModelConfig[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState("");
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [pageLoading, setPageLoading] = useState(true);
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  useEffect(() => {
    Promise.all([getCustomers(), getModels()]).then(([c, m]) => {
      setCustomers(c);
      setAllModels(m);
      const pre = searchParams.get("customer");
      setSelectedCustomer(pre || (c.length > 0 ? c[0].customer_id : ""));
    }).finally(() => setPageLoading(false));
  }, [searchParams]);

  if (pageLoading) return <PlaygroundSkeleton />;

  const handleSend = async () => {
    if (!selectedCustomer || !prompt.trim()) return;
    setLoading(true);
    try {
      const result = await sendPrompt(selectedCustomer, prompt);
      setHistory((prev) => [{ prompt, response: result.response, routing: result.routing, timestamp: new Date().toLocaleTimeString() }, ...prev]);
      setPrompt("");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const selected = customers.find((c) => c.customer_id === selectedCustomer);

  // Find the most expensive model for "without ModelGate" comparison
  const premiumModelRaw = allModels.length > 0
    ? allModels.reduce((prev, curr) => curr.cost_per_m_input > prev.cost_per_m_input ? curr : prev, allModels[0])
    : null;
  const premiumModel = premiumModelRaw
    ? { name: premiumModelRaw.model_name, provider: premiumModelRaw.provider, cost_per_m_input: premiumModelRaw.cost_per_m_input, cost_per_m_output: premiumModelRaw.cost_per_m_output, avg_latency_ms: premiumModelRaw.avg_latency_ms }
    : null;

  return (
    <div className="space-y-5 animate-in fade-in duration-500">
      <div>
        <h1 className="text-xl font-bold tracking-tight">测试台</h1>
        <p className="text-xs text-muted-foreground mt-0.5">实时测试提示词路由</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left panel */}
        <div className="lg:col-span-4 space-y-4">
          {/* Customer selector */}
          <Card className="bg-card/50 border-border/50">
            <CardHeader className="pb-2"><CardTitle className="text-xs uppercase tracking-widest text-muted-foreground">客户</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              <select
                value={selectedCustomer}
                onChange={(e) => setSelectedCustomer(e.target.value)}
                className="w-full bg-secondary/50 border border-border/50 rounded-md px-3 py-2 text-sm text-foreground"
              >
                {customers.map((c) => (
                  <option key={c.customer_id} value={c.customer_id}>{c.customer_name}</option>
                ))}
              </select>
              {selected && (
                <div className="space-y-1 text-[10px]">
                  <div className="flex items-center justify-between text-muted-foreground">
                    <span>目标</span><span className="font-mono text-primary">{selected.objective.replace(/_/g, " ")}</span>
                  </div>
                  <div className="flex items-center justify-between text-muted-foreground">
                    <span>区域</span><span className="font-mono text-blue-400">{selected.constraints.region}</span>
                  </div>
                  <div className="flex items-center justify-between text-muted-foreground">
                    <span>延迟目标</span><span className="font-mono">{selected.performance.latency_target_ms}ms</span>
                  </div>
                  {selected.constraints.forbidden_providers.length > 0 && (
                    <div className="flex items-center justify-between text-muted-foreground">
                      <span>已屏蔽</span>
                      <span className="font-mono text-red-400">{selected.constraints.forbidden_providers.join(", ")}</span>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Prompt input */}
          <Card className="bg-card/50 border-border/50">
            <CardHeader className="pb-2"><CardTitle className="text-xs uppercase tracking-widest text-muted-foreground">提示词</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <Textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="请输入你的提示词..."
                rows={4}
                className="bg-secondary/30 border-border/50 text-sm resize-none"
                onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleSend(); }}
              />
              <Button onClick={handleSend} disabled={loading || !prompt.trim() || !selectedCustomer} className="w-full text-xs">
                {loading ? (
                  <span className="flex items-center gap-2">
                    <span className="animate-spin h-3 w-3 border-2 border-primary-foreground border-t-transparent rounded-full" />
                    路由中...
                  </span>
                ) : "发送"}
              </Button>
              <div className="text-[9px] text-muted-foreground text-center">按 Ctrl+Enter 发送</div>
            </CardContent>
          </Card>

          {/* Quick prompts */}
          <Card className="bg-card/50 border-border/50">
            <CardHeader className="pb-2"><CardTitle className="text-xs uppercase tracking-widest text-muted-foreground">快捷提示</CardTitle></CardHeader>
            <CardContent className="space-y-1.5">
              {QUICK_PROMPTS.map((q) => (
                <button
                  key={q.label}
                  onClick={() => setPrompt(q.text)}
                  className={`w-full text-left text-[11px] p-2.5 rounded border transition-colors ${q.color}`}
                >
                  <span className="font-semibold">{q.label}:</span> {q.text.slice(0, 80)}...
                </button>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Right panel - results */}
        <div className="lg:col-span-8 space-y-4">
          {history.length === 0 ? (
            <Card className="bg-card/50 border-border/50">
              <CardContent className="py-20 text-center">
                <div className="text-muted-foreground text-sm">发送提示词以查看路由决策</div>
                <div className="text-[10px] text-muted-foreground mt-1">路由引擎将分类你的提示词并选择最优模型</div>
              </CardContent>
            </Card>
          ) : (
            history.map((entry, i) => {
              const actualModel = entry.routing.model || entry.routing.selected_model || "unknown";
              const actualModelInfo = allModels.find(m => m.model_name === actualModel);
              const actualCost = Number(entry.routing.cost || 0);
              const inputTokens = Number(entry.routing.input_tokens || 0);
              const outputTokens = Number(entry.routing.output_tokens || 0);

              // Compute "without ModelGate" cost: same tokens through premium model
              const premiumRef = premiumModel || PREMIUM_MODEL;
              const premiumCost = inputTokens > 0
                ? (inputTokens / 1_000_000) * premiumRef.cost_per_m_input + (outputTokens / 1_000_000) * premiumRef.cost_per_m_output
                : actualCost * 3; // fallback estimate
              const savings = premiumCost - actualCost;
              const savingsPercent = premiumCost > 0 ? ((savings / premiumCost) * 100) : 0;

              return (
                <Card key={i} className={`bg-card/50 border-border/50 ${i === 0 ? "glow-cyan" : ""}`}>
                  <CardContent className="pt-4 space-y-3">
                    {/* Routing decision panel */}
                    <div className="bg-secondary/30 rounded-lg p-3 space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="text-[9px] uppercase tracking-widest text-muted-foreground">路由决策</div>
                        <span className="text-[10px] text-muted-foreground font-mono">{entry.timestamp}</span>
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        <Badge variant="outline" className={`text-[9px] ${
                          entry.routing.classification === "simple" ? "border-green-500/30 text-green-400"
                          : entry.routing.classification === "complex" ? "border-red-500/30 text-red-400"
                          : "border-amber-500/30 text-amber-400"
                        }`}>{TIER_LABELS[entry.routing.classification] || entry.routing.classification}</Badge>
                        <Badge variant="outline" className="text-[9px] border-primary/30 text-primary">{actualModel}</Badge>
                        {entry.routing.selected_provider && <Badge variant="outline" className="text-[9px]">{entry.routing.selected_provider}</Badge>}
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                        {[
                          { label: "总延迟", value: `${entry.routing.latency || entry.routing.latency_ms || "?"}ms` },
                          { label: "首字延迟", value: `${entry.routing.ttft || entry.routing.ttft_ms || "?"}ms` },
                          { label: "分类耗时", value: `${entry.routing.classifyMs || entry.routing.classify_ms || "?"}ms` },
                          { label: "成本", value: `$${actualCost.toFixed(6)}` },
                        ].map(({ label, value }) => (
                          <div key={label} className="bg-secondary/40 rounded px-2 py-1">
                            <div className="text-[8px] uppercase tracking-widest text-muted-foreground">{label}</div>
                            <div className="text-[11px] font-mono">{value}</div>
                          </div>
                        ))}
                      </div>
                      {entry.routing.reason && (
                        <div className="text-[10px] text-muted-foreground">
                          <span className="text-foreground font-medium">原因： </span>{entry.routing.reason}
                        </div>
                      )}
                      {entry.routing.candidates_eliminated && typeof entry.routing.candidates_eliminated === "object" && Object.keys(entry.routing.candidates_eliminated).length > 0 && (
                        <div className="text-[10px]">
                          <span className="text-muted-foreground">已淘汰： </span>
                          {Object.entries(entry.routing.candidates_eliminated).map(([m, r]) => (
                            <span key={m} className="text-red-400">{m} ({String(r)}) </span>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Side-by-side comparison (Fix #9) */}
                    <div className="grid grid-cols-2 gap-2">
                      <div className="bg-green-500/5 border border-green-500/20 rounded-lg p-2.5">
                        <div className="text-[8px] uppercase tracking-widest text-green-400 mb-1.5 font-medium">使用 ModelGate</div>
                        <div className="space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] text-muted-foreground">模型</span>
                            <span className="text-[10px] font-mono text-green-400">{actualModel}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] text-muted-foreground">提供商</span>
                            <span className="text-[10px] font-mono">{entry.routing.selected_provider || actualModelInfo?.provider || "?"}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] text-muted-foreground">成本</span>
                            <span className="text-[10px] font-mono text-green-400">${actualCost.toFixed(6)}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] text-muted-foreground">平均延迟</span>
                            <span className="text-[10px] font-mono">{actualModelInfo?.avg_latency_ms || entry.routing.latency || "?"}ms</span>
                          </div>
                        </div>
                      </div>
                      <div className="bg-red-500/5 border border-red-500/20 rounded-lg p-2.5">
                        <div className="text-[8px] uppercase tracking-widest text-red-400 mb-1.5 font-medium">不使用 ModelGate</div>
                        <div className="space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] text-muted-foreground">模型</span>
                            <span className="text-[10px] font-mono text-red-400">{premiumRef.name || "premium"}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] text-muted-foreground">提供商</span>
                            <span className="text-[10px] font-mono">{premiumRef.provider || "?"}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] text-muted-foreground">成本</span>
                            <span className="text-[10px] font-mono text-red-400">${premiumCost.toFixed(6)}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] text-muted-foreground">平均延迟</span>
                            <span className="text-[10px] font-mono">{premiumRef.avg_latency_ms}ms</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Savings badge */}
                    {savings > 0 && (
                      <div className="flex items-center justify-center gap-2 py-1">
                        <Badge className="bg-green-500/15 text-green-400 border-green-500/30 text-[10px]">
                          节省 ${savings.toFixed(6)}（降低 ${savingsPercent.toFixed(0)}%）
                        </Badge>
                      </div>
                    )}

                    {/* Prompt */}
                    <div className="text-xs">
                      <span className="text-muted-foreground font-medium">提示词： </span>{entry.prompt}
                    </div>

                    {/* Response */}
                    <div className="bg-primary/5 border border-primary/10 rounded-lg p-3 text-xs leading-relaxed whitespace-pre-wrap max-h-[300px] overflow-y-auto">
                      {entry.response}
                    </div>
                  </CardContent>
                </Card>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
