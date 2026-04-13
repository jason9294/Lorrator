export type NodeType =
  | 'character'
  | 'location'
  | 'item'
  | 'event'
  | 'organization'
  | 'concept'

export interface GraphNode {
  id: string
  type: NodeType
  label: string
  description: string
}

export interface GraphEdge {
  id: string
  type: string
  source: string
  target: string
  directed: boolean
}

export interface Graph {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export const NODE_TYPE_LABELS: Record<NodeType, string> = {
  character: '角色',
  location: '地點',
  item: '道具',
  event: '事件',
  organization: '組織',
  concept: '概念',
}

export const NODE_COLORS: Record<NodeType, string> = {
  character: '#f97316',
  location: '#3b82f6',
  item: '#a855f7',
  event: '#ef4444',
  organization: '#10b981',
  concept: '#6b7280',
}
