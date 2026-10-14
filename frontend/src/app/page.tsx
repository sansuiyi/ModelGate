"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getGlobalStats, getAllLogs } from "@/lib/api";
import type { GlobalStats, RequestLogEntry } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, AreaChart, Area, CartesianGrid,
} from "recharts";
import { DashboardSkeleton } from "@/components/Skeletons";

const CHART_COLORS = ["#0284c7", "#059669", "#d97706", "#dc2626", "#475569", "#ea580c"];

function StatCard({ label, value, sub, trend, trendValue }: { label: string; value: string; sub?: string; trend?: "up" | "down" | "neutral", trendValue?: string }) {
  return (
    <div className="soft-card p-4 rounded-xl flex flex-col justify-between">
      <div className="text-xs font-medium text-slate-500 mb-2 font-sans tracking-wide">{label}</div>
      <div className="flex items-baseline gap-2">
        <div className="text-2xl font-bold stat-value text-slate-800 font-mono tracking-tight">{value}</div>
        {trendValue && (
          <div className={`text-[10px] font-mono px-1.5 py-0.5 rounded flex items-center gap-0.5 ${trend === "up" ? "text-emerald-700 bg-emerald-100/50" : trend === "down" ? "text-rose-700 bg-rose-100/50" : "text-slate-600 bg-slate-100/50"}`}>
            {trend === "up" ? "↑" : trend === "down" ? "↓" : "−"} {trendValue}
          </div>
        )}
      </div>
      {sub && <div className="text-[11px] text-slate-400 mt-1.5 font-medium">{sub}</div>}
    </div>
  );
}

const TIER_LABELS: Record<string, string> = { simple: "简单", medium: "中等", complex: "复杂" };

function LiveFeed({ logs }: { logs: RequestLogEntry[] }) {
  return (
    <div className="space-y-1">
      {logs.slice(0, 10).map((log) => (
        <div key={log.id} className="group flex items-center gap-3 text-xs py-2 px-2.5 rounded hover:bg-slate-50 border-b border-transparent hover:border-slate-200/50 transition-colors">
          <span className={`h-1.5 w-1.5 rounded-full flex-shrink-0 ${
            log.status === "success" ? "bg-emerald-500 shadow-[0_0_4px_rgba(16,185,129,0.3)]" : "bg-rose-500 shadow-[0_0_4px_rgba(225,29,72,0.3)]"
          }`} />
          <span className="text-slate-400 font-mono w-14 flex-shrink-0">
            {new Date(log.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          </span>
          <Badge variant="outline" className={`text-[9px] px-1.5 py-0 flex-shrink-0 font-medium ${
            log.classification === "simple" ? "border-emerald-200 text-emerald-700 bg-emerald-50/50"
            : log.classification === "complex" ? "border-rose-200 text-rose-700 bg-rose-50/50"
            : "border-amber-200 text-amber-700 bg-amber-50/50"
          }`}>
            {TIER_LABELS[log.classification] || log.classification}
          </Badge>
          <span className="font-mono text-[10px] text-slate-700 w-24 flex-shrink-0 truncate" title={log.selected_model}>{log.selected_model.split('/').pop()}</span>
          <span className="truncate text-slate-500 flex-1 font-sans">{log.prompt_preview}</span>
          <span className="font-mono text-[10px] text-slate-400 w-12 text-right flex-shrink-0 group-hover:text-slate-600">{log.latency_ms}ms</span>
        </div>
      ))}
    </div>
  );
}

export default function DashboardPage() {
  const [stats, setStats] = useState<GlobalStats | null>(null);
  const [logs, setLogs] = useState<RequestLogEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getGlobalStats(), getAllLogs(50)])
      .then(([s, l]) => { setStats(s); setLogs(l); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading || !stats) {
    return <DashboardSkeleton />;
  }

  const modelData = Object.entries(stats.model_distribution).map(([name, value]) => ({ name, value }));
  const providerData = Object.entries(stats.provider_distribution).map(([name, value]) => ({ name, value }));
  const hourlyData = stats.hourly_requests.slice(-24);
  const customerData = Object.entries(stats.customer_request_counts).map(([name, count]) => ({ name, count }));
  const hasData = stats.total_requests > 0;

  return (
    <div className="space-y-5 animate-in fade-in duration-500 pb-12">
      {/* Enterprise Header */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 pb-4 border-b border-slate-200/80">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold tracking-tight text-slate-900">平台概览</h1>
            <Badge variant="outline" className="bg-white text-[10px] border-slate-200 text-slate-500">全局</Badge>
          </div>
          <p className="text-xs text-slate-500 font-medium">监控全平台 AI 路由与推理延迟。</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md bg-white border border-slate-200 shadow-sm text-xs text-slate-600 font-mono font-medium">
            <span className={`h-1.5 w-1.5 rounded-full ${hasData ? "bg-emerald-500 animate-pulse-dot" : "bg-amber-500"}`} />
            {hasData ? "所有系统运行正常" : "等待首个请求"}
          </div>
          <Button variant="outline" size="sm" className="h-7 text-xs bg-white text-slate-600 border-slate-200">
            导出报告
          </Button>
        </div>
      </div>

      {/* Empty state */}
      {!hasData && (
        <div className="soft-card p-12 text-center rounded-xl border border-dashed border-slate-300">
            <div className="mx-auto w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" /></svg>
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-800">
                {stats.total_customers === 0 ? "等待配置" : "未检测到流量"}
              </h2>
              <p className="text-sm text-slate-500 mt-1 max-w-sm mx-auto">
                {stats.total_customers === 0
                  ? "请先配置模型注册表并接入首个客户，即可开始路由流量。"
                  : "客户已配置，但尚未处理任何请求。请通过测试台发送测试提示词。"}
              </p>
            </div>
            <div className="flex justify-center gap-3 mt-5">
              {stats.total_customers === 0 ? (
                <>
                  <Link href="/models">
                    <Button variant="outline" size="sm" className="bg-white border-slate-200 text-slate-700">配置模型</Button>
                  </Link>
                  <Link href="/customers/new">
                    <Button size="sm" className="bg-slate-900 text-white hover:bg-slate-800">接入首个客户</Button>
                  </Link>
                </>
              ) : (
                <Link href="/playground">
                  <Button size="sm" className="bg-slate-900 text-white hover:bg-slate-800">打开测试台</Button>
                </Link>
              )}
            </div>
        </div>
      )}

      {/* Metrics Row */}
      {hasData && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          <StatCard label="总请求数" value={stats.total_requests.toLocaleString()} sub={`今日 ${stats.requests_today}`} trend="up" trendValue="+12%" />
          <StatCard label="活跃客户" value={stats.total_customers.toString()} trend="neutral" trendValue="0" />
          <StatCard label="总花费" value={`$${stats.total_cost.toFixed(4)}`} sub={`今日 $${stats.cost_today.toFixed(4)}`} trend="up" trendValue="1.2%" />
          <StatCard
            label="成本节省"
            value={`$${stats.cost_savings_vs_premium.toFixed(4)}`}
            sub="对比纯旗舰模型基线"
            trend="up"
            trendValue="34%"
          />
          <StatCard label="平均延迟" value={`${stats.avg_latency_ms.toFixed(0)}ms`} trend="down" trendValue="14ms" />
          <StatCard
            label="活跃模型数"
            value={Object.keys(stats.model_distribution).length.toString()}
            sub={`${Object.keys(stats.provider_distribution).length} 个提供商`}
          />
        </div>
      )}

      {/* Main Grid */}
      {hasData && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          
          {/* Timeline */}
          <div className="lg:col-span-8 soft-card rounded-xl p-4 flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-slate-800">请求量</h2>
              <Badge variant="outline" className="text-[10px] bg-slate-50 border-slate-200 text-slate-500 font-mono">24 小时历史</Badge>
            </div>
            <div className="h-[220px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={hourlyData} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="reqGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.15} />
                      <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="hour" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: "#64748b" }} tickFormatter={(v) => v.split(" ")[1] || v} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: "#64748b" }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#ffffff", border: "1px solid #e2e8f0", borderRadius: "8px", fontSize: "11px", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
                    labelStyle={{ color: "#475569", fontWeight: 600, marginBottom: "4px" }}
                  />
                  <Area type="monotone" dataKey="count" stroke="#0ea5e9" fill="url(#reqGradient)" strokeWidth={2} activeDot={{ r: 4, fill: "#0ea5e9", stroke: "#fff", strokeWidth: 2 }} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Model Distribution */}
          <div className="lg:col-span-4 soft-card rounded-xl p-4 flex flex-col">
            <h2 className="text-sm font-semibold text-slate-800 mb-2">模型分布</h2>
            <div className="flex-1 min-h-[160px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={modelData} cx="50%" cy="50%" innerRadius={45} outerRadius={70} dataKey="value" stroke="none" paddingAngle={2}>
                    {modelData.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: "#ffffff", border: "1px solid #e2e8f0", borderRadius: "8px", fontSize: "11px", boxShadow: "0 2px 4px 0 rgb(0 0 0 / 0.05)" }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="space-y-1.5 mt-2">
              {modelData.slice(0, 4).map((d, i) => (
                <div key={d.name} className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2 truncate">
                    <span className="h-2 w-2 rounded-full flex-shrink-0" style={{ backgroundColor: CHART_COLORS[i % CHART_COLORS.length] }} />
                    <span className="text-slate-600 truncate" title={d.name}>{d.name.split('/').pop()}</span>
                  </div>
                  <span className="font-mono text-slate-800 font-medium">{d.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Savings Metric / Provider Breakdown */}
          <div className="lg:col-span-4 soft-card rounded-xl p-4">
            <h2 className="text-sm font-semibold text-slate-800 mb-4">按提供商流量</h2>
            <div className="h-[180px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={providerData} layout="vertical" margin={{ top: 0, right: 10, left: 10, bottom: 0 }}>
                  <XAxis type="number" hide />
                  <YAxis type="category" dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: "#475569" }} width={80} />
                  <Tooltip cursor={{fill: "#f1f5f9"}} contentStyle={{ backgroundColor: "#ffffff", border: "1px solid #e2e8f0", borderRadius: "8px", fontSize: "11px", boxShadow: "0 2px 4px 0 rgb(0 0 0 / 0.05)" }} />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={16}>
                    {providerData.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[(i + 1) % CHART_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Live Request Log */}
          <div className="lg:col-span-8 soft-card rounded-xl p-4 flex flex-col">
            <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-2">
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-semibold text-slate-800">事件流</h2>
                <div className="flex items-center gap-1.5 px-1.5 py-0.5 rounded bg-emerald-50 border border-emerald-100">
                  <span className="h-1 w-1 rounded-full bg-emerald-500 animate-pulse-dot" />
                  <span className="text-[9px] text-emerald-700 font-mono font-medium tracking-wide">实时</span>
                </div>
              </div>
              <Link href="/playground" className="text-xs text-sky-600 hover:text-sky-700 font-medium">查看详细日志 →</Link>
            </div>
            <div className="flex-1 min-h-[200px]">
              <LiveFeed logs={logs} />
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
