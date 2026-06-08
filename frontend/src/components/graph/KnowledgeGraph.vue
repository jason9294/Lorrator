<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import cytoscape from 'cytoscape'
import fcose from 'cytoscape-fcose'

import type { Graph, GraphEdgeDetail, GraphNode, GraphSelection, NodeType } from '@/types/graph'
import { NODE_COLORS } from '@/types/graph'

// Icons
import { ZoomIn, ZoomOut, Maximize2, RefreshCw } from 'lucide-vue-next'

// Components
import GraphDetailCard from './GraphDetailCard.vue'

// Low-level components
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

cytoscape.use(fcose)

// Props / Emits
const props = defineProps<{
  graph: Graph
  isDark?: boolean
  hiddenTypes?: NodeType[]
  highlightType?: NodeType | null
}>()

const emit = defineEmits<{
  (e: 'nodeUpdated', node: GraphNode): void
}>()

// Template Ref
const containerRef = ref<HTMLDivElement | null>(null)

// Cytoscape 實例不放入 ref（有循環參照，Vue Proxy 會出問題）
let cy: cytoscape.Core | null = null

// ─── 選取狀態 ──────────────────────────────────────────────────────────────────
const selection = ref<GraphSelection | null>(null)
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
    typeHl: '#0ea5e9',
    labelColor: dark ? '#94a3b8' : '#64748b',
    labelBg: dark ? '#0f172a' : '#f8fafc',
    dimOpacity: 0.12,
    typeDimOpacity: 0.18,
  }
}

// ─── Stylesheet Builder ────────────────────────────────────────────────────────
function buildStylesheet(dark: boolean) {
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
        'text-background-shape': 'roundrectangle' as cytoscape.Css.PropertyValue<
          cytoscape.EdgeSingular,
          'circle' | 'rectangle' | 'roundrectangle'
        >,
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
      style: {
        'target-arrow-shape':
          'triangle' as cytoscape.Css.PropertyValueEdge<cytoscape.Css.ArrowShape>,
      },
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
    // ── 選取中的邊 ────────────────────────────────────────────────────────
    {
      selector: '.selected-edge',
      style: {
        'line-color': t.edgeHl,
        'target-arrow-color': t.edgeHl,
        color: t.edgeHl,
        'text-background-color': dark ? '#1e293b' : '#fff',
        width: 4,
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
    // ── 類型篩選：符合類型的節點 ─────────────────────────────────────────
    {
      selector: '.type-match',
      style: {
        'border-color': t.typeHl,
        'border-width': 3,
        'border-opacity': 1,
        width: 58,
        height: 58,
        'shadow-blur': 12,
        'shadow-color': `${t.typeHl}80`,
        'shadow-opacity': 0.55,
      } as cytoscape.Css.Node,
    },
    // ── 類型篩選：非符合類型的節點 ─────────────────────────────────────────
    {
      selector: '.type-dim',
      style: { opacity: t.typeDimOpacity },
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
function clearSelectionHighlight() {
  cy?.elements().removeClass('hl-main hl-neighbor hl-edge dim selected selected-edge')
}

function nodeLabel(id: string): string {
  return props.graph.nodes.find((n) => n.id === id)?.label ?? id
}

function buildEdgeDetail(edge: cytoscape.EdgeSingular): GraphEdgeDetail {
  const source = edge.data('source') as string
  const target = edge.data('target') as string
  return {
    id: edge.id(),
    type: edge.data('type') as string,
    source,
    target,
    directed: edge.data('directed') === 'true',
    sourceLabel: nodeLabel(source),
    targetLabel: nodeLabel(target),
  }
}

function clearTypeHighlight() {
  cy?.nodes().removeClass('type-match type-dim')
}

function applyTypeHighlight(type: NodeType | null | undefined) {
  if (!cy || !type) {
    clearTypeHighlight()
    return
  }
  cy.batch(() => {
    clearTypeHighlight()
    cy!.nodes().forEach((node) => {
      if (node.data('type') === type) {
        node.addClass('type-match')
      } else {
        node.addClass('type-dim')
      }
    })
  })
}

function restoreTypeFilterIfActive() {
  if (props.highlightType) applyTypeHighlight(props.highlightType)
}

function clearHighlight() {
  clearSelectionHighlight()
  restoreTypeFilterIfActive()
}

function applyHighlight(node: cytoscape.NodeSingular, mode: 'hover' | 'select') {
  if (!cy) return
  clearTypeHighlight()
  cy.batch(() => {
    cy!.elements().addClass('dim')
    const hood = node.closedNeighborhood()
    hood.removeClass('dim')
    node.addClass(mode === 'select' ? 'selected hl-main' : 'hl-main')
    hood.edges().addClass('hl-edge')
    hood.nodes().not(node).addClass('hl-neighbor')
  })
}

function applyEdgeHighlight(edge: cytoscape.EdgeSingular, mode: 'hover' | 'select') {
  if (!cy) return
  clearTypeHighlight()
  cy.batch(() => {
    cy!.elements().addClass('dim')
    const endpoints = edge.connectedNodes()
    edge.removeClass('dim')
    endpoints.removeClass('dim')
    edge.addClass(mode === 'select' ? 'selected-edge hl-edge' : 'hl-edge')
    endpoints.addClass('hl-neighbor')
  })
}

function isNodeInteractive(node: cytoscape.NodeSingular): boolean {
  if (!props.highlightType) return true
  return node.data('type') === props.highlightType
}

// ─── 事件綁定 ──────────────────────────────────────────────────────────────────
function bindEvents() {
  if (!cy) return
  const container = cy.container() as HTMLElement

  cy.on('mouseover', 'node', (evt) => {
    if (isSelected) return
    const node = evt.target as cytoscape.NodeSingular
    if (!isNodeInteractive(node)) return
    applyHighlight(node, 'hover')
    container.style.cursor = 'pointer'
  })

  cy.on('mouseout', 'node', (evt) => {
    if (isSelected) return
    const node = evt.target as cytoscape.NodeSingular
    if (!isNodeInteractive(node)) return
    clearSelectionHighlight()
    restoreTypeFilterIfActive()
    container.style.cursor = 'default'
  })

  cy.on('mouseover', 'edge', () => {
    if (isSelected) return
    container.style.cursor = 'pointer'
  })

  cy.on('mouseout', 'edge', () => {
    if (isSelected) return
    container.style.cursor = 'default'
  })

  cy.on('tap', 'node', (evt) => {
    const node = evt.target as cytoscape.NodeSingular
    if (isSelected && selection.value?.kind === 'node' && selection.value.data.id === node.id()) {
      isSelected = false
      selection.value = null
      clearHighlight()
      return
    }
    isSelected = true
    selection.value = {
      kind: 'node',
      data: {
        id: node.id(),
        type: node.data('type') as NodeType,
        label: node.data('label'),
        description: node.data('description'),
      },
    }
    clearHighlight()
    applyHighlight(node, 'select')
  })

  cy.on('tap', 'edge', (evt) => {
    const edge = evt.target as cytoscape.EdgeSingular
    if (isSelected && selection.value?.kind === 'edge' && selection.value.data.id === edge.id()) {
      isSelected = false
      selection.value = null
      clearHighlight()
      return
    }
    isSelected = true
    selection.value = { kind: 'edge', data: buildEdgeDetail(edge) }
    clearHighlight()
    applyEdgeHighlight(edge, 'select')
  })

  // 點背景 → 取消選取
  cy.on('tap', (evt) => {
    if (evt.target !== cy) return
    isSelected = false
    selection.value = null
    clearHighlight()
  })
}

// ─── fcose 佈局設定 ────────────────────────────────────────────────────────────
const fcoseLayout = {
  name: 'fcose',
  quality: 'proof',
  randomize: true,
  animate: true,
  animationDuration: 500,
  padding: 80,
  nodeDimensionsIncludeLabels: true,
  uniformNodeDimensions: false,
  packComponents: true,
  nodeRepulsion: 12000,
  idealEdgeLength: 120,
  edgeElasticity: 0.45,
  nestingFactor: 0.1,
  numIter: 2500,
  piTol: 0.0000001,
} as cytoscape.LayoutOptions

// ─── 初始化 ────────────────────────────────────────────────────────────────────
function initCy() {
  if (!containerRef.value) return
  cy = cytoscape({
    container: containerRef.value,
    elements: buildElements(props.graph),
    style: buildStylesheet(props.isDark ?? false),
    layout: { ...fcoseLayout, animate: false } as cytoscape.LayoutOptions,
    userZoomingEnabled: true,
    userPanningEnabled: true,
    boxSelectionEnabled: false,
    autoungrabify: false,
    minZoom: 0.2,
    maxZoom: 3,
  })
  bindEvents()
  if (props.hiddenTypes?.length) applyTypeFilter(props.hiddenTypes)
  if (props.highlightType) applyTypeHighlight(props.highlightType)
}

// ─── 節點類型篩選 ─────────────────────────────────────────────────────────────
function applyTypeFilter(hiddenTypes: NodeType[]) {
  if (!cy) return
  cy.batch(() => {
    cy!.nodes().forEach((node) => {
      if (hiddenTypes.includes(node.data('type') as NodeType)) {
        node.style('display', 'none')
      } else {
        node.style('display', 'element')
      }
    })
    cy!.edges().forEach((edge) => {
      const srcHidden = cy!.$id(edge.data('source')).style('display') === 'none'
      const tgtHidden = cy!.$id(edge.data('target')).style('display') === 'none'
      edge.style('display', srcHidden || tgtHidden ? 'none' : 'element')
    })
  })
}

// ─── 從外部聚焦節點（Command 搜尋用）─────────────────────────────────────────
function focusNode(id: string) {
  if (!cy) return
  const node = cy.$id(id) as cytoscape.NodeSingular
  if (!node || node.empty()) return
  isSelected = true
  selection.value = {
    kind: 'node',
    data: {
      id: node.id(),
      type: node.data('type') as NodeType,
      label: node.data('label'),
      description: node.data('description'),
    },
  }
  clearHighlight()
  applyHighlight(node, 'select')
  cy.animate({
    center: { eles: node },
    zoom: Math.max(cy.zoom(), 1.2),
    duration: 350,
    easing: 'ease-in-out-cubic',
  })
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
    cy.layout(fcoseLayout).run()
    isSelected = false
    selection.value = null
    clearSelectionHighlight()
    applyTypeHighlight(props.highlightType)
  },
  { deep: true },
)

// ─── 監聽隱藏類型變化 ─────────────────────────────────────────────────────────
watch(
  () => props.hiddenTypes,
  (types) => applyTypeFilter(types ?? []),
  { deep: true },
)

// ─── 監聽類型高亮篩選 ─────────────────────────────────────────────────────────
watch(
  () => props.highlightType,
  (type) => {
    if (isSelected) return
    applyTypeHighlight(type)
  },
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
  cy?.layout(fcoseLayout).run()
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
  if (selection.value?.kind === 'node' && selection.value.data.id === updated.id) {
    selection.value = { kind: 'node', data: { ...updated } }
  }
  emit('nodeUpdated', updated)
}

function onCardClose() {
  isSelected = false
  selection.value = null
  clearHighlight()
}

// ─── 生命週期 ──────────────────────────────────────────────────────────────────
onMounted(initCy)
onBeforeUnmount(() => {
  cy?.destroy()
  cy = null
})

defineExpose({ focusNode })
</script>

<template>
  <div class="relative w-full h-full overflow-hidden rounded-xl border bg-background flex flex-col">
    <!-- 工具列 -->
    <TooltipProvider :delay-duration="400">
      <div class="absolute top-3 left-3 z-10 flex flex-col gap-1.5">
        <Tooltip>
          <TooltipTrigger as-child>
            <Button variant="outline" size="icon-sm" @click="zoomIn">
              <ZoomIn class="size-3.5" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="right">放大</TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger as-child>
            <Button variant="outline" size="icon-sm" @click="zoomOut">
              <ZoomOut class="size-3.5" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="right">縮小</TooltipContent>
        </Tooltip>

        <Separator class="my-0.5" />

        <Tooltip>
          <TooltipTrigger as-child>
            <Button variant="outline" size="icon-sm" @click="fitView">
              <Maximize2 class="size-3.5" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="right">全部顯示</TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger as-child>
            <Button variant="outline" size="icon-sm" @click="resetLayout">
              <RefreshCw class="size-3.5" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="right">重新排列</TooltipContent>
        </Tooltip>
      </div>
    </TooltipProvider>

    <!-- 操作提示 -->
    <div
      class="absolute bottom-3 left-3 z-10 text-[10px] text-muted-foreground/60 select-none space-y-0.5"
    >
      <div>滾輪縮放・拖曳平移</div>
      <div>點擊節點或關係選取・再次點擊取消</div>
    </div>

    <!-- Cytoscape 畫布 -->
    <div ref="containerRef" class="w-full h-full" />

    <!-- 右側詳細資訊卡 -->
    <GraphDetailCard :selection="selection" @update="onNodeUpdate" @close="onCardClose" />
  </div>
</template>
