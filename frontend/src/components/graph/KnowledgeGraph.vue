<script setup lang="ts">
import type { Graph, GraphNode, NodeType } from '@/types/graph'
import { NODE_COLORS } from '@/types/graph'
import cytoscape from 'cytoscape'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { ZoomIn, ZoomOut, Maximize2, RefreshCw } from 'lucide-vue-next'
import GraphDetailCard from './GraphDetailCard.vue'

// ─── Props / Emits ─────────────────────────────────────────────────────────────
const props = defineProps<{
  graph: Graph
  isDark?: boolean
}>()

const emit = defineEmits<{
  (e: 'nodeUpdated', node: GraphNode): void
}>()

// ─── Template Ref ──────────────────────────────────────────────────────────────
const containerRef = ref<HTMLDivElement | null>(null)

// Cytoscape 實例不放入 ref（有循環參照，Vue Proxy 會出問題）
let cy: cytoscape.Core | null = null

// ─── 選取狀態 ──────────────────────────────────────────────────────────────────
const selectedNode = ref<GraphNode | null>(null)
let isSelected = false

// ─── 顏色工具 ──────────────────────────────────────────────────────────────────
function getColor(type: string): string {
  return NODE_COLORS[type as NodeType] ?? '#6b7280'
}

// ─── 主題色彩 Token ────────────────────────────────────────────────────────────
// 根據 isDark prop 回傳對應的顏色，讓 Cytoscape 樣式跟隨主題
function themeTokens(dark: boolean) {
  return {
    edgeColor: dark ? '#475569' : '#94a3b8',
    edgeHl: '#f59e0b',
    labelColor: dark ? '#94a3b8' : '#64748b',
    labelBg: dark ? '#0f172a' : '#f8fafc',
    dimOpacity: 0.12,
  }
}

// ─── Stylesheet Builder ────────────────────────────────────────────────────────
function buildStylesheet(dark: boolean): cytoscape.Stylesheet[] {
  const t = themeTokens(dark)
  return [
    // ── 節點 ──────────────────────────────────────────────────────────────
    {
      selector: 'node',
      style: {
        label: 'data(label)',
        'text-valign': 'center',
        'text-halign': 'center',
        'font-size': 11,
        'font-weight': 600,
        color: '#fff',
        'text-outline-color': '#00000055',
        'text-outline-width': 2,
        width: 52,
        height: 52,
        'background-color': 'data(color)',
        'border-width': 2.5,
        'border-color': 'transparent',
        'border-opacity': 0,
        opacity: 1,
        'shadow-blur': 8,
        'shadow-color': '#00000030',
        'shadow-offset-x': 0,
        'shadow-offset-y': 3,
        'shadow-opacity': 1,
        'transition-property': 'opacity, border-color, border-width, border-opacity, width, height',
        'transition-duration': 150,
      } as cytoscape.Css.Node,
    },
    // ── 邊 ────────────────────────────────────────────────────────────────
    {
      selector: 'edge',
      style: {
        label: 'data(type)',
        'font-size': 9,
        color: t.labelColor,
        'text-background-color': t.labelBg,
        'text-background-opacity': 0.85,
        'text-background-padding': '2px',
        'text-background-shape': 'round-rectangle',
        width: 1.5,
        'line-color': t.edgeColor,
        'target-arrow-color': t.edgeColor,
        'target-arrow-shape': 'none',
        'curve-style': 'bezier',
        opacity: 1,
        'transition-property': 'opacity, line-color, target-arrow-color, width',
        'transition-duration': 150,
      } as cytoscape.Css.Edge,
    },
    // ── 有向邊 ────────────────────────────────────────────────────────────
    {
      selector: 'edge[directed="true"]',
      style: { 'target-arrow-shape': 'triangle' },
    },
    // ── Highlight：主節點 ─────────────────────────────────────────────────
    {
      selector: '.hl-main',
      style: {
        'border-color': t.edgeHl,
        'border-width': 3,
        'border-opacity': 1,
        width: 62,
        height: 62,
      } as cytoscape.Css.Node,
    },
    // ── Highlight：鄰居節點 ───────────────────────────────────────────────
    {
      selector: '.hl-neighbor',
      style: {
        'border-color': t.edgeHl,
        'border-width': 2,
        'border-opacity': 0.6,
      } as cytoscape.Css.Node,
    },
    // ── Highlight：相連邊 ─────────────────────────────────────────────────
    {
      selector: '.hl-edge',
      style: {
        'line-color': t.edgeHl,
        'target-arrow-color': t.edgeHl,
        color: t.edgeHl,
        'text-background-color': dark ? '#1e293b' : '#fff',
        width: 2.5,
        opacity: 1,
      } as cytoscape.Css.Edge,
    },
    // ── 暗化（非鄰居） ─────────────────────────────────────────────────────
    {
      selector: '.dim',
      style: { opacity: t.dimOpacity },
    },
    // ── 選取中主節點 ──────────────────────────────────────────────────────
    {
      selector: '.selected',
      style: {
        'border-color': t.edgeHl,
        'border-width': 4,
        'border-opacity': 1,
        width: 66,
        height: 66,
        'shadow-blur': 20,
        'shadow-color': t.edgeHl,
        'shadow-opacity': 0.5,
      } as cytoscape.Css.Node,
    },
  ]
}

// ─── Elements 轉換 ─────────────────────────────────────────────────────────────
function buildElements(graph: Graph): cytoscape.ElementDefinition[] {
  return [
    ...graph.nodes.map((n) => ({
      group: 'nodes' as const,
      data: {
        id: n.id,
        label: n.label,
        type: n.type,
        description: n.description,
        color: getColor(n.type),
      },
    })),
    ...graph.edges.map((e) => ({
      group: 'edges' as const,
      data: {
        id: e.id,
        source: e.source,
        target: e.target,
        type: e.type,
        directed: String(e.directed),
      },
    })),
  ]
}

// ─── Highlight 工具 ────────────────────────────────────────────────────────────
function clearHighlight() {
  cy?.elements().removeClass('hl-main hl-neighbor hl-edge dim selected')
}

function applyHighlight(node: cytoscape.NodeSingular, mode: 'hover' | 'select') {
  if (!cy) return
  cy.batch(() => {
    cy!.elements().addClass('dim')
    const hood = node.closedNeighborhood()
    hood.removeClass('dim')
    node.addClass(mode === 'select' ? 'selected hl-main' : 'hl-main')
    hood.edges().addClass('hl-edge')
    hood.nodes().not(node).addClass('hl-neighbor')
  })
}

// ─── 事件綁定 ──────────────────────────────────────────────────────────────────
function bindEvents() {
  if (!cy) return
  const container = cy.container() as HTMLElement

  cy.on('mouseover', 'node', (evt) => {
    if (isSelected) return
    applyHighlight(evt.target as cytoscape.NodeSingular, 'hover')
    container.style.cursor = 'pointer'
  })

  cy.on('mouseout', 'node', () => {
    if (isSelected) return
    clearHighlight()
    container.style.cursor = 'default'
  })

  cy.on('tap', 'node', (evt) => {
    const node = evt.target as cytoscape.NodeSingular
    // 點擊同一節點 → 取消選取
    if (isSelected && selectedNode.value?.id === node.id()) {
      isSelected = false
      selectedNode.value = null
      clearHighlight()
      return
    }
    isSelected = true
    selectedNode.value = {
      id: node.id(),
      type: node.data('type') as NodeType,
      label: node.data('label'),
      description: node.data('description'),
    }
    clearHighlight()
    applyHighlight(node, 'select')
  })

  // 點背景 → 取消選取
  cy.on('tap', (evt) => {
    if (evt.target !== cy) return
    isSelected = false
    selectedNode.value = null
    clearHighlight()
  })
}

// ─── 初始化 ────────────────────────────────────────────────────────────────────
function initCy() {
  if (!containerRef.value) return
  cy = cytoscape({
    container: containerRef.value,
    elements: buildElements(props.graph),
    style: buildStylesheet(props.isDark ?? false),
    layout: {
      name: 'cose',
      animate: false,
      padding: 60,
      // @ts-expect-error cose 特有參數
      nodeOverlap: 20,
      idealEdgeLength: 140,
      nodeRepulsion: () => 10000,
      gravity: 0.8,
    },
    userZoomingEnabled: true,
    userPanningEnabled: true,
    boxSelectionEnabled: false,
    autoungrabifyNodes: false,
    minZoom: 0.2,
    maxZoom: 3,
  })
  bindEvents()
}

// ─── 監聽 isDark 切換主題 ──────────────────────────────────────────────────────
watch(
  () => props.isDark,
  (dark) => {
    if (!cy) return
    cy.style(buildStylesheet(dark ?? false))
  },
)

// ─── 監聽 graph 資料變化 ───────────────────────────────────────────────────────
watch(
  () => props.graph,
  (newGraph) => {
    if (!cy) return
    cy.elements().remove()
    cy.add(buildElements(newGraph))
    cy.layout({ name: 'cose', animate: true }).run()
    isSelected = false
    selectedNode.value = null
    clearHighlight()
  },
  { deep: true },
)

// ─── 工具列動作 ────────────────────────────────────────────────────────────────
function fitView() {
  cy?.fit(undefined, 50)
}
function zoomIn() {
  if (!cy) return
  cy.zoom({ level: cy.zoom() * 1.25, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } })
}
function zoomOut() {
  if (!cy) return
  cy.zoom({ level: cy.zoom() * 0.8, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } })
}
function resetLayout() {
  cy?.layout({ name: 'cose', animate: true, padding: 60 }).run()
}

// ─── 詳細卡事件 ────────────────────────────────────────────────────────────────
function onNodeUpdate(updated: GraphNode) {
  if (!cy) return
  cy.$id(updated.id).data({
    label: updated.label,
    type: updated.type,
    description: updated.description,
    color: getColor(updated.type),
  })
  selectedNode.value = { ...updated }
  emit('nodeUpdated', updated)
}

function onCardClose() {
  isSelected = false
  selectedNode.value = null
  clearHighlight()
}

// ─── 生命週期 ──────────────────────────────────────────────────────────────────
onMounted(initCy)
onBeforeUnmount(() => {
  cy?.destroy()
  cy = null
})
</script>

<template>
  <div class="relative w-full h-full overflow-hidden rounded-xl border bg-background flex flex-col">

    <!-- 工具列 -->
    <div class="absolute top-3 left-3 z-10 flex flex-col gap-1.5">
      <button
        class="w-8 h-8 rounded-lg bg-card border shadow-sm flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
        title="放大"
        @click="zoomIn"
      >
        <ZoomIn :size="14" />
      </button>
      <button
        class="w-8 h-8 rounded-lg bg-card border shadow-sm flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
        title="縮小"
        @click="zoomOut"
      >
        <ZoomOut :size="14" />
      </button>
      <div class="h-px bg-border mx-1" />
      <button
        class="w-8 h-8 rounded-lg bg-card border shadow-sm flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
        title="全部顯示"
        @click="fitView"
      >
        <Maximize2 :size="14" />
      </button>
      <button
        class="w-8 h-8 rounded-lg bg-card border shadow-sm flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
        title="重新排列"
        @click="resetLayout"
      >
        <RefreshCw :size="14" />
      </button>
    </div>

    <!-- 操作提示 -->
    <div class="absolute bottom-3 left-3 z-10 text-[10px] text-muted-foreground/60 select-none space-y-0.5">
      <div>滾輪縮放・拖曳平移</div>
      <div>點擊節點選取・再次點擊取消</div>
    </div>

    <!-- Cytoscape 畫布 -->
    <div
      ref="containerRef"
      class="w-full h-full"
    />

    <!-- 右側詳細資訊卡 -->
    <GraphDetailCard
      :node="selectedNode"
      @update="onNodeUpdate"
      @close="onCardClose"
    />

  </div>
</template>
