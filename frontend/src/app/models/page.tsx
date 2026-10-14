"use client";

import { useEffect, useState, useCallback } from "react";
import { getModels, updateModel, addModel, removeModel, searchOpenRouterModels } from "@/lib/api";
import type { ModelConfig, OpenRouterModel } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { ModelsSkeleton } from "@/components/Skeletons";

const TIER_LABELS: Record<string, string> = { simple: "简单", medium: "中等", complex: "复杂" };

const PROVIDER_COLORS: Record<string, string> = {
  anthropic: "border-amber-500/40 text-amber-400",
  openai: "border-green-500/40 text-green-400",
  google: "border-blue-500/40 text-blue-400",
  deepseek: "border-purple-500/40 text-purple-400",
  meta: "border-sky-500/40 text-sky-400",
  "meta-llama": "border-sky-500/40 text-sky-400",
  mistralai: "border-orange-500/40 text-orange-400",
  cohere: "border-rose-500/40 text-rose-400",
  qwen: "border-teal-500/40 text-teal-400",
};

const TIER_COLORS: Record<string, string> = {
  simple: "bg-green-500/15 text-green-400 border-green-500/30",
  medium: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  complex: "bg-red-500/15 text-red-400 border-red-500/30",
};

const TIER_OPTIONS = ["simple", "medium", "complex"];

function slugify(name: string): string {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "").slice(0, 40);
}

export default function ModelsPage() {
  const [models, setModels] = useState<ModelConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState<string | null>(null);

  // Catalog
  const [searchQuery, setSearchQuery] = useState("");
  const [catalogResults, setCatalogResults] = useState<OpenRouterModel[]>([]);
  const [searching, setSearching] = useState(false);
  const [catalogLoaded, setCatalogLoaded] = useState(false);
  const [addingModel, setAddingModel] = useState<string | null>(null);
  const [selectedTier, setSelectedTier] = useState<Record<string, string>>({});

  const refresh = useCallback(() => {
    getModels().then(setModels).catch(console.error);
  }, []);

  // Load models + initial catalog on mount
  useEffect(() => {
    Promise.all([
      getModels(),
      searchOpenRouterModels(""),
    ]).then(([m, catalog]) => {
      setModels(m);
      setCatalogResults(catalog);
      setCatalogLoaded(true);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  const handleToggle = async (model: ModelConfig) => {
    setUpdating(model.model_name);
    try {
      await updateModel(model.model_name, !model.enabled, model.description);
      setModels((prev) =>
        prev.map((m) =>
          m.model_name === model.model_name ? { ...m, enabled: !m.enabled } : m
        )
      );
    } catch (err) {
      console.error(err);
    } finally {
      setUpdating(null);
    }
  };

  const handleRemove = async (modelName: string) => {
    setUpdating(modelName);
    try {
      await removeModel(modelName);
      setModels((prev) => prev.filter((m) => m.model_name !== modelName));
    } catch (err) {
      console.error(err);
    } finally {
      setUpdating(null);
    }
  };

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    setSearching(true);
    try {
      const results = await searchOpenRouterModels(query);
      setCatalogResults(results);
    } catch (err) {
      console.error(err);
    } finally {
      setSearching(false);
    }
  };

  const handleAdd = async (orModel: OpenRouterModel) => {
    const tier = selectedTier[orModel.id] || "medium";
    const friendlyName = slugify(orModel.name || orModel.id.split("/").pop() || orModel.id);
    setAddingModel(orModel.id);
    try {
      await addModel({
        model_name: friendlyName,
        provider: orModel.provider,
        openrouter_id: orModel.id,
        tier,
        cost_per_m_input: orModel.cost_per_m_input || 0,
        cost_per_m_output: orModel.cost_per_m_output || 0,
        avg_latency_ms: 500,
        regions: ["US", "EU"],
        max_context: orModel.context_length || 128000,
        description: `${orModel.name || orModel.id} via OpenRouter`,
      });
      refresh();
    } catch (err) {
      console.error(err);
    } finally {
      setAddingModel(null);
    }
  };

  if (loading) return <ModelsSkeleton />;

  const enabledCount = models.filter((m) => m.enabled).length;
  const existingIds = new Set(models.map((m) => m.openrouter_id));

  return (
    <div className="space-y-4 animate-in fade-in duration-500">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold tracking-tight">模型注册表</h1>
        <p className="text-xs text-muted-foreground mt-0.5">
          浏览 OpenRouter 目录，并配置驱动路由的模型
        </p>
      </div>

      {/* Split layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 items-start" style={{ minHeight: "calc(100vh - 180px)" }}>

        {/* ═══ LEFT: OpenRouter Catalog ═══ */}
        <div className="flex flex-col border border-border/50 rounded-xl bg-card/30 overflow-hidden" style={{ height: "calc(100vh - 180px)" }}>
          {/* Catalog header */}
          <div className="px-4 py-3 border-b border-border/30 space-y-2 flex-shrink-0">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="h-5 w-5 rounded bg-primary/15 flex items-center justify-center">
                  <svg className="w-3 h-3 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
                  </svg>
                </div>
                <span className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">OpenRouter 目录</span>
              </div>
              {catalogLoaded && (
                <span className="text-[10px] font-mono text-muted-foreground/60">{catalogResults.length} 个模型</span>
              )}
            </div>
            <Input
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="筛选模型...（claude、gpt、llama、gemini）"
              className="bg-secondary/20 border-border/30 h-8 text-xs"
            />
          </div>

          {/* Catalog list */}
          <div className="flex-1 overflow-y-auto">
            {searching && catalogResults.length === 0 ? (
              <div className="flex items-center justify-center h-32">
                <span className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full" />
              </div>
            ) : catalogResults.length === 0 ? (
              <div className="flex items-center justify-center h-32 text-xs text-muted-foreground">
                未找到模型
              </div>
            ) : (
              <div className="divide-y divide-border/20">
                {catalogResults.map((orModel) => {
                  const alreadyAdded = existingIds.has(orModel.id);
                  const tier = selectedTier[orModel.id] || "medium";
                  return (
                    <div
                      key={orModel.id}
                      className={`px-4 py-3 transition-colors ${
                        alreadyAdded ? "bg-green-500/[0.03]" : "hover:bg-secondary/10"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-1.5 flex-wrap">
                            <span className="text-xs font-medium truncate">{orModel.name || orModel.id}</span>
                            <Badge variant="outline" className={`text-[8px] px-1 py-0 ${PROVIDER_COLORS[orModel.provider] || "border-gray-500/30 text-gray-400"}`}>
                              {orModel.provider}
                            </Badge>
                            {alreadyAdded && (
                              <Badge className="bg-green-500/15 text-green-400 border-green-500/30 text-[8px] px-1 py-0">
                                已添加
                              </Badge>
                            )}
                          </div>
                          <div className="flex gap-3 mt-1 text-[9px] font-mono text-muted-foreground/60">
                            <span>${(orModel.cost_per_m_input || 0).toFixed(2)}/M in</span>
                            <span>${(orModel.cost_per_m_output || 0).toFixed(2)}/M out</span>
                            <span>{((orModel.context_length || 0) / 1000).toFixed(0)}K</span>
                          </div>
                        </div>

                        {!alreadyAdded && (
                          <div className="flex items-center gap-1.5 flex-shrink-0">
                            <div className="flex gap-px">
                              {TIER_OPTIONS.map((t) => (
                                <button
                                  key={t}
                                  onClick={() => setSelectedTier((prev) => ({ ...prev, [orModel.id]: t }))}
                                  className={`px-1.5 py-0.5 text-[8px] font-medium transition-colors first:rounded-l last:rounded-r ${
                                    tier === t
                                      ? t === "simple" ? "bg-green-500/25 text-green-400"
                                        : t === "complex" ? "bg-red-500/25 text-red-400"
                                        : "bg-amber-500/25 text-amber-400"
                                      : "bg-secondary/40 text-muted-foreground/50 hover:bg-secondary/60"
                                  }`}
                                >
                                  {t[0].toUpperCase()}
                                </button>
                              ))}
                            </div>
                            <Button
                              size="sm"
                              className="h-6 px-2 text-[9px]"
                              onClick={() => handleAdd(orModel)}
                              disabled={addingModel === orModel.id}
                            >
                              {addingModel === orModel.id ? (
                                <span className="animate-spin h-2.5 w-2.5 border border-primary-foreground border-t-transparent rounded-full" />
                              ) : (
                                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                                </svg>
                              )}
                            </Button>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* ═══ RIGHT: Your Models ═══ */}
        <div className="flex flex-col border border-border/50 rounded-xl bg-card/30 overflow-hidden" style={{ height: "calc(100vh - 180px)" }}>
          {/* Your models header */}
          <div className="px-4 py-3 border-b border-border/30 flex-shrink-0">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="h-5 w-5 rounded bg-green-500/15 flex items-center justify-center">
                  <svg className="w-3 h-3 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                  </svg>
                </div>
                <span className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">我的模型</span>
              </div>
              <span className="text-[10px] font-mono text-muted-foreground/60">
                {enabledCount}/{models.length} 已启用
              </span>
            </div>
          </div>

          {/* Models list */}
          <div className="flex-1 overflow-y-auto">
            {models.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center p-6">
                <div className="h-10 w-10 rounded-xl bg-secondary/30 flex items-center justify-center mb-3">
                  <svg className="w-5 h-5 text-muted-foreground/40" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                  </svg>
                </div>
                <p className="text-xs text-muted-foreground">尚未配置模型</p>
                <p className="text-[10px] text-muted-foreground/50 mt-1">搜索目录并添加模型即可开始</p>
              </div>
            ) : (
              <div className="divide-y divide-border/20">
                {models.map((model) => (
                  <div
                    key={model.model_name}
                    className={`px-4 py-3 transition-all ${
                      model.enabled ? "" : "opacity-40"
                    } ${updating === model.model_name ? "animate-pulse" : ""}`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <span className="text-xs font-semibold">{model.model_name}</span>
                          <Badge variant="outline" className={`text-[8px] px-1 py-0 ${TIER_COLORS[model.tier] || ""}`}>
                            {TIER_LABELS[model.tier] || model.tier}
                          </Badge>
                          <Badge variant="outline" className={`text-[8px] px-1 py-0 ${PROVIDER_COLORS[model.provider] || "border-gray-500/30 text-gray-400"}`}>
                            {model.provider}
                          </Badge>
                        </div>
                        <p className="text-[10px] text-muted-foreground/60 mt-0.5 truncate">{model.description}</p>

                        {/* Specs row */}
                        <div className="flex gap-3 mt-1.5 text-[9px] font-mono text-muted-foreground/50">
                          <span>${model.cost_per_m_input.toFixed(2)}/M in</span>
                          <span>${model.cost_per_m_output.toFixed(2)}/M out</span>
                          <span>{model.avg_latency_ms}ms</span>
                          <span>{(model.max_context / 1000).toFixed(0)}K</span>
                        </div>

                        {/* Regions */}
                        <div className="flex gap-1 mt-1.5">
                          {model.regions.map((r) => (
                            <Badge key={r} variant="outline" className="text-[8px] px-1 py-0">{r}</Badge>
                          ))}
                          <span className="text-[8px] font-mono text-muted-foreground/30 ml-1 truncate">{model.openrouter_id}</span>
                        </div>
                      </div>

                      {/* Controls */}
                      <div className="flex items-center gap-2 flex-shrink-0 pt-0.5">
                        <Switch
                          checked={model.enabled}
                          onCheckedChange={() => handleToggle(model)}
                          disabled={updating === model.model_name}
                        />
                        <button
                          onClick={() => handleRemove(model.model_name)}
                          className="h-6 w-6 rounded flex items-center justify-center text-muted-foreground/30 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                          title="移除模型"
                        >
                          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
