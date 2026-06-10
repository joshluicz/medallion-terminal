'use client'

import { useEffect, useRef } from 'react'
import {
  type IChartApi,
  type CandlestickData,
  type LineData,
  type Time,
  createChart,
} from 'lightweight-charts'
import {
  computeMA,
  computeRSI,
  generateMockOHLCV,
  type ChartTicker,
} from '@/lib/mockData'
import { colors } from '@/lib/theme'

const chartOptions = {
  layout: {
    background: { color: 'transparent' },
    textColor: colors.dim,
  },
  grid: {
    vertLines: { color: 'rgba(0,212,255,0.06)' },
    horzLines: { color: 'rgba(0,212,255,0.06)' },
  },
  rightPriceScale: { borderColor: colors.border },
  timeScale: { borderColor: colors.border },
  crosshair: {
    vertLine: { color: colors.cyanDim },
    horzLine: { color: colors.cyanDim },
  },
}

type ChartPanelInnerProps = {
  ticker: ChartTicker
}

export function ChartPanelInner({ ticker }: ChartPanelInnerProps) {
  const mainRef = useRef<HTMLDivElement>(null)
  const rsiRef = useRef<HTMLDivElement>(null)
  const mainChartRef = useRef<IChartApi | null>(null)
  const rsiChartRef = useRef<IChartApi | null>(null)

  useEffect(() => {
    if (!mainRef.current || !rsiRef.current) return

    const seed = ticker.charCodeAt(0) + ticker.length
    const ohlcv = generateMockOHLCV(seed)
    const ma50 = computeMA(ohlcv, 50)
    const ma200 = computeMA(ohlcv, 200)
    const rsi = computeRSI(ohlcv, 14)

    const mainChart = createChart(mainRef.current, {
      ...chartOptions,
      width: mainRef.current.clientWidth,
      height: 280,
    })

    const rsiChart = createChart(rsiRef.current, {
      ...chartOptions,
      width: rsiRef.current.clientWidth,
      height: 72,
    })

    const candles = mainChart.addCandlestickSeries({
      upColor: colors.positive,
      downColor: colors.negative,
      borderUpColor: colors.positive,
      borderDownColor: colors.negative,
      wickUpColor: colors.positive,
      wickDownColor: colors.negative,
    })

    const line50 = mainChart.addLineSeries({
      color: colors.gold,
      lineWidth: 1,
      title: '50MA',
    })

    const line200 = mainChart.addLineSeries({
      color: colors.violet,
      lineWidth: 1,
      title: '200MA',
    })

    const rsiLine = rsiChart.addLineSeries({
      color: colors.cyan,
      lineWidth: 1,
    })

    const rsiUpper = rsiChart.addLineSeries({
      color: colors.muted,
      lineWidth: 1,
      lineStyle: 2,
    })

    const candleData: CandlestickData<Time>[] = ohlcv.map((b) => ({
      time: b.time as Time,
      open: b.open,
      high: b.high,
      low: b.low,
      close: b.close,
    }))

    candles.setData(candleData)

    const toLine = (values: (number | null)[]): LineData<Time>[] =>
      ohlcv
        .map((b, i) =>
          values[i] != null ? { time: b.time as Time, value: values[i]! } : null,
        )
        .filter((x): x is LineData<Time> => x !== null)

    const ma50Data = toLine(ma50)
    const ma200Data = toLine(ma200)
    const rsiData = toLine(rsi)

    line50.setData(ma50Data)
    line200.setData(ma200Data)

    rsiLine.setData(rsiData)
    rsiUpper.setData(ohlcv.map((b) => ({ time: b.time as Time, value: 70 })))

    mainChart.timeScale().fitContent()
    rsiChart.timeScale().fitContent()

    mainChartRef.current = mainChart
    rsiChartRef.current = rsiChart

    const onResize = () => {
      if (mainRef.current && mainChartRef.current) {
        mainChartRef.current.applyOptions({ width: mainRef.current.clientWidth })
      }
      if (rsiRef.current && rsiChartRef.current) {
        rsiChartRef.current.applyOptions({ width: rsiRef.current.clientWidth })
      }
    }

    window.addEventListener('resize', onResize)

    return () => {
      window.removeEventListener('resize', onResize)
      mainChart.remove()
      rsiChart.remove()
      mainChartRef.current = null
      rsiChartRef.current = null
    }
  }, [ticker])

  return (
    <div className="w-full">
      <div ref={mainRef} className="w-full" />
      <p className="mb-1 mt-1 text-xxs uppercase tracking-widest" style={{ color: colors.dim }}>
        RSI (14)
      </p>
      <div ref={rsiRef} className="w-full" />
    </div>
  )
}
