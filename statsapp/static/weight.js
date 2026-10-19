// Weight chart: weigh-ins and their moving average, with runs, weekly steps and
// yoga sessions on their own hidden axes. Series colours come from the CSS tokens.

document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.getElementById("weight-chart");
    if (!canvas) return;

    const data = JSON.parse(document.getElementById("chart-data").textContent);
    const css = getComputedStyle(document.documentElement);
    const token = name => css.getPropertyValue(name).trim();

    const textMuted = token("--text-muted");
    // axis titles crowd the tick labels on phones; the page heading says what's plotted
    const narrow = window.matchMedia("(max-width: 560px)").matches;
    const gridColour = token("--border");

    Chart.defaults.color = textMuted;
    Chart.defaults.font.family = token("--font");
    Chart.defaults.borderColor = gridColour;

    const toPoints = series => series.map(point => ({x: point.x, y: point.y}));
    const longestRun = Math.max(0, ...data.runs.map(point => point.y));

    // display: false axes skip layout and end up offset from the chart area,
    // so these are laid out like normal axes but draw nothing
    const invisibleAxis = {
        position: "right",
        ticks: {display: false},
        grid: {display: false},
        border: {display: false},
        afterFit: scale => { scale.width = 0; },
    };

    const chart = new Chart(canvas, {
        data: {
            datasets: [
                {
                    type: "line",
                    label: "7-reading average",
                    data: toPoints(data.weight_average),
                    yAxisID: "weight",
                    borderColor: token("--series-average"),
                    backgroundColor: token("--series-average"),
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.3,
                    order: 0,
                },
                {
                    type: "scatter",
                    label: "Weigh-ins",
                    data: toPoints(data.weight),
                    yAxisID: "weight",
                    backgroundColor: token("--series-weight") + "99",
                    pointRadius: 2,
                    pointHoverRadius: 4,
                    order: 1,
                },
                {
                    type: "bar",
                    label: "Runs (m)",
                    data: toPoints(data.runs),
                    yAxisID: "runs",
                    backgroundColor: token("--series-runs") + "88",
                    barThickness: 2,
                    order: 2,
                },
                {
                    type: "line",
                    label: "Steps / week",
                    data: toPoints(data.steps).sort((a, b) => a.x.localeCompare(b.x)),
                    yAxisID: "steps",
                    borderColor: token("--series-steps"),
                    backgroundColor: token("--series-steps"),
                    borderWidth: 1.5,
                    pointRadius: 0,
                    hidden: true,
                    order: 3,
                },
                {
                    type: "bar",
                    label: "Yoga",
                    data: toPoints(data.yoga),
                    yAxisID: "yoga",
                    backgroundColor: token("--series-yoga") + "55",
                    barThickness: 2,
                    hidden: true,
                    order: 4,
                },
            ],
        },
        options: {
            maintainAspectRatio: false,
            interaction: {mode: "nearest", intersect: false},
            plugins: {
                legend: {
                    position: "top",
                    align: "start",
                    labels: {usePointStyle: true, boxWidth: 8, boxHeight: 8, padding: 16},
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const y = context.parsed.y;
                            switch (context.dataset.yAxisID) {
                                case "weight": return `${context.dataset.label}: ${y.toFixed(1)} lbs`;
                                case "runs": return `Run: ${(y / 1609).toFixed(2)} miles`;
                                case "steps": return `Steps that week: ${Math.round(y).toLocaleString()}`;
                                default: return "Yoga session";
                            }
                        },
                    },
                },
            },
            scales: {
                x: {
                    type: "time",
                    time: {tooltipFormat: "d MMM yyyy"},
                    grid: {display: false},
                    ticks: {maxRotation: 0, autoSkipPadding: 24},
                },
                weight: {
                    position: "left",
                    title: {display: !narrow, text: "Weight (lbs)"},
                    grid: {color: gridColour},
                },
                steps: {
                    position: "right",
                    display: "auto",
                    title: {display: !narrow, text: "Steps / week"},
                    grid: {display: false},
                },
                // keep run bars in the bottom ~40% so they don't cover the weight line
                runs: {...invisibleAxis, min: 0, max: longestRun * 2.5 || undefined},
                yoga: {...invisibleAxis, min: 0, max: 1},
            },
        },
    });

    // date range buttons
    const buttons = document.querySelectorAll("[data-range-years]");
    buttons.forEach(button => button.addEventListener("click", function () {
        const years = Number(button.dataset.rangeYears);
        if (years) {
            const min = new Date();
            min.setFullYear(min.getFullYear() - years);
            chart.options.scales.x.min = min.getTime();
        } else {
            delete chart.options.scales.x.min;
        }
        buttons.forEach(b => b.setAttribute("aria-pressed", String(b === button)));
        chart.update();
    }));
});
