export type NodeType = string

export interface GraphNode {
  id: string
  type: NodeType
  label: string
  description: string
  aliases: string[]
  descriptions: string[]
}

export function withGraphNodeLists(
  node: Omit<GraphNode, 'aliases' | 'descriptions'> &
    Partial<Pick<GraphNode, 'aliases' | 'descriptions'>>,
): GraphNode {
  const descriptions =
    node.descriptions && node.descriptions.length > 0
      ? node.descriptions
      : node.description
        ? [node.description]
        : []
  return {
    ...node,
    aliases: node.aliases ?? [],
    descriptions,
  }
}

export interface GraphEdge {
  id: string
  type: string
  source: string
  target: string
  directed: boolean
}

export interface GraphEdgeDetail extends GraphEdge {
  sourceLabel: string
  targetLabel: string
}

export type GraphSelection =
  | { kind: 'node'; data: GraphNode }
  | { kind: 'edge'; data: GraphEdgeDetail }

export interface Graph {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

/** Known types with localized labels. Unknown LLM types fall back to raw text. */
export const NODE_TYPE_LABELS: Record<string, string> = {
  character: '角色',
  location: '地點',
  item: '道具',
  event: '事件',
  organization: '組織',
  concept: '概念',
  CHUNK: '文本區塊',
  LOCATION: '地點',
  CHARACTER: '角色',
  FACTION: '陣營',
  EVENT: '事件',
  ITEM: '物品',
  SAN_CHECK: '理智檢定',
  NPC: 'NPC',
  Location: '地點',
  Item: '道具',
  Event: '事件',
  Entity: '實體',
  Ending: '結局',
}

/** Fixed colors for known types. Unknown types use {@link getNodeTypeColor}. */
export const NODE_COLORS: Record<string, string> = {
  character: '#f97316',
  location: '#3b82f6',
  item: '#a855f7',
  event: '#ef4444',
  organization: '#10b981',
  concept: '#6b7280',
  CHUNK: '#64748b',
  LOCATION: '#3b82f6',
  CHARACTER: '#f97316',
  FACTION: '#10b981',
  EVENT: '#ef4444',
  ITEM: '#a855f7',
  SAN_CHECK: '#ec4899',
  NPC: '#f97316',
  Location: '#3b82f6',
  Item: '#a855f7',
  Event: '#ef4444',
  Entity: '#10b981',
  Ending: '#a855f7',
}

const HASH_COLOR_PALETTE = [
  '#f97316',
  '#3b82f6',
  '#a855f7',
  '#ef4444',
  '#10b981',
  '#ec4899',
  '#14b8a6',
  '#eab308',
  '#8b5cf6',
  '#06b6d4',
  '#84cc16',
  '#f43f5e',
  '#0ea5e9',
  '#d946ef',
  '#22c55e',
  '#fb7185',
] as const

function hashType(type: string): number {
  let hash = 0
  for (let i = 0; i < type.length; i += 1) {
    hash = (hash * 31 + type.charCodeAt(i)) | 0
  }
  return Math.abs(hash)
}

export function normalizeNodeType(type: string): NodeType {
  if (type === 'Chunk') return 'CHUNK'
  return type
}

export function getNodeTypeLabel(type: string): string {
  return NODE_TYPE_LABELS[type] ?? type
}

export function getNodeTypeColor(type: string): string {
  const known = NODE_COLORS[type]
  if (known) return known
  return (
    HASH_COLOR_PALETTE[hashType(type) % HASH_COLOR_PALETTE.length] ?? HASH_COLOR_PALETTE[0]
  )
}
