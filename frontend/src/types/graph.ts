export type NodeType =
  | 'character'
  | 'location'
  | 'item'
  | 'event'
  | 'organization'
  | 'concept'
  | 'NPC'
  | 'Location'
  | 'Item'
  | 'Event'
  | 'Entity'
  | 'Ending'
  | 'UNKNOWN'

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

export const NODE_TYPE_LABELS: Record<NodeType, string> = {
  character: '角色',
  location: '地點',
  item: '道具',
  event: '事件',
  organization: '組織',
  concept: '概念',
  NPC: 'NPC',
  Location: '地點',
  Item: '道具',
  Event: '事件',
  Entity: '實體',
  Ending: '結局',
  UNKNOWN: '未知',
}

export const NODE_COLORS: Record<NodeType, string> = {
  character: '#f97316',
  location: '#3b82f6',
  item: '#a855f7',
  event: '#ef4444',
  organization: '#10b981',
  concept: '#6b7280',
  NPC: '#f97316',
  Location: '#3b82f6',
  Item: '#a855f7',
  Event: '#ef4444',
  Entity: '#10b981',
  Ending: '#a855f7',
  UNKNOWN: '#6b7280',
}
