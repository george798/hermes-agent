import { describe, expect, it } from 'vitest'

import { shimmerSegments } from '../components/loaders.js'

describe('shimmerSegments', () => {
  it('always partitions the full width', () => {
    for (let phase = -40; phase < 80; phase++) {
      const [pre, band, post] = shimmerSegments(20, phase)

      expect(pre + band + post).toBe(20)
      expect(Math.min(pre, band, post)).toBeGreaterThanOrEqual(0)
    }
  })

  it('sweeps: enters from the left edge, exits off the right, then wraps', () => {
    const bandAt = (phase: number) => shimmerSegments(10, phase, 4)

    expect(bandAt(0)).toEqual([10, 0, 0]) // band fully off-left
    expect(bandAt(1)).toEqual([0, 1, 9]) // entering
    expect(bandAt(7)).toEqual([3, 4, 3]) // mid-sweep
    expect(bandAt(13)).toEqual([9, 1, 0]) // exiting
    expect(bandAt(14)).toEqual([10, 0, 0]) // gone → next cycle re-enters
    expect(bandAt(15)).toEqual([0, 1, 9])
  })

  it('negative phases (row stagger) wrap instead of vanishing', () => {
    const [pre, band, post] = shimmerSegments(10, -3, 4)

    expect(pre + band + post).toBe(10)
  })
})
