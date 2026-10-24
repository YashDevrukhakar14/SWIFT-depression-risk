import React from 'react'

/**
 * Diverging horizontal bar chart matching the publication Figure 9 & 10 design.
 * Features center zero-line, left/right horizontal bars with values,
 * customizable domain, axis ticks, and legend.
 */
export default function DivergingBarChart({
  data = [],
  minDomain = -0.6,
  maxDomain = 0.6,
  ticks = [-0.6, -0.3, 0, 0.3, 0.6],
  axisLabel = 'SHAP value (impact on model output)',
  legend = {
    positive: 'Higher risk association',
    negative: 'Lower risk association',
  },
}) {
  const range = maxDomain - minDomain
  const zeroPct = ((0 - minDomain) / range) * 100

  return (
    <div className="diverging-chart">
      <div className="chart-bars-container">
        {data.map((item, idx) => {
          const val = item.value
          const isPos = val >= 0
          const barWidthPct = (Math.abs(val) / range) * 100
          const barLeftPct = isPos ? zeroPct : zeroPct - barWidthPct
          const colorClass = isPos ? 'bar-positive' : 'bar-negative'

          return (
            <div key={idx} className="chart-row">
              <div className="chart-label" title={item.label}>
                {item.label}
              </div>
              <div className="chart-track">
                {/* Zero line */}
                <div
                  className="chart-zero-line"
                  style={{ left: `${zeroPct}%` }}
                />

                {/* The bar */}
                <div
                  className={`chart-bar ${colorClass}`}
                  style={{
                    left: `${barLeftPct}%`,
                    width: `${barWidthPct}%`,
                  }}
                />

                {/* The value text */}
                <div
                  className={`chart-val-text ${isPos ? 'val-right' : 'val-left'}`}
                  style={{
                    left: isPos
                      ? `calc(${zeroPct + barWidthPct}% + 6px)`
                      : `auto`,
                    right: !isPos
                      ? `calc(${100 - zeroPct + barWidthPct}% + 6px)`
                      : `auto`,
                  }}
                >
                  {isPos ? `+${val.toFixed(3)}` : val.toFixed(3)}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Ticks and Axis */}
      <div className="chart-axis-wrapper">
        <div className="chart-axis-labels">
          {ticks.map((t, i) => {
            const pct = ((t - minDomain) / range) * 100
            return (
              <span
                key={i}
                className="axis-tick-label"
                style={{
                  left: `${pct}%`,
                  transform:
                    i === 0
                      ? 'translateX(0)'
                      : i === ticks.length - 1
                      ? 'translateX(-100%)'
                      : 'translateX(-50%)',
                }}
              >
                {t}
              </span>
            )
          })}
        </div>
        <div className="chart-axis-title">{axisLabel}</div>
      </div>

      {/* Legend */}
      <div className="chart-legend-row">
        <div className="legend-item">
          <span className="legend-box red-box" />
          <span>{legend.positive}</span>
        </div>
        <div className="legend-item">
          <span className="legend-box blue-box" />
          <span>{legend.negative}</span>
        </div>
      </div>
    </div>
  )
}
