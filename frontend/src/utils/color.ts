/**
 * Generate a deterministic HSL color from any string ID.
 * Used as the default avatar background color when no custom avatar is set.
 */
export function colorFromId(id: string): string {
  let hash = 0
  for (let i = 0; i < id.length; i++) hash = (hash * 31 + id.charCodeAt(i)) | 0
  const hue = Math.abs(hash) % 360
  return `hsl(${hue} 75% 48%)`
}
