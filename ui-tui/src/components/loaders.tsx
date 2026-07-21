import { Box, Text } from '@hermes/ink'
import { useEffect, useState } from 'react'

/**
 * Animated ASCII loaders — THE loading-state primitives (session panel
 * skeleton, widget apps via the SDK). A highlight band sweeps across block
 * runs; rows offset their phase for a diagonal shimmer. One interval per
 * composition (the parent ticks, rows are pure), colors are caller-owned
 * theme tones — never hardcoded.
 */

const BAND = 7

/** Pure band math: [pre, band, post] cell widths for a sweep at `phase`.
 *  The band enters from off-left and exits off-right, wrapping. */
export function shimmerSegments(width: number, phase: number, band = BAND): [number, number, number] {
  const cycle = width + band
  const start = (((phase % cycle) + cycle) % cycle) - band
  const from = Math.max(0, start)
  const to = Math.min(width, start + band)

  return to <= from ? [width, 0, 0] : [from, to - from, width - to]
}

/** One shimmering run. Controlled: the parent owns `phase` so sibling rows
 *  stay in lockstep (offset it per row for the diagonal). */
export function Shimmer({
  char = '▁',
  color,
  highlight,
  phase,
  width
}: {
  char?: string
  color: string
  highlight: string
  phase: number
  width: number
}) {
  const [pre, band, post] = shimmerSegments(width, phase)

  return (
    <Text>
      {pre > 0 && <Text color={color}>{char.repeat(pre)}</Text>}
      {band > 0 && <Text color={highlight}>{char.repeat(band)}</Text>}
      {post > 0 && <Text color={color}>{char.repeat(post)}</Text>}
    </Text>
  )
}

/** Self-ticking phase for shimmer compositions. */
export function useShimmerPhase(tickMs = 90): number {
  const [phase, setPhase] = useState(0)

  useEffect(() => {
    const id = setInterval(() => setPhase(p => p + 1), tickMs)

    id.unref?.()

    return () => clearInterval(id)
  }, [tickMs])

  return phase
}

/** Skeleton rows shaped like `label: value` content, diagonal shimmer.
 *  `rows` = [labelWidth, valueWidth][] so callers mirror their real layout. */
export function ShimmerRows({
  color,
  highlight,
  rows
}: {
  color: string
  highlight: string
  rows: readonly (readonly [number, number])[]
}) {
  const phase = useShimmerPhase()

  return (
    <Box flexDirection="column">
      {rows.map(([labelWidth, valueWidth], i) => (
        <Text key={i}>
          <Shimmer color={color} highlight={highlight} phase={phase - i * 2} width={labelWidth} />
          <Text> </Text>
          <Shimmer color={color} highlight={highlight} phase={phase - i * 2 - labelWidth} width={valueWidth} />
        </Text>
      ))}
    </Box>
  )
}
